"""
Table-Aware RAG Ingestion Pipeline
====================================
This module provides document ingestion capabilities that intelligently separate
narrative text from structured tables for hybrid storage in a RAG system.

Architecture:
- Narrative text -> Vector database (for semantic search)
- Structured tables -> NoSQL database (for exact lookups)

Migration Path: Local (Qdrant/MongoDB) -> Microsoft Fabric (Real-Time Intelligence/Cosmos DB)
"""

import os
from typing import List, Tuple, Dict, Any
from pathlib import Path

from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Table, NarrativeText, Title, Text, ListItem


class DocumentProcessor:
    """
    Processes PDF documents to extract tables and narrative text separately.

    This class is designed to be modular and easily migratable to Microsoft Fabric.
    Database connectors will be abstracted in separate modules (db_connector.py).
    """

    def __init__(self):
        """Initialize the document processor."""
        self.supported_text_types = (NarrativeText, Title, Text, ListItem)
        # Track table locations to filter out duplicate table text
        self.table_locations = []

    def process_pdf(
        self,
        file_path: str,
        strategy: str = "auto",
        extract_tables_as: str = "html"
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Process a PDF file and separate tables from narrative text.

        Args:
            file_path: Path to the PDF file to process
            strategy: Parsing strategy - 'auto' (recommended), 'fast', or 'hi_res'
                     - 'auto': Smart detection, works without layoutparser
                     - 'fast': Faster processing, good table detection
                     - 'hi_res': Best accuracy but requires layoutparser (often fails)
            extract_tables_as: Format for table extraction ('html' or 'text')

        Returns:
            Tuple containing:
            - tables_to_store: List of dictionaries with table metadata and content
            - text_to_embed: List of text strings for vector embedding

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the file is not a PDF
        """
        # Validate input file
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        if file_path.suffix.lower() != '.pdf':
            raise ValueError(f"File must be a PDF. Got: {file_path.suffix}")

        print(f"Processing PDF: {file_path.name}")
        print(f"Using strategy: {strategy}")
        print("-" * 60)

        # Process the PDF with unstructured.io
        # hi_res strategy uses computer vision for better table detection
        try:
            elements = partition_pdf(
                filename=str(file_path),
                strategy=strategy,
                infer_table_structure=True,  # Enable table structure inference
                extract_images_in_pdf=False,  # Focus on text and tables only
                include_page_breaks=False,
            )
        except (ImportError, ModuleNotFoundError) as e:
            if strategy == "hi_res":
                print(f"\n⚠️  Warning: {e}")
                print("⚠️  hi_res strategy requires layoutparser and PyTorch")
                print("⚠️  Falling back to 'fast' strategy...")
                print("⚠️  For full table detection, install: pip install -r requirements.txt\n")

                # Retry with fast strategy
                elements = partition_pdf(
                    filename=str(file_path),
                    strategy="fast",
                    infer_table_structure=True,
                    extract_images_in_pdf=False,
                    include_page_breaks=False,
                )
            else:
                raise

        # Initialize storage lists
        tables_to_store = []
        text_to_embed = []
        self.table_locations = []  # Reset for each PDF

        # First pass: identify and extract all tables
        for idx, element in enumerate(elements):
            if isinstance(element, Table):
                # Extract table as structured data
                table_data = self._extract_table(element, idx, extract_tables_as)
                tables_to_store.append(table_data)

                # Track table location (page number and approximate position)
                metadata = element.metadata.to_dict() if hasattr(element, 'metadata') else {}
                self.table_locations.append({
                    'page': metadata.get('page_number'),
                    'index': idx
                })

        # Second pass: extract text while filtering out table-like content
        for idx, element in enumerate(elements):
            if isinstance(element, self.supported_text_types):
                # Extract narrative text for embedding
                text_content = element.text.strip()
                if text_content and not self._is_table_like_text(text_content, element):
                    text_to_embed.append(text_content)

        # Print summary
        self._print_summary(file_path.name, tables_to_store, text_to_embed)

        return tables_to_store, text_to_embed

    def _extract_table(
        self,
        table_element: Table,
        index: int,
        extract_as: str = "html"
    ) -> Dict[str, Any]:
        """
        Extract table data with metadata for storage in NoSQL database.

        Args:
            table_element: The Table element from unstructured
            index: Index of the table in the document
            extract_as: Format for extraction ('html' or 'text')

        Returns:
            Dictionary containing table metadata and content
        """
        # Extract table metadata
        metadata = table_element.metadata.to_dict() if hasattr(table_element, 'metadata') else {}

        # Get table content in requested format
        if extract_as == "html" and hasattr(table_element.metadata, 'text_as_html'):
            table_content = table_element.metadata.text_as_html
            content_type = "html"
        else:
            table_content = table_element.text
            content_type = "text"

        # Build structured table record
        table_record = {
            "table_id": f"table_{index}",
            "content": table_content,
            "content_type": content_type,
            "metadata": {
                "page_number": metadata.get("page_number"),
                "filename": metadata.get("filename"),
                "file_directory": metadata.get("file_directory"),
                "coordinates": metadata.get("coordinates"),
                "parent_id": metadata.get("parent_id"),
            }
        }

        return table_record

    def _is_table_like_text(self, text_content: str, element: Any) -> bool:
        """
        Detect if text content appears to be table data that should be filtered out.

        Args:
            text_content: The text content to check
            element: The element object (for metadata access)

        Returns:
            True if the text appears to be table data, False otherwise
        """
        # Check 1: Does it start with common table indicators?
        table_indicators = [
            'Table data:',
            'table data:',
            '| ',  # Markdown table
            '<table',  # HTML table remnant
        ]
        if any(text_content.startswith(indicator) for indicator in table_indicators):
            return True

        # Check 2: Does it have table-like patterns?
        # Multiple consecutive date patterns (YYYY-MM-DD)
        import re
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        date_matches = re.findall(date_pattern, text_content)
        if len(date_matches) >= 3:  # Likely a table row or column of dates
            return True

        # Check 3: High density of tab characters or multiple consecutive spaces (table formatting)
        if text_content.count('\t') >= 3:
            return True

        # Check 4: Pattern of "word number word number" repeating (table cells)
        # Example: "Design 2024-01-30 2024-02-26 Development 2024-02-27"
        words = text_content.split()
        if len(words) >= 8:  # Need enough words to check pattern
            # Count transitions between word-like and number/date-like tokens
            transitions = 0
            for i in range(len(words) - 1):
                curr_is_num = bool(re.match(r'[\d$,.-]+', words[i]))
                next_is_num = bool(re.match(r'[\d$,.-]+', words[i + 1]))
                if curr_is_num != next_is_num:
                    transitions += 1
            # High transition count suggests alternating text/numbers (table data)
            if transitions >= 6:
                return True

        # Check 5: Contains multiple currency amounts (table of financial data)
        currency_pattern = r'\$[\d,]+\.?\d*'
        currency_matches = re.findall(currency_pattern, text_content)
        if len(currency_matches) >= 3:
            return True

        return False

    def _print_summary(
        self,
        filename: str,
        tables: List[Dict[str, Any]],
        texts: List[str]
    ) -> None:
        """
        Print a summary of the processed document.

        Args:
            filename: Name of the processed file
            tables: List of extracted tables
            texts: List of extracted text chunks
        """
        print("\n" + "=" * 60)
        print(f"PROCESSING SUMMARY: {filename}")
        print("=" * 60)
        print(f"📊 Tables extracted: {len(tables)}")
        print(f"📝 Text chunks extracted: {len(texts)}")

        if tables:
            print("\nTable Details:")
            for i, table in enumerate(tables, 1):
                page = table['metadata'].get('page_number', 'Unknown')
                print(f"  • Table {i}: Page {page}, Type: {table['content_type']}")

        if texts:
            total_chars = sum(len(text) for text in texts)
            avg_chars = total_chars / len(texts) if texts else 0
            print(f"\nText Statistics:")
            print(f"  • Total characters: {total_chars:,}")
            print(f"  • Average chunk size: {avg_chars:.0f} characters")

        print("=" * 60 + "\n")


def process_single_pdf(file_path: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Convenience function to process a single PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Tuple of (tables_to_store, text_to_embed)

    Example:
        >>> tables, texts = process_single_pdf("data/contract.pdf")
        >>> print(f"Found {len(tables)} tables and {len(texts)} text chunks")
    """
    processor = DocumentProcessor()
    return processor.process_pdf(file_path)


def process_directory(directory_path: str) -> Dict[str, Tuple[List[Dict[str, Any]], List[str]]]:
    """
    Process all PDF files in a directory.

    Args:
        directory_path: Path to directory containing PDF files

    Returns:
        Dictionary mapping filenames to their (tables, texts) tuples

    Example:
        >>> results = process_directory("data/")
        >>> for filename, (tables, texts) in results.items():
        ...     print(f"{filename}: {len(tables)} tables, {len(texts)} texts")
    """
    directory = Path(directory_path)
    if not directory.is_dir():
        raise ValueError(f"Not a directory: {directory_path}")

    pdf_files = list(directory.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {directory_path}")
        return {}

    print(f"Found {len(pdf_files)} PDF files to process\n")

    results = {}
    processor = DocumentProcessor()

    for pdf_file in pdf_files:
        try:
            tables, texts = processor.process_pdf(str(pdf_file))
            results[pdf_file.name] = (tables, texts)
        except Exception as e:
            print(f"❌ Error processing {pdf_file.name}: {str(e)}\n")
            continue

    return results


if __name__ == "__main__":
    """
    Example usage demonstrating the ingestion pipeline.
    """
    import sys

    # Check if a file path was provided as command-line argument
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        tables, texts = process_single_pdf(pdf_path)

    else:
        # Default: process all PDFs in the data directory
        print("No file specified. Processing all PDFs in 'data/' directory...\n")
        results = process_directory("data")

        # Print overall summary
        if results:
            total_tables = sum(len(tables) for tables, _ in results.values())
            total_texts = sum(len(texts) for _, texts in results.values())
            print(f"\n🎉 BATCH PROCESSING COMPLETE")
            print(f"Files processed: {len(results)}")
            print(f"Total tables: {total_tables}")
            print(f"Total text chunks: {total_texts}")

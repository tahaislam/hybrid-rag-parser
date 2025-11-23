"""
run_pipeline.py
Main orchestration script for the Hybrid RAG Parser.

This script:
1. Initializes the DocumentProcessor (ingest.py)
2. Initializes the EmbeddingModel (embedding.py)
3. Initializes the DB Connectors (db_connectors.py)
4. Sets up the Qdrant collection.
5. Processes all PDFs in the 'data/' directory.
6. For each PDF:
   - Extracts tables and text.
   - Inserts tables into MongoDB.
   - Embeds text and inserts vectors into Qdrant.
"""

from src.ingestion.ingest import DocumentProcessor
from src.ingestion.embedding import EmbeddingModel
from src.database.db_connectors import MongoConnector, QdrantConnector
import os
import re
from typing import List, Dict, Any

# --- Configuration ---
PDF_DIRECTORY = "data"
QDRANT_COLLECTION = "document_chunks"

def extract_table_text_for_vectorization(tables: List[Dict[str, Any]]) -> List[str]:
    """
    Extract searchable text from tables for vector indexing.

    This function addresses a critical RAG limitation: when document content
    is primarily in tables, vector search can't find the right document because
    keywords only exist in structured data (MongoDB), not in text chunks (Qdrant).

    Solution: Extract all text from tables and create searchable chunks that
    include table content. This allows vector search to match queries like
    "What was the F1 score of XGBoost?" to documents containing that data.

    Args:
        tables: List of table dictionaries with 'content' field (HTML)

    Returns:
        List of text strings suitable for vector embedding
    """
    table_texts = []

    for table in tables:
        content = table.get('content', '')
        if not content or not isinstance(content, str):
            continue

        # Extract all text from HTML table (remove tags, keep content)
        # This captures column headers, row headers, and cell values
        text_content = re.sub(r'<[^>]+>', ' ', content)  # Remove HTML tags
        text_content = re.sub(r'\s+', ' ', text_content)  # Normalize whitespace
        text_content = text_content.strip()

        if len(text_content) > 10:  # Only add non-trivial content
            # Create a descriptive summary that includes table structure info
            table_summary = f"Table data: {text_content}"
            table_texts.append(table_summary)

    return table_texts

def main():
    print("🚀 Starting Hybrid RAG Ingestion Pipeline...")

    # 1. Initialize all components
    try:
        processor = DocumentProcessor()
        embedder = EmbeddingModel() # This will load the model (takes a moment)
        mongo = MongoConnector()
        qdrant = QdrantConnector(collection_name=QDRANT_COLLECTION)
    except Exception as e:
        print(f"Failed to initialize components: {e}")
        return

    # 2. Setup Qdrant collection (must match the model's vector size)
    vector_size = embedder.vector_size
    qdrant.setup_collection(vector_size=vector_size)

    # 3. Find PDF files in the data directory
    pdf_files = [f for f in os.listdir(PDF_DIRECTORY) if f.endswith(".pdf")]
    if not pdf_files:
        print(f"No PDF files found in '{PDF_DIRECTORY}'. Exiting.")
        return

    print(f"Found {len(pdf_files)} PDF files to process.")

    # 4. Process each PDF
    for pdf_file in pdf_files:
        file_path = os.path.join(PDF_DIRECTORY, pdf_file)
        print(f"\n{'='*80}\nProcessing file: {pdf_file}\n{'='*80}")
        
        try:
            # --- Phase 1: Ingest ---
            # Use "auto" strategy for better table detection
            tables, texts = processor.process_pdf(file_path, strategy="auto")
            
            if not tables and not texts:
                print("No content extracted.")
                continue

            # --- Phase 2a: Store Tables (NoSQL) ---
            if tables:
                mongo.insert_tables(tables, source_filename=pdf_file)

                # ENHANCEMENT: Extract table content for vector search
                # This solves the problem where documents with primarily table data
                # can't be found by vector search (e.g., "What was the F1 score of XGBoost?")
                print(f"  → Extracting searchable text from {len(tables)} tables...")
                table_texts = extract_table_text_for_vectorization(tables)
                texts.extend(table_texts)
                print(f"  → Added {len(table_texts)} table summary chunks for vector search")
            else:
                print("No tables found in this document.")

            # --- Phase 2b: Embed & Store Text (Vector) ---
            if texts:
                # Generate Qdrant points (id, vector, payload)
                vector_points = embedder.prepare_qdrant_points(texts, source_filename=pdf_file)
                # Insert points into Qdrant
                qdrant.insert_vectors(vector_points)
            else:
                print("No text chunks found in this document.")
                
            print(f"Successfully processed and stored: {pdf_file}")

        except Exception as e:
            print(f"❌ FAILED to process {pdf_file}. Error: {e}")

    print("\n🎉 Pipeline complete! All documents processed.")

if __name__ == "__main__":
    main()
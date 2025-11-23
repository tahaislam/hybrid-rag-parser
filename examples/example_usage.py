"""
Example Usage of the Table-Aware RAG Ingestion Pipeline
=========================================================
This script demonstrates how to use the ingest.py module to process PDF files.

Before running this script, install dependencies:
    pip install -r requirements.txt

Note: The installation may take several minutes due to heavy dependencies
(PyTorch, layout detection models, etc.)
"""

from src.ingestion.ingest import DocumentProcessor, process_single_pdf, process_directory


def example_1_single_file():
    """Example 1: Process a single PDF file."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Processing a Single PDF File")
    print("="*80)

    # Process a single file
    tables, texts = process_single_pdf("data/sample1.pdf")

    # Inspect the results
    print(f"\nExtracted {len(tables)} tables:")
    for i, table in enumerate(tables, 1):
        print(f"\n  Table {i}:")
        print(f"    - ID: {table['table_id']}")
        print(f"    - Page: {table['metadata'].get('page_number', 'Unknown')}")
        print(f"    - Format: {table['content_type']}")
        print(f"    - Content preview: {table['content'][:100]}...")

    print(f"\nExtracted {len(texts)} text chunks:")
    for i, text in enumerate(texts[:3], 1):  # Show first 3
        print(f"\n  Text {i}: {text[:100]}...")


def example_2_batch_processing():
    """Example 2: Process all PDFs in a directory."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Batch Processing Multiple PDFs")
    print("="*80)

    # Process all PDFs in the data directory
    results = process_directory("data")

    # Analyze results
    for filename, (tables, texts) in results.items():
        print(f"\n{filename}:")
        print(f"  - Tables: {len(tables)}")
        print(f"  - Text chunks: {len(texts)}")


def example_3_custom_processor():
    """Example 3: Using the DocumentProcessor class directly for more control."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Using DocumentProcessor Class Directly")
    print("="*80)

    # Create a processor instance
    processor = DocumentProcessor()

    # Process with custom settings
    tables, texts = processor.process_pdf(
        file_path="data/sample1.pdf",
        strategy="hi_res",  # Use hi_res for best table detection
        extract_tables_as="html"  # Get tables as HTML
    )

    print(f"\nProcessed with custom settings:")
    print(f"  - Strategy: hi_res")
    print(f"  - Table format: HTML")
    print(f"  - Results: {len(tables)} tables, {len(texts)} texts")


def example_4_prepare_for_storage():
    """Example 4: Prepare data for database storage (next phase)."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Preparing Data for Database Storage")
    print("="*80)

    tables, texts = process_single_pdf("data/sample1.pdf")

    # Simulate what would be stored in MongoDB (NoSQL)
    print("\n📦 Data ready for MongoDB (tables):")
    print(f"  - Number of documents: {len(tables)}")
    print(f"  - Collection name: 'extracted_tables'")
    print(f"  - Sample document structure:")
    if tables:
        import json
        print(json.dumps(tables[0], indent=2, default=str))

    # Simulate what would be embedded and stored in Qdrant (Vector DB)
    print("\n🔍 Data ready for Qdrant (vector embeddings):")
    print(f"  - Number of text chunks: {len(texts)}")
    print(f"  - Collection name: 'document_embeddings'")
    print(f"  - Next step: Generate embeddings using sentence-transformers")
    if texts:
        print(f"  - Sample text chunk: '{texts[0][:100]}...'")


if __name__ == "__main__":
    """
    Run all examples.
    Uncomment individual examples to run them separately.
    """
    print("\n" + "🚀 " * 30)
    print("TABLE-AWARE RAG INGESTION PIPELINE - EXAMPLES")
    print("🚀 " * 30)

    # Run examples
    # Uncomment the examples you want to run:

    # example_1_single_file()
    # example_2_batch_processing()
    # example_3_custom_processor()
    # example_4_prepare_for_storage()

    # Or run all examples:
    try:
        example_1_single_file()
        example_2_batch_processing()
        example_3_custom_processor()
        example_4_prepare_for_storage()

        print("\n" + "✅ " * 30)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("✅ " * 30 + "\n")

    except ImportError as e:
        print("\n❌ Missing dependencies. Please install requirements first:")
        print("   pip install -r requirements.txt")
        print(f"\nError: {e}")
    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}")
        print("   Make sure you have PDF files in the 'data/' directory")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

"""
Debug script to inspect what's actually stored in MongoDB and Qdrant.
This will help identify if old data is still present or if tables are empty.
"""

from src.database.db_connectors import MongoConnector, QdrantConnector

def check_mongodb():
    """Check what documents are in MongoDB."""
    print("=" * 80)
    print("MONGODB INSPECTION")
    print("=" * 80)

    mongo = MongoConnector()

    # Get all unique source files
    sources = mongo.collection.distinct("source_file")
    print(f"\n📁 Found {len(sources)} unique source files:")
    for source in sorted(sources):
        print(f"   - {source}")

    # Count tables per source
    print(f"\n📊 Table count per source file:")
    for source in sorted(sources):
        count = mongo.collection.count_documents({"source_file": source})
        print(f"   - {source}: {count} tables")

    # Show sample table content from each file
    print(f"\n📄 Sample table content from each file:")
    for source in sorted(sources):
        print(f"\n   {source}:")
        tables = mongo.collection.find({"source_file": source}).limit(2)
        for i, table in enumerate(tables, 1):
            content = table.get('content', '')
            content_preview = content[:200] if len(content) > 200 else content
            print(f"      Table {i}: {content_preview}...")
            print(f"      Content length: {len(content)} chars")
            print(f"      Type: {table.get('content_type', 'unknown')}")

def check_qdrant():
    """Check what's in Qdrant."""
    print("\n" + "=" * 80)
    print("QDRANT INSPECTION")
    print("=" * 80)

    qdrant = QdrantConnector(collection_name="document_chunks")

    # Get collection info
    collection_info = qdrant.client.get_collection("document_chunks")
    print(f"\n📊 Collection stats:")
    print(f"   Total vectors: {collection_info.points_count}")

    # Get all points (limited to first 100)
    points = qdrant.client.scroll(
        collection_name="document_chunks",
        limit=100,
        with_payload=True
    )[0]

    # Extract unique sources
    sources = set()
    for point in points:
        if 'source_file' in point.payload:
            sources.add(point.payload['source_file'])

    print(f"\n📁 Found {len(sources)} unique source files in vectors:")
    for source in sorted(sources):
        # Count vectors per source
        count = sum(1 for p in points if p.payload.get('source_file') == source)
        print(f"   - {source}: {count} vectors")

def check_data_directory():
    """Check what PDFs exist in the data directory."""
    import os
    print("\n" + "=" * 80)
    print("DATA DIRECTORY INSPECTION")
    print("=" * 80)

    data_dir = "data"
    if os.path.exists(data_dir):
        pdf_files = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]
        print(f"\n📁 Found {len(pdf_files)} PDF files in data/ directory:")
        for pdf in sorted(pdf_files):
            file_path = os.path.join(data_dir, pdf)
            size = os.path.getsize(file_path)
            print(f"   - {pdf} ({size:,} bytes)")
    else:
        print(f"\n❌ Data directory not found!")

if __name__ == "__main__":
    check_data_directory()
    check_mongodb()
    check_qdrant()

    print("\n" + "=" * 80)
    print("DIAGNOSIS")
    print("=" * 80)
    print("""
If you see old files like 'sample1.pdf' or 'sample2.pdf':
  → These need to be removed from data/ directory
  → Clear databases again and re-ingest

If tables show empty content or very short content:
  → Table extraction failed (dark background issue)
  → Need to regenerate PDFs with light backgrounds

Expected files:
  - project_budget.pdf
  - financial_report.pdf
  - research_results.pdf
  - product_specs.pdf
  - sales_report.pdf
""")

#!/usr/bin/env python3
"""
Clear all data from MongoDB and Qdrant databases.
Use this before re-ingesting PDFs with updated content.
"""
from src.database.db_connectors import MongoConnector, QdrantConnector

def clear_databases():
    """Clear all documents from MongoDB and Qdrant."""

    print("="*80)
    print("CLEARING RAG DATABASES")
    print("="*80)

    # Clear MongoDB
    print("\n📦 Clearing MongoDB...")
    try:
        mongo = MongoConnector()
        result = mongo.collection.delete_many({})
        print(f"✓ Deleted {result.deleted_count} documents from MongoDB")
    except Exception as e:
        print(f"❌ Error clearing MongoDB: {e}")

    # Clear Qdrant
    print("\n🔍 Clearing Qdrant...")
    try:
        qdrant = QdrantConnector(collection_name="document_chunks")
        # Delete the entire collection
        qdrant.client.delete_collection("document_chunks")
        print("✓ Deleted Qdrant collection 'document_chunks'")

        # Recreate the collection
        from qdrant_client.http.models import Distance, VectorParams
        qdrant.client.create_collection(
            collection_name="document_chunks",
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print("✓ Recreated empty Qdrant collection")
    except Exception as e:
        print(f"❌ Error clearing Qdrant: {e}")

    print("\n" + "="*80)
    print("✓ DATABASES CLEARED")
    print("="*80)
    print("\nNext steps:")
    print("1. Regenerate PDFs (if needed): python generate_sample_pdfs.py")
    print("2. Re-ingest data: python run_pipeline.py")

if __name__ == "__main__":
    response = input("\n⚠️  This will DELETE ALL data from MongoDB and Qdrant.\nAre you sure? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        clear_databases()
    else:
        print("Cancelled.")

#!/usr/bin/env python
"""
Example: Using the Hybrid RAG Parser API via Python client

This example demonstrates how to interact with the REST API using the Python client.

Prerequisites:
1. Start the API server: python api_server.py
2. Install dependencies: pip install -r requirements.txt
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.client import RAGClient


def main():
    """Run example API client operations"""

    # Initialize client
    client = RAGClient(base_url="http://localhost:8000")

    try:
        # 1. Check health
        print("=" * 70)
        print("1. Checking service health...")
        print("=" * 70)
        health = client.health_check()
        print(f"Status: {health['status']}")
        print(f"Message: {health['message']}\n")

        # 2. Get system status
        print("=" * 70)
        print("2. Getting system status...")
        print("=" * 70)
        status = client.system_status()
        print(f"Overall Status: {status['overall_status']}")
        for service in status['services']:
            print(f"  - {service['name']}: {service['status']}")
            if service['message']:
                print(f"    {service['message']}")
        print()

        # 3. List documents
        print("=" * 70)
        print("3. Listing ingested documents...")
        print("=" * 70)
        docs = client.list_documents()
        print(f"Total documents: {docs['total_count']}")
        for doc in docs['documents']:
            print(f"  - {doc['filename']}: {doc['num_tables']} tables, {doc['num_chunks']} chunks")
        print()

        # 4. Query example (if documents exist)
        if docs['total_count'] > 0:
            print("=" * 70)
            print("4. Executing a query...")
            print("=" * 70)
            query_text = "What are the key metrics?"
            print(f"Query: {query_text}")

            response = client.query(query_text, debug=True)
            print(f"Answer: {response.answer}")
            print(f"Sources: {len(response.sources)} found")
            if response.debug_info:
                print(f"Query time: {response.debug_info.get('query_time_ms', 0):.2f}ms")
            print()

            # 5. Vector search
            print("=" * 70)
            print("5. Performing vector search...")
            print("=" * 70)
            vector_results = client.search_vectors(query_text, limit=3)
            print(f"Found {len(vector_results.results)} results")
            for i, result in enumerate(vector_results.results, 1):
                print(f"  {i}. {result.filename} (score: {result.score:.3f})")
                print(f"     {result.text[:100]}...")
            print()

            # 6. Table search
            print("=" * 70)
            print("6. Searching tables...")
            print("=" * 70)
            table_results = client.search_tables(query_text, limit=3)
            print(f"Found {len(table_results.results)} tables")
            for i, result in enumerate(table_results.results, 1):
                print(f"  {i}. {result.filename} (table {result.table_index})")
                print(f"     {result.table_data[:100]}...")
            print()

        # 7. Cache statistics
        print("=" * 70)
        print("7. Cache statistics...")
        print("=" * 70)
        cache_stats = client.cache_stats()
        print(f"Cache enabled: {cache_stats['cache_enabled']}")
        print(f"Total entries: {cache_stats['total_entries']}")
        print(f"Hit rate: {cache_stats['hit_rate']:.2%}")
        print()

        # 8. Ingest document example (uncomment to use)
        # print("=" * 70)
        # print("8. Ingesting a document...")
        # print("=" * 70)
        # ingest_result = client.ingest_document("data/sample.pdf")
        # print(f"Status: {ingest_result['status']}")
        # print(f"Tables extracted: {ingest_result['num_tables']}")
        # print(f"Text chunks: {ingest_result['num_chunks']}")
        # print()

        print("=" * 70)
        print("Example completed successfully!")
        print("=" * 70)
        print("\nAPI Documentation:")
        print("  - Swagger UI: http://localhost:8000/docs")
        print("  - ReDoc: http://localhost:8000/redoc")

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure the API server is running:")
        print("  python api_server.py")
        sys.exit(1)

    finally:
        client.close()


if __name__ == "__main__":
    main()

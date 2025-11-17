"""
view_qdrant_data.py
Helper script to view and query data stored in Qdrant.

This script provides an easy way to see the actual text content
stored in Qdrant without dealing with raw vector data.
"""

from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

def view_all_points(collection_name: str = "document_chunks", limit: int = 10):
    """
    View all points in the Qdrant collection with their text payloads.

    Args:
        collection_name: Name of the Qdrant collection
        limit: Maximum number of points to display
    """
    client = QdrantClient("localhost", port=6333)

    # Get collection info
    try:
        collection_info = client.get_collection(collection_name)
        print(f"\n{'='*80}")
        print(f"QDRANT COLLECTION: {collection_name}")
        print(f"{'='*80}")
        print(f"Total vectors: {collection_info.points_count}")
        print(f"Vector size: {collection_info.config.params.vectors.size}")
        print(f"Distance metric: {collection_info.config.params.vectors.distance}")
        print(f"{'='*80}\n")
    except Exception as e:
        print(f"Error accessing collection: {e}")
        return

    # Scroll through points
    try:
        points, _ = client.scroll(
            collection_name=collection_name,
            limit=limit,
            with_payload=True,
            with_vectors=False  # Don't fetch the vector data (too large)
        )

        if not points:
            print("No points found in the collection.")
            print("\nHave you run 'python run_pipeline.py' yet?")
            return

        print(f"Showing first {len(points)} points:\n")

        for i, point in enumerate(points, 1):
            print(f"{'-'*80}")
            print(f"Point {i}")
            print(f"{'-'*80}")
            print(f"ID: {point.id}")

            if point.payload:
                print(f"\nSource File: {point.payload.get('source_filename', 'N/A')}")
                print(f"Chunk Index: {point.payload.get('chunk_index', 'N/A')}")
                print(f"\nText Content:")
                print(f"  {point.payload.get('text', 'No text available')[:200]}...")
            else:
                print("No payload data available")

            print()

    except Exception as e:
        print(f"Error scrolling collection: {e}")


def view_by_source(source_filename: str, collection_name: str = "document_chunks"):
    """
    View all points from a specific source file.

    Args:
        source_filename: Name of the source PDF file
        collection_name: Name of the Qdrant collection
    """
    client = QdrantClient("localhost", port=6333)

    print(f"\n{'='*80}")
    print(f"POINTS FROM: {source_filename}")
    print(f"{'='*80}\n")

    try:
        # Scroll with filter
        points, _ = client.scroll(
            collection_name=collection_name,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="source_filename",
                        match=MatchValue(value=source_filename)
                    )
                ]
            ),
            with_payload=True,
            with_vectors=False,
            limit=100
        )

        if not points:
            print(f"No points found for source file: {source_filename}")
            return

        print(f"Found {len(points)} text chunks from {source_filename}\n")

        for i, point in enumerate(points, 1):
            print(f"{'-'*80}")
            print(f"Chunk {i} (ID: {point.id})")
            print(f"{'-'*80}")
            print(point.payload.get('text', 'No text'))
            print()

    except Exception as e:
        print(f"Error querying collection: {e}")


def search_similar_text(query: str, collection_name: str = "document_chunks", limit: int = 5):
    """
    Search for text chunks similar to the query.

    Args:
        query: The search query text
        collection_name: Name of the Qdrant collection
        limit: Number of results to return
    """
    from embedding import EmbeddingModel

    client = QdrantClient("localhost", port=6333)
    embedder = EmbeddingModel()

    print(f"\n{'='*80}")
    print(f"SEARCHING FOR: '{query}'")
    print(f"{'='*80}\n")

    try:
        # Generate query vector
        query_vector = embedder.embed_texts([query])[0]

        # Search
        results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit
        )

        if not results:
            print("No results found.")
            return

        print(f"Top {len(results)} results:\n")

        for i, result in enumerate(results, 1):
            print(f"{'-'*80}")
            print(f"Result {i} - Similarity Score: {result.score:.4f}")
            print(f"{'-'*80}")
            print(f"Source: {result.payload.get('source_filename', 'N/A')}")
            print(f"Chunk Index: {result.payload.get('chunk_index', 'N/A')}")
            print(f"\nText:")
            print(f"  {result.payload.get('text', 'No text')}")
            print()

    except Exception as e:
        print(f"Error searching: {e}")


def collection_stats(collection_name: str = "document_chunks"):
    """
    Display statistics about the collection grouped by source file.

    Args:
        collection_name: Name of the Qdrant collection
    """
    client = QdrantClient("localhost", port=6333)

    print(f"\n{'='*80}")
    print(f"COLLECTION STATISTICS")
    print(f"{'='*80}\n")

    try:
        # Get all points
        points, _ = client.scroll(
            collection_name=collection_name,
            with_payload=True,
            with_vectors=False,
            limit=10000  # Adjust if you have more points
        )

        if not points:
            print("No data in collection.")
            return

        # Group by source file
        file_stats = {}
        for point in points:
            source = point.payload.get('source_filename', 'Unknown')
            if source not in file_stats:
                file_stats[source] = {
                    'count': 0,
                    'total_chars': 0
                }
            file_stats[source]['count'] += 1
            text = point.payload.get('text', '')
            file_stats[source]['total_chars'] += len(text)

        print(f"Total Points: {len(points)}\n")
        print("Breakdown by Source File:")
        print(f"{'-'*80}")

        for source, stats in sorted(file_stats.items()):
            avg_chars = stats['total_chars'] / stats['count'] if stats['count'] > 0 else 0
            print(f"\n📄 {source}")
            print(f"   • Text chunks: {stats['count']}")
            print(f"   • Total characters: {stats['total_chars']:,}")
            print(f"   • Avg chunk size: {avg_chars:.0f} characters")

    except Exception as e:
        print(f"Error getting stats: {e}")


if __name__ == "__main__":
    import sys

    print("\n" + "🔍 " * 30)
    print("QDRANT DATA VIEWER")
    print("🔍 " * 30)

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "stats":
            collection_stats()

        elif command == "view" and len(sys.argv) > 2:
            view_by_source(sys.argv[2])

        elif command == "search" and len(sys.argv) > 2:
            query = " ".join(sys.argv[2:])
            search_similar_text(query)

        else:
            print("\nUsage:")
            print("  python view_qdrant_data.py stats              # Show collection statistics")
            print("  python view_qdrant_data.py view <filename>    # View all chunks from a file")
            print("  python view_qdrant_data.py search <query>     # Search for similar text")
            print("\nExamples:")
            print("  python view_qdrant_data.py stats")
            print("  python view_qdrant_data.py view sample1.pdf")
            print("  python view_qdrant_data.py search payment terms")

    else:
        # Default: show overview
        collection_stats()
        print("\n")
        view_all_points(limit=5)

        print("\n" + "="*80)
        print("TIP: For more options, run:")
        print("  python view_qdrant_data.py stats")
        print("  python view_qdrant_data.py view sample1.pdf")
        print("  python view_qdrant_data.py search 'your search query'")
        print("="*80 + "\n")

"""
Debug script to understand why vector search is failing for test 8.
This will show what text chunks are actually stored and how they're matching.
"""

from src.database.db_connectors import QdrantConnector
from src.ingestion.embedding import EmbeddingModel

def debug_vector_search():
    """Debug why 'F1 score of XGBoost' matches sales_report instead of research_results."""

    print("=" * 80)
    print("DEBUGGING VECTOR SEARCH FOR: 'What was the F1 score of XGBoost?'")
    print("=" * 80)

    # Initialize components
    qdrant = QdrantConnector(collection_name="document_chunks")
    embedder = EmbeddingModel()

    # Create query embedding
    query = "What was the F1 score of XGBoost?"
    query_vector = embedder.embed_text(query)

    # Search for similar vectors
    results = qdrant.client.search(
        collection_name="document_chunks",
        query_vector=query_vector,
        limit=10,  # Get top 10 matches
        with_payload=True
    )

    print(f"\n📊 Top 10 vector search results for: '{query}'")
    print("-" * 80)

    for i, result in enumerate(results, 1):
        source = result.payload.get('source_file', 'unknown')
        content = result.payload.get('content', '')
        score = result.score

        print(f"\n{i}. Source: {source} (Score: {score:.4f})")
        print(f"   Content: {content[:200]}...")

    # Now let's see ALL chunks from research_results.pdf
    print("\n" + "=" * 80)
    print("ALL CHUNKS FROM research_results.pdf")
    print("=" * 80)

    all_points = qdrant.client.scroll(
        collection_name="document_chunks",
        limit=100,
        with_payload=True
    )[0]

    research_chunks = [p for p in all_points if p.payload.get('source_file') == 'research_results.pdf']

    print(f"\nFound {len(research_chunks)} chunks from research_results.pdf:")
    for i, chunk in enumerate(research_chunks, 1):
        content = chunk.payload.get('content', '')
        print(f"\n{i}. {content}")

    # Check if "XGBoost" or "F1" appear in any chunk
    print("\n" + "=" * 80)
    print("KEYWORD ANALYSIS")
    print("=" * 80)

    has_xgboost = any('xgboost' in chunk.payload.get('content', '').lower() for chunk in research_chunks)
    has_f1 = any('f1' in chunk.payload.get('content', '').lower() for chunk in research_chunks)

    print(f"\nDoes research_results.pdf have 'XGBoost'? {has_xgboost}")
    print(f"Does research_results.pdf have 'F1'? {has_f1}")

    if not has_xgboost or not has_f1:
        print("\n⚠️  PROBLEM IDENTIFIED:")
        print("The text chunks from research_results.pdf don't contain the keywords")
        print("'XGBoost' or 'F1 score'. This is why vector search is failing!")
        print("\nThe PDF only has a TABLE with this data, but tables are stored in MongoDB,")
        print("not in Qdrant vectors. So the vector search can't find the right document.")
        print("\n💡 SOLUTION:")
        print("Need to add table metadata/summaries to the text chunks so vector search")
        print("can find documents based on table content.")

if __name__ == "__main__":
    debug_vector_search()

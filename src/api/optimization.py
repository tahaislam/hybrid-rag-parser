"""Query optimization utilities for performance enhancement"""

import logging
from typing import List, Dict, Any, Optional
from src.api.cache import get_cache
from src.ingestion.embedding import EmbeddingModel

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """Handles query optimization and caching of expensive operations"""

    def __init__(self):
        self.cache = get_cache()
        self.embedder = EmbeddingModel()
        self.embedding_cache_hits = 0
        self.embedding_cache_misses = 0

    def get_embedding_cached(self, text: str) -> Optional[List[float]]:
        """
        Get embedding with caching to avoid recomputing for identical queries

        Args:
            text: Text to embed

        Returns:
            Embedding vector or None if computation failed
        """
        # Check cache first
        cached = self.cache.get_embedding_cache(text)
        if cached:
            self.embedding_cache_hits += 1
            logger.debug(f"Embedding cache hit for: {text[:30]}...")
            return cached

        # Compute embedding
        try:
            embedding = self.embedder.embed_text(text)
            self.embedding_cache_misses += 1

            # Cache the result
            self.cache.set_embedding_cache(text, embedding)
            logger.debug(f"Embedding cached for: {text[:30]}...")
            return embedding

        except Exception as e:
            logger.error(f"Embedding computation failed: {e}")
            self.embedding_cache_misses += 1
            return None

    def optimize_vector_search_results(
        self,
        results: List[Dict[str, Any]],
        max_results: int = 3,
        score_threshold: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Optimize vector search results by filtering and ranking

        Args:
            results: Raw vector search results
            max_results: Maximum number of results to return
            score_threshold: Minimum similarity score (0-1)

        Returns:
            Filtered and ranked results
        """
        # Filter by score threshold
        filtered = [r for r in results if r.get("score", 0) >= score_threshold]

        # Sort by score (descending) and take top N
        sorted_results = sorted(
            filtered,
            key=lambda x: x.get("score", 0),
            reverse=True,
        )[:max_results]

        logger.info(f"Optimized {len(results)} results to {len(sorted_results)} (threshold: {score_threshold})")
        return sorted_results

    def deduplicate_results(
        self,
        results: List[Dict[str, Any]],
        key: str = "text",
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicate results based on a key

        Args:
            results: Results to deduplicate
            key: Field to use for deduplication

        Returns:
            Deduplicated results
        """
        seen = set()
        unique = []

        for result in results:
            value = str(result.get(key, "")).strip()
            if value and value not in seen:
                seen.add(value)
                unique.append(result)

        if len(unique) < len(results):
            logger.info(f"Removed {len(results) - len(unique)} duplicate results")

        return unique

    def merge_results(
        self,
        vector_results: List[Dict[str, Any]],
        table_results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Merge vector and table search results intelligently

        Args:
            vector_results: Vector search results
            table_results: Table search results

        Returns:
            Merged and ranked results
        """
        # Weight results by type
        merged = []

        # Add vector results with weight
        for r in vector_results:
            r["_weight"] = 1.0
            r["_type"] = "vector"
            merged.append(r)

        # Add table results with weight
        for r in table_results:
            r["_weight"] = 0.8
            r["_type"] = "table"
            merged.append(r)

        # Sort by score and weight
        merged.sort(
            key=lambda x: x.get("score", 0) * x.get("_weight", 1),
            reverse=True,
        )

        logger.info(f"Merged {len(vector_results)} vector + {len(table_results)} table results")
        return merged

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        total_embedding_requests = self.embedding_cache_hits + self.embedding_cache_misses
        embedding_hit_rate = (
            self.embedding_cache_hits / total_embedding_requests
            if total_embedding_requests > 0
            else 0
        )

        return {
            "embedding_cache": {
                "hits": self.embedding_cache_hits,
                "misses": self.embedding_cache_misses,
                "hit_rate": embedding_hit_rate,
            },
        }


class VectorSearchOptimizer:
    """Optimizes vector search parameters based on query characteristics"""

    @staticmethod
    def calculate_optimal_limit(query_length: int) -> int:
        """
        Calculate optimal number of results based on query length

        Args:
            query_length: Length of the query string

        Returns:
            Recommended search limit
        """
        # Shorter queries -> need more results to find relevant ones
        # Longer queries -> more specific, can use fewer results
        if query_length < 20:
            return 5  # Short query, broader search
        elif query_length < 50:
            return 3  # Medium query, balanced
        else:
            return 2  # Long query, very specific

    @staticmethod
    def calculate_optimal_score_threshold(
        domain: str = "general",
    ) -> float:
        """
        Calculate optimal similarity score threshold

        Args:
            domain: Domain type (general, technical, medical, legal)

        Returns:
            Recommended score threshold (0-1)
        """
        thresholds = {
            "general": 0.3,
            "technical": 0.4,
            "medical": 0.5,
            "legal": 0.6,
        }
        return thresholds.get(domain, 0.3)

    @staticmethod
    def estimate_result_quality(
        results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Estimate quality of search results

        Args:
            results: Search results

        Returns:
            Quality assessment
        """
        if not results:
            return {"quality": "no_results", "score": 0.0}

        scores = [r.get("score", 0) for r in results]
        avg_score = sum(scores) / len(scores) if scores else 0
        max_score = max(scores) if scores else 0
        score_variance = (
            sum((s - avg_score) ** 2 for s in scores) / len(scores)
            if len(scores) > 1
            else 0
        )

        if avg_score > 0.7:
            quality = "excellent"
        elif avg_score > 0.5:
            quality = "good"
        elif avg_score > 0.3:
            quality = "fair"
        else:
            quality = "poor"

        return {
            "quality": quality,
            "average_score": avg_score,
            "max_score": max_score,
            "score_variance": score_variance,
            "result_count": len(results),
        }

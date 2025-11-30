"""Query endpoints for RAG functionality"""

import logging
import time
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, status, HTTPException

from src.api.schemas import (
    QueryRequest, QueryResponse,
    VectorSearchRequest, VectorSearchResponse, VectorSearchResult,
    TableSearchRequest, TableSearchResponse, TableSearchResult,
)
from src.api.cache import get_cache
from src.api.optimization import QueryOptimizer, VectorSearchOptimizer
from src.query.query import QueryEngine
from src.database.db_connectors import MongoConnector, QdrantConnector

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["query"])

# Initialize query engine and optimizer once
_query_engine: Optional[QueryEngine] = None
_query_optimizer: Optional[QueryOptimizer] = None
_vector_search_optimizer: Optional[VectorSearchOptimizer] = None


def get_query_engine() -> QueryEngine:
    """Get or initialize query engine"""
    global _query_engine
    if _query_engine is None:
        _query_engine = QueryEngine(temperature=0.0)  # Deterministic by default
    return _query_engine


def get_optimizer() -> QueryOptimizer:
    """Get or initialize query optimizer"""
    global _query_optimizer
    if _query_optimizer is None:
        _query_optimizer = QueryOptimizer()
    return _query_optimizer


def get_vector_optimizer() -> VectorSearchOptimizer:
    """Get vector search optimizer"""
    global _vector_search_optimizer
    if _vector_search_optimizer is None:
        _vector_search_optimizer = VectorSearchOptimizer()
    return _vector_search_optimizer


@router.post("/query", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def hybrid_query(request: QueryRequest) -> QueryResponse:
    """
    Execute a hybrid RAG query combining vector search and table lookup

    - **question**: The question to ask
    - **file_filter**: Optional filename to filter results
    - **debug**: Enable debug mode to see formatted context
    """
    try:
        cache = get_cache()

        # Check cache first
        cached_result = cache.get_query_cache(request.question, request.file_filter)
        if cached_result and not request.debug:
            logger.info(f"Cache hit for query: {request.question[:50]}...")
            return QueryResponse(**cached_result)

        # Execute query
        start_time = time.time()
        query_engine = get_query_engine()
        answer = query_engine.ask(request.question, debug=request.debug)
        query_time_ms = (time.time() - start_time) * 1000

        # Get sources for response
        vector_results = query_engine.search_vectors(request.question)
        table_results = query_engine.search_tables(request.question, request.file_filter)

        sources = []
        for vec_result in vector_results:
            sources.append({
                "type": "text",
                "filename": vec_result.get("filename"),
                "content": vec_result.get("text", "")[:200],
            })
        for table_result in table_results:
            sources.append({
                "type": "table",
                "filename": table_result.get("filename"),
                "content": table_result.get("table", "")[:200],
            })

        response = QueryResponse(
            answer=answer,
            sources=sources,
            debug_info={"query_time_ms": query_time_ms} if request.debug else None,
        )

        # Cache result
        cache.set_query_cache(request.question, response.model_dump(), request.file_filter)

        logger.info(f"Query executed: {request.question[:50]}... (time: {query_time_ms:.2f}ms)")
        return response

    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}"
        )


@router.post("/search/vectors", response_model=VectorSearchResponse, status_code=status.HTTP_200_OK)
async def vector_search(request: VectorSearchRequest) -> VectorSearchResponse:
    """
    Perform semantic vector search on text chunks

    - **query**: Text to search semantically
    - **limit**: Number of results to return (default: 3)
    """
    try:
        start_time = time.time()
        query_engine = get_query_engine()
        optimizer = get_optimizer()
        vector_optimizer = get_vector_optimizer()

        # Search vectors with optimization
        results = query_engine.search_vectors(request.query)

        # Optimize results
        optimized_results = optimizer.optimize_vector_search_results(
            results,
            max_results=request.limit,
            score_threshold=0.0,  # Configurable threshold
        )

        # Deduplicate results
        deduped_results = optimizer.deduplicate_results(optimized_results)

        # Format response
        vector_results = [
            VectorSearchResult(
                text=result.get("text", "")[:500],
                filename=result.get("filename", "unknown"),
                score=result.get("score", 0.0),
                metadata={"source": result.get("source")},
            )
            for result in deduped_results
        ]

        query_time_ms = (time.time() - start_time) * 1000

        logger.info(f"Vector search: {request.query[:50]}... ({len(vector_results)} results, {query_time_ms:.2f}ms)")
        return VectorSearchResponse(
            results=vector_results,
            query_time_ms=query_time_ms,
        )

    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vector search failed: {str(e)}"
        )


@router.post("/search/tables", response_model=TableSearchResponse, status_code=status.HTTP_200_OK)
async def table_search(request: TableSearchRequest) -> TableSearchResponse:
    """
    Search for tables in ingested documents

    - **query**: Search query
    - **file_filter**: Optional filename to filter results
    - **limit**: Number of table results to return (default: 5)
    """
    try:
        start_time = time.time()
        query_engine = get_query_engine()

        # Search tables
        results = query_engine.search_tables(request.query, request.file_filter)

        # Format response
        table_results = [
            TableSearchResult(
                table_data=result.get("table", "")[:1000],
                filename=result.get("filename", "unknown"),
                table_index=result.get("table_index", 0),
                metadata={"source": result.get("source")},
            )
            for result in results[:request.limit]
        ]

        query_time_ms = (time.time() - start_time) * 1000

        logger.info(f"Table search: {request.query[:50]}... ({len(table_results)} results)")
        return TableSearchResponse(
            results=table_results,
            query_time_ms=query_time_ms,
        )

    except Exception as e:
        logger.error(f"Table search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Table search failed: {str(e)}"
        )


@router.post("/cache/clear", status_code=status.HTTP_200_OK)
async def clear_cache():
    """Clear query cache"""
    try:
        cache = get_cache()
        cache.clear_query_cache()
        logger.info("Query cache cleared")
        return {
            "status": "success",
            "message": "Query cache cleared successfully",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"Cache clear failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache clear failed: {str(e)}"
        )

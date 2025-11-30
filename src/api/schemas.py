"""Pydantic schemas for API request/response validation"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# Query Request/Response Models
# ============================================================================

class QueryRequest(BaseModel):
    """Request model for RAG query endpoint"""
    question: str = Field(..., min_length=1, max_length=2000, description="The question to ask")
    file_filter: Optional[str] = Field(None, description="Optional filename to filter results")
    debug: bool = Field(False, description="Enable debug mode to see formatted context")


class QueryResponse(BaseModel):
    """Response model for RAG query endpoint"""
    answer: str = Field(..., description="The LLM-generated answer")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source documents and tables used")
    debug_info: Optional[Dict[str, Any]] = Field(None, description="Debug information (when debug=true)")


# ============================================================================
# Vector Search Models
# ============================================================================

class VectorSearchRequest(BaseModel):
    """Request model for vector search"""
    query: str = Field(..., min_length=1, max_length=2000, description="Text to search semantically")
    limit: int = Field(3, ge=1, le=20, description="Number of results to return")


class VectorSearchResult(BaseModel):
    """Single vector search result"""
    text: str = Field(..., description="Retrieved text chunk")
    filename: str = Field(..., description="Source document filename")
    score: float = Field(..., description="Similarity score (0-1)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class VectorSearchResponse(BaseModel):
    """Response model for vector search"""
    results: List[VectorSearchResult] = Field(..., description="Search results")
    query_time_ms: float = Field(..., description="Query execution time in milliseconds")


# ============================================================================
# Table Search Models
# ============================================================================

class TableSearchRequest(BaseModel):
    """Request model for table search"""
    query: str = Field(..., min_length=1, max_length=2000, description="Search query")
    file_filter: Optional[str] = Field(None, description="Filter by source filename")
    limit: int = Field(5, ge=1, le=20, description="Number of table results")


class TableSearchResult(BaseModel):
    """Single table search result"""
    table_data: str = Field(..., description="Table content (markdown format)")
    filename: str = Field(..., description="Source document filename")
    table_index: int = Field(..., description="Index of table in document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TableSearchResponse(BaseModel):
    """Response model for table search"""
    results: List[TableSearchResult] = Field(..., description="Table search results")
    query_time_ms: float = Field(..., description="Query execution time in milliseconds")


# ============================================================================
# Document Management Models
# ============================================================================

class DocumentMetadata(BaseModel):
    """Metadata for an ingested document"""
    filename: str = Field(..., description="Document filename")
    upload_date: str = Field(..., description="ISO format upload timestamp")
    num_tables: int = Field(..., description="Number of tables extracted")
    num_chunks: int = Field(..., description="Number of text chunks indexed")
    file_size_bytes: int = Field(..., description="Original file size in bytes")


class DocumentListResponse(BaseModel):
    """Response model for listing documents"""
    documents: List[DocumentMetadata] = Field(..., description="List of ingested documents")
    total_count: int = Field(..., description="Total number of documents")


class IngestionRequest(BaseModel):
    """Request model for document ingestion"""
    parse_strategy: str = Field("auto", description="Parsing strategy: 'auto', 'fast', or 'hi_res'")


class IngestionResponse(BaseModel):
    """Response model for document ingestion"""
    filename: str = Field(..., description="Ingested filename")
    status: str = Field(..., description="Ingestion status: 'success' or 'failed'")
    num_tables: int = Field(..., description="Number of tables extracted")
    num_chunks: int = Field(..., description="Number of text chunks created")
    message: str = Field(..., description="Status message or error details")


# ============================================================================
# System Status Models
# ============================================================================

class ServiceStatus(BaseModel):
    """Individual service status"""
    name: str = Field(..., description="Service name")
    status: str = Field(..., description="Status: 'ok', 'error', or 'warning'")
    message: Optional[str] = Field(None, description="Status message or error details")


class SystemStatusResponse(BaseModel):
    """Response model for system status"""
    overall_status: str = Field(..., description="Overall system status")
    services: List[ServiceStatus] = Field(..., description="Individual service statuses")
    timestamp: str = Field(..., description="ISO format response timestamp")


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str = Field("healthy", description="Health status: 'healthy' or 'unhealthy'")
    message: str = Field(..., description="Status message")
    timestamp: str = Field(..., description="ISO format response timestamp")


# ============================================================================
# Error Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error type or message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    request_id: Optional[str] = Field(None, description="Request tracking ID")


# ============================================================================
# Cache Statistics Models
# ============================================================================

class CacheStatsResponse(BaseModel):
    """Response model for cache statistics"""
    cache_enabled: bool = Field(..., description="Whether caching is enabled")
    total_entries: int = Field(..., description="Total entries in cache")
    hit_rate: float = Field(..., description="Cache hit rate (0-1)")
    memory_usage_bytes: Optional[int] = Field(None, description="Approximate memory usage")
    last_cleared: Optional[str] = Field(None, description="ISO format timestamp of last cache clear")

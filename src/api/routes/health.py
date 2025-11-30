"""Health check and status endpoints"""

import logging
from datetime import datetime
from fastapi import APIRouter, status

from src.api.cache import get_cache
from src.api.schemas import HealthResponse, SystemStatusResponse, ServiceStatus, CacheStatsResponse
from src.database.db_connectors import MongoConnector, QdrantConnector

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthResponse:
    """Check if the service is healthy"""
    try:
        # Check MongoDB
        mongo = MongoConnector()
        mongo.client.admin.command("ping")

        # Check Qdrant
        qdrant = QdrantConnector()
        qdrant.client.get_collections()

        return HealthResponse(
            status="healthy",
            message="All services are operational",
            timestamp=datetime.utcnow().isoformat() + "Z",
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            message=f"Service error: {str(e)}",
            timestamp=datetime.utcnow().isoformat() + "Z",
        )


@router.get("/api/status", response_model=SystemStatusResponse, status_code=status.HTTP_200_OK)
async def system_status() -> SystemStatusResponse:
    """Get detailed system status"""
    services = []

    # Check MongoDB
    try:
        mongo = MongoConnector()
        mongo.client.admin.command("ping")
        services.append(ServiceStatus(
            name="MongoDB",
            status="ok",
            message="Connected and operational",
        ))
    except Exception as e:
        logger.error(f"MongoDB check failed: {e}")
        services.append(ServiceStatus(
            name="MongoDB",
            status="error",
            message=str(e),
        ))

    # Check Qdrant
    try:
        qdrant = QdrantConnector()
        qdrant.client.get_collections()
        services.append(ServiceStatus(
            name="Qdrant",
            status="ok",
            message="Connected and operational",
        ))
    except Exception as e:
        logger.error(f"Qdrant check failed: {e}")
        services.append(ServiceStatus(
            name="Qdrant",
            status="error",
            message=str(e),
        ))

    # Check Cache
    try:
        cache = get_cache()
        cache_stats = cache.get_cache_stats()
        services.append(ServiceStatus(
            name="Cache",
            status="ok",
            message=f"Cache hit rate: {cache_stats['query_stats']['hit_rate']:.2%}",
        ))
    except Exception as e:
        logger.error(f"Cache check failed: {e}")
        services.append(ServiceStatus(
            name="Cache",
            status="warning",
            message=str(e),
        ))

    # Determine overall status
    statuses = [s.status for s in services]
    if "error" in statuses:
        overall = "degraded"
    elif "warning" in statuses:
        overall = "degraded"
    else:
        overall = "healthy"

    return SystemStatusResponse(
        overall_status=overall,
        services=services,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@router.get("/api/cache/stats", response_model=CacheStatsResponse, status_code=status.HTTP_200_OK)
async def cache_stats() -> CacheStatsResponse:
    """Get cache statistics"""
    try:
        cache = get_cache()
        stats = cache.get_cache_stats()

        return CacheStatsResponse(
            cache_enabled=True,
            total_entries=stats["backend"].get("total_entries", 0),
            hit_rate=stats["query_stats"]["hit_rate"],
            memory_usage_bytes=stats["backend"].get("memory_usage_bytes"),
            last_cleared=stats["last_cleared"],
        )
    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        return CacheStatsResponse(
            cache_enabled=False,
            total_entries=0,
            hit_rate=0.0,
        )

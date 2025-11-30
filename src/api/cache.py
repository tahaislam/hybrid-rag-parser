"""Caching layer for query optimization"""

import hashlib
import json
import time
import logging
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheBackend(ABC):
    """Abstract base class for cache implementations"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: int) -> bool:
        """Set value in cache with TTL"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache entries"""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        pass


class InMemoryCache(CacheBackend):
    """Simple in-memory cache implementation"""

    def __init__(self, max_entries: int = 1000):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_entries = max_entries
        self.hits = 0
        self.misses = 0
        self.created_at = datetime.now()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache, checking expiration"""
        if key not in self.cache:
            self.misses += 1
            return None

        entry = self.cache[key]
        if entry["expires_at"] and entry["expires_at"] < time.time():
            del self.cache[key]
            self.misses += 1
            return None

        self.hits += 1
        return entry["value"]

    def set(self, key: str, value: Any, ttl_seconds: int) -> bool:
        """Set value in cache"""
        if len(self.cache) >= self.max_entries:
            # Simple eviction: remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["created_at"])
            del self.cache[oldest_key]
            logger.warning(f"Cache full, evicted oldest entry: {oldest_key}")

        self.cache[key] = {
            "value": value,
            "created_at": time.time(),
            "expires_at": time.time() + ttl_seconds if ttl_seconds > 0 else None,
        }
        return True

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self) -> bool:
        """Clear all cache entries"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0

        return {
            "type": "in_memory",
            "total_entries": len(self.cache),
            "max_entries": self.max_entries,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "created_at": self.created_at.isoformat(),
        }


class RedisCache(CacheBackend):
    """Redis-backed cache implementation"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            self.available = True
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis cache initialization failed: {e}. Falling back to in-memory cache.")
            self.available = False

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        if not self.available:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl_seconds: int) -> bool:
        """Set value in Redis with TTL"""
        if not self.available:
            return False

        try:
            self.redis_client.setex(key, ttl_seconds, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if not self.available:
            return False

        try:
            return self.redis_client.delete(key) > 0
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

    def clear(self) -> bool:
        """Clear all Redis entries"""
        if not self.available:
            return False

        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get Redis statistics"""
        if not self.available:
            return {"type": "redis", "available": False}

        try:
            info = self.redis_client.info()
            return {
                "type": "redis",
                "available": True,
                "total_entries": self.redis_client.dbsize(),
                "memory_usage_bytes": info.get("used_memory", 0),
                "connected_clients": info.get("connected_clients", 0),
            }
        except Exception as e:
            logger.error(f"Redis stats error: {e}")
            return {"type": "redis", "available": False, "error": str(e)}


class QueryCache:
    """High-level cache manager for query operations"""

    def __init__(self, ttl_seconds: int = 3600, redis_url: Optional[str] = None):
        self.ttl_seconds = ttl_seconds
        self.query_hits = 0
        self.query_misses = 0
        self.embedding_cache: Dict[str, Any] = {}
        self.last_cleared = datetime.now()

        # Initialize cache backend
        if redis_url and REDIS_AVAILABLE:
            self.backend: CacheBackend = RedisCache(redis_url)
            if not self.backend.available:
                self.backend = InMemoryCache()
        else:
            self.backend = InMemoryCache()

    def _make_key(self, cache_type: str, value: str) -> str:
        """Generate cache key"""
        hash_value = hashlib.md5(value.encode()).hexdigest()
        return f"{cache_type}:{hash_value}"

    def get_query_cache(self, question: str, file_filter: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get cached query result"""
        cache_key = self._make_key("query", f"{question}:{file_filter}")
        result = self.backend.get(cache_key)
        if result:
            self.query_hits += 1
            logger.debug(f"Query cache hit for: {question[:50]}...")
            return result
        self.query_misses += 1
        return None

    def set_query_cache(self, question: str, result: Dict[str, Any], file_filter: Optional[str] = None) -> bool:
        """Cache query result"""
        cache_key = self._make_key("query", f"{question}:{file_filter}")
        return self.backend.set(cache_key, result, self.ttl_seconds)

    def get_embedding_cache(self, text: str) -> Optional[list]:
        """Get cached embedding"""
        cache_key = self._make_key("embedding", text)
        return self.embedding_cache.get(cache_key)

    def set_embedding_cache(self, text: str, embedding: list) -> bool:
        """Cache embedding"""
        cache_key = self._make_key("embedding", text)
        self.embedding_cache[cache_key] = embedding
        return True

    def clear_query_cache(self) -> bool:
        """Clear all query cache"""
        result = self.backend.clear()
        if result:
            self.last_cleared = datetime.now()
        return result

    def clear_embedding_cache(self) -> bool:
        """Clear embedding cache"""
        self.embedding_cache.clear()
        return True

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        backend_stats = self.backend.get_stats()
        total_requests = self.query_hits + self.query_misses
        query_hit_rate = self.query_hits / total_requests if total_requests > 0 else 0

        return {
            "cache_enabled": True,
            "backend": backend_stats,
            "query_stats": {
                "hits": self.query_hits,
                "misses": self.query_misses,
                "hit_rate": query_hit_rate,
            },
            "embedding_cache_entries": len(self.embedding_cache),
            "last_cleared": self.last_cleared.isoformat(),
        }


# Global cache instance
_query_cache: Optional[QueryCache] = None


def init_cache(ttl_seconds: int = 3600, redis_url: Optional[str] = None) -> QueryCache:
    """Initialize global cache instance"""
    global _query_cache
    _query_cache = QueryCache(ttl_seconds=ttl_seconds, redis_url=redis_url)
    return _query_cache


def get_cache() -> QueryCache:
    """Get global cache instance"""
    global _query_cache
    if _query_cache is None:
        _query_cache = QueryCache()
    return _query_cache

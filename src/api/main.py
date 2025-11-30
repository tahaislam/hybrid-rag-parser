"""FastAPI application factory and setup"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from src.api.config import config
from src.api.cache import init_cache
from src.api.routes import health, query, documents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    # Startup
    logger.info("Starting Hybrid RAG Parser API")
    init_cache(
        ttl_seconds=config.CACHE_TTL_SECONDS,
        redis_url=config.REDIS_URL,
    )
    logger.info("Cache initialized")

    yield

    # Shutdown
    logger.info("Shutting down Hybrid RAG Parser API")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title="Hybrid RAG Parser API",
        description="REST API for Retrieval-Augmented Generation with table-aware parsing",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure based on your needs
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(exc) if config.DEBUG else "An error occurred",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        )

    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info(f"{request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"{request.method} {request.url.path} - {response.status_code}")
        return response

    # Include routers
    app.include_router(health.router)
    app.include_router(query.router)
    app.include_router(documents.router)

    # Custom OpenAPI schema
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="Hybrid RAG Parser API",
            version="1.0.0",
            description="REST API for Retrieval-Augmented Generation with table-aware parsing",
            routes=app.routes,
        )

        openapi_schema["info"]["x-logo"] = {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
        }

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Hybrid RAG Parser API",
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc",
        }

    logger.info("FastAPI application created successfully")
    return app


# Create app instance for ASGI servers
app = create_app()

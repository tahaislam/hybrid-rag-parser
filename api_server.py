#!/usr/bin/env python
"""
Entry point for running the Hybrid RAG Parser API server

Usage:
    python api_server.py                # Start with default settings
    python api_server.py --host 0.0.0.0 --port 8000  # Custom host/port
    python api_server.py --reload       # Development mode with hot reload

Environment Variables:
    API_HOST: Server host (default: 0.0.0.0)
    API_PORT: Server port (default: 8000)
    DEBUG: Enable debug mode (default: False)
    REDIS_URL: Redis connection URL for caching (optional)
    CACHE_TTL_SECONDS: Cache TTL in seconds (default: 3600)
"""

import argparse
import os
import sys
import logging

try:
    import uvicorn
except ImportError:
    print("Error: uvicorn is not installed. Install it with:")
    print("    pip install uvicorn[standard]")
    sys.exit(1)

from src.api.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Run the API server"""
    parser = argparse.ArgumentParser(
        description="Hybrid RAG Parser API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--host",
        type=str,
        default=config.HOST,
        help=f"Server host (default: {config.HOST})",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=config.PORT,
        help=f"Server port (default: {config.PORT})",
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload mode for development",
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["critical", "error", "warning", "info", "debug"],
        default="info",
        help="Logging level (default: info)",
    )

    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("Hybrid RAG Parser API Server")
    logger.info("=" * 70)
    logger.info(f"Host: {args.host}")
    logger.info(f"Port: {args.port}")
    logger.info(f"Reload: {args.reload}")
    logger.info(f"Workers: {args.workers}")
    logger.info(f"Log Level: {args.log_level.upper()}")
    logger.info(f"Cache Enabled: {config.CACHE_ENABLED}")
    if config.REDIS_URL:
        logger.info(f"Redis URL: {config.REDIS_URL}")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Server starting at:")
    logger.info(f"  http://{args.host}:{args.port}")
    logger.info("")
    logger.info("Documentation available at:")
    logger.info(f"  http://{args.host}:{args.port}/docs (Swagger UI)")
    logger.info(f"  http://{args.host}:{args.port}/redoc (ReDoc)")
    logger.info("")

    # Run server
    uvicorn.run(
        "src.api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else 1,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    main()

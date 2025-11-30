"""Python client for the Hybrid RAG Parser API"""

import requests
from typing import Optional, List, Dict, Any
from pathlib import Path

from src.api.schemas import QueryResponse, VectorSearchResponse, TableSearchResponse


class RAGClient:
    """Client for interacting with the Hybrid RAG Parser API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the client"""
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def system_status(self) -> Dict[str, Any]:
        """Get detailed system status"""
        response = self.session.get(f"{self.base_url}/api/status")
        response.raise_for_status()
        return response.json()

    def query(
        self,
        question: str,
        file_filter: Optional[str] = None,
        debug: bool = False,
    ) -> QueryResponse:
        """Execute a hybrid RAG query"""
        payload = {
            "question": question,
            "file_filter": file_filter,
            "debug": debug,
        }
        response = self.session.post(
            f"{self.base_url}/api/query",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return QueryResponse(**data)

    def search_vectors(self, query: str, limit: int = 3) -> VectorSearchResponse:
        """Search vectors semantically"""
        payload = {
            "query": query,
            "limit": limit,
        }
        response = self.session.post(
            f"{self.base_url}/api/search/vectors",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return VectorSearchResponse(**data)

    def search_tables(
        self,
        query: str,
        file_filter: Optional[str] = None,
        limit: int = 5,
    ) -> TableSearchResponse:
        """Search tables"""
        payload = {
            "query": query,
            "file_filter": file_filter,
            "limit": limit,
        }
        response = self.session.post(
            f"{self.base_url}/api/search/tables",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return TableSearchResponse(**data)

    def list_documents(self) -> Dict[str, Any]:
        """List all ingested documents"""
        response = self.session.get(f"{self.base_url}/api/documents")
        response.raise_for_status()
        return response.json()

    def ingest_document(
        self,
        file_path: str,
        parse_strategy: str = "auto",
    ) -> Dict[str, Any]:
        """Ingest a PDF document"""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "application/pdf")}
            data = {"parse_strategy": parse_strategy}
            response = self.session.post(
                f"{self.base_url}/api/ingest",
                files=files,
                data=data,
            )
            response.raise_for_status()
            return response.json()

    def delete_document(self, filename: str) -> Dict[str, Any]:
        """Delete a document"""
        response = self.session.delete(f"{self.base_url}/api/documents/{filename}")
        response.raise_for_status()
        return response.json()

    def clear_database(self) -> Dict[str, Any]:
        """Clear all database data"""
        response = self.session.post(f"{self.base_url}/api/clear-db")
        response.raise_for_status()
        return response.json()

    def clear_cache(self) -> Dict[str, Any]:
        """Clear query cache"""
        response = self.session.post(f"{self.base_url}/api/cache/clear")
        response.raise_for_status()
        return response.json()

    def cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        response = self.session.get(f"{self.base_url}/api/cache/stats")
        response.raise_for_status()
        return response.json()

    def close(self):
        """Close the session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

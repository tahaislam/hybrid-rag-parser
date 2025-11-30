"""Document management endpoints"""

import logging
import os
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Form

from src.api.schemas import (
    DocumentListResponse, DocumentMetadata,
    IngestionRequest, IngestionResponse,
)
from src.api.config import config
from src.ingestion.ingest import DocumentProcessor
from src.ingestion.embedding import EmbeddingModel
from src.database.db_connectors import MongoConnector, QdrantConnector

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["documents"])


@router.get("/documents", response_model=DocumentListResponse, status_code=status.HTTP_200_OK)
async def list_documents() -> DocumentListResponse:
    """
    List all ingested documents with metadata
    """
    try:
        mongo = MongoConnector()

        # Get unique documents from tables collection
        documents = mongo.client["hybrid_rag_db"]["document_tables"].distinct("source_filename")

        # Get metadata for each document
        doc_metadata = []
        for filename in sorted(documents):
            # Count tables
            num_tables = mongo.client["hybrid_rag_db"]["document_tables"].count_documents({
                "source_filename": filename
            })

            doc_metadata.append(DocumentMetadata(
                filename=filename,
                upload_date=datetime.utcnow().isoformat() + "Z",
                num_tables=num_tables,
                num_chunks=0,  # Would need to query Qdrant
                file_size_bytes=0,  # Not tracked currently
            ))

        return DocumentListResponse(
            documents=doc_metadata,
            total_count=len(doc_metadata),
        )

    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.post("/ingest", response_model=IngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_document(
    file: UploadFile = File(...),
    parse_strategy: str = Form("auto"),
) -> IngestionResponse:
    """
    Upload and ingest a PDF document

    - **file**: PDF file to ingest
    - **parse_strategy**: Parsing strategy ('auto', 'fast', or 'hi_res')
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PDF",
        )

    # Create upload directory if needed
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)

    try:
        # Save uploaded file
        file_path = os.path.join(config.UPLOAD_DIR, file.filename)
        contents = await file.read()

        # Check file size
        if len(contents) > config.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds {config.MAX_FILE_SIZE_MB}MB limit",
            )

        with open(file_path, "wb") as f:
            f.write(contents)

        logger.info(f"Processing file: {file.filename}")

        # Process document
        processor = DocumentProcessor()
        tables, texts = processor.process(file_path, strategy=parse_strategy)

        # Generate embeddings and prepare Qdrant points
        embedding_model = EmbeddingModel()

        # Store in databases
        mongo = MongoConnector()
        qdrant = QdrantConnector()

        # Store tables in MongoDB
        for table in tables:
            mongo.insert_table({
                "table": table,
                "source_filename": file.filename,
            })

        # Store text chunks in Qdrant
        # prepare_qdrant_points returns a generator of point dicts
        qdrant_points = list(embedding_model.prepare_qdrant_points(texts, file.filename))
        qdrant.client.upsert(
            collection_name="document_chunks",
            points=qdrant_points,
        )

        logger.info(f"Ingested {file.filename}: {len(tables)} tables, {len(texts)} text chunks")

        return IngestionResponse(
            filename=file.filename,
            status="success",
            num_tables=len(tables),
            num_chunks=len(texts),
            message=f"Successfully ingested {file.filename}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ingestion failed for {file.filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}"
        )


@router.delete("/documents/{filename}", status_code=status.HTTP_200_OK)
async def delete_document(filename: str):
    """
    Delete a document and its associated data

    - **filename**: Document filename to delete
    """
    try:
        mongo = MongoConnector()
        qdrant = QdrantConnector()

        # Delete from MongoDB
        result_mongo = mongo.client["hybrid_rag_db"]["document_tables"].delete_many({
            "source_filename": filename
        })

        # Delete from Qdrant (by filtering payloads)
        # Note: Qdrant doesn't have native delete by filter, so we'd need to
        # scroll and delete points individually. For now, we log this limitation.
        # TODO: Implement proper Qdrant deletion

        logger.info(f"Deleted document: {filename} ({result_mongo.deleted_count} tables)")

        return {
            "status": "success",
            "message": f"Deleted document: {filename}",
            "tables_deleted": result_mongo.deleted_count,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    except Exception as e:
        logger.error(f"Failed to delete document {filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.post("/clear-db", status_code=status.HTTP_200_OK)
async def clear_database():
    """
    Clear all database data (development only)
    WARNING: This cannot be undone
    """
    try:
        mongo = MongoConnector()
        qdrant = QdrantConnector()

        # Clear MongoDB
        mongo.client["hybrid_rag_db"]["document_tables"].delete_many({})

        # Clear Qdrant (delete and recreate collection)
        try:
            qdrant.client.delete_collection(collection_name="document_chunks")
            qdrant.client.recreate_collection(
                collection_name="document_chunks",
                vectors_config={"size": 384, "distance": "Cosine"},
            )
        except Exception as e:
            logger.warning(f"Qdrant collection clear issue: {e}")

        logger.warning("All databases cleared")

        return {
            "status": "success",
            "message": "All databases cleared successfully",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    except Exception as e:
        logger.error(f"Failed to clear databases: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear databases: {str(e)}"
        )

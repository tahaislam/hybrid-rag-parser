"""
db_connectors.py
Contains classes for connecting to and interacting with
MongoDB and Qdrant databases.
"""

from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any, Iterable

class MongoConnector:
    """
    Manages connection and data insertion for MongoDB.
    Fabric-Ready: This logic can be swapped for a Cosmos DB (Mongo API) client.
    """
    def __init__(self, db_name: str = "hybrid_rag_db"):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client[db_name]
        self.collection = self.db["document_tables"]
        print(f"Connected to MongoDB. Database: '{db_name}', Collection: 'document_tables'")

    def insert_tables(self, tables_data: List[Dict[str, Any]], source_filename: str):
        """
        Inserts a list of table records into MongoDB.
        Adds a 'source_filename' to each record for traceability.
        """
        if not tables_data:
            return

        for table in tables_data:
            table['source_filename'] = source_filename
            
        result = self.collection.insert_many(tables_data)
        print(f"Inserted {len(result.inserted_ids)} tables into MongoDB for {source_filename}.")

class QdrantConnector:
    """
    Manages connection and data insertion for Qdrant.
    Fabric-Ready: This logic can be swapped for Fabric Real-Time Intelligence (KQL).
    """
    def __init__(self, collection_name: str = "document_chunks"):
        self.client = QdrantClient("localhost", port=6333)
        self.collection_name = collection_name
        print(f"Connected to Qdrant. Collection: '{collection_name}'")

    def setup_collection(self, vector_size: int):
        """
        Creates or updates the Qdrant collection with the correct vector size.
        """
        try:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            print(f"Qdrant collection '{self.collection_name}' created/recreated.")
        except Exception as e:
            print(f"Error setting up Qdrant collection: {e}")

    def insert_vectors(self, points: Iterable[Dict[str, Any]]):
        """
        Upserts (inserts or updates) vector points into Qdrant.
        
        Args:
            points: An iterable of Qdrant PointStructs (as dictionaries).
        """
        # Convert dicts to PointStruct objects
        qdrant_points = [
            PointStruct(id=p["id"], vector=p["vector"], payload=p["payload"])
            for p in points
        ]
        
        if not qdrant_points:
            return

        self.client.upsert(
            collection_name=self.collection_name,
            points=qdrant_points,
            wait=True # Wait for the operation to complete
        )
        print(f"Inserted {len(qdrant_points)} vector points into Qdrant.")
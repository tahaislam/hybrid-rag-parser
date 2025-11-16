"""
embedding.py
Handles the conversion of text chunks into vector embeddings.
"""

from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Generator
import uuid

class EmbeddingModel:
    """
    A wrapper class for the sentence-transformer embedding model.
    
    This is designed to be swappable. In a Fabric environment,
    this could be replaced with a call to an Azure ML endpoint.
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initializes the embedding model.
        
        Args:
            model_name: The name of the model from Hugging Face.
                        'all-MiniLM-L6-v2' is a great, fast, open-source
                        default that produces 384-dimensional vectors.
        """
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        # Search results confirm 'all-MiniLM-L6-v2' produces 384-dimensional vectors
        self.vector_size = 384 
        print("Embedding model loaded.")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embeds a list of text strings.
        
        Args:
            texts: A list of text strings to embed.
            
        Returns:
            A list of vector embeddings.
        """
        embeddings_array = self.model.encode(texts)
        return embeddings_array.tolist()

    def prepare_qdrant_points(
        self, 
        texts: List[str], 
        source_filename: str
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Generates Qdrant PointStructs (dictionaries) from text chunks.
        This combines embedding and metadata preparation.
        
        Args:
            texts: The list of text chunks.
            source_filename: The name of the file these texts came from.
            
        Yields:
            Dictionaries formatted for Qdrant (id, vector, payload).
        """
        print(f"Generating {len(texts)} vector points for Qdrant...")
        embeddings = self.embed_texts(texts)
        
        for i, (text, vector) in enumerate(zip(texts, embeddings)):
            yield {
                "id": str(uuid.uuid4()),
                "vector": vector,
                "payload": {
                    "text": text,
                    "source_filename": source_filename,
                    "chunk_index": i
                }
            }
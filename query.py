"""
query.py
Handles the RAG (Retrieval-Augmented Generation) query process.

THIS VERSION USES A LOCAL, 100% PRIVATE OLLAMA MODEL.
"""

from db_connectors import MongoConnector, QdrantConnector
from embedding import EmbeddingModel
from ollama import Client
from typing import List, Dict, Any

class QueryEngine:
    def __init__(self):
        print("Initializing Query Engine...")
        self.mongo = MongoConnector()
        self.qdrant = QdrantConnector(collection_name="document_chunks")
        self.embedder = EmbeddingModel()
        
        # Connect to local Ollama server
        try:
            self.llm_client = Client(host='http://localhost:11434')
            self.llm_model = 'llama3:8b' # Or 'mistral', etc.
            # Check if the server is running
            self.llm_client.list() 
            print(f"Connected to Ollama. Using model: {self.llm_model}")
        except Exception as e:
            print("="*50)
            print("OLLAMA CONNECTION FAILED")
            print("Please make sure the Ollama application is running on your machine.")
            print(f"Error: {e}")
            print("="*50)
            raise
        
    def search_vectors(self, question: str) -> List[Dict[str, Any]]:
        """Searches Qdrant for text chunks semantically related to the question."""
        print(f"Searching vectors for: '{question}'")
        
        question_vector = self.embedder.embed_texts([question])[0]
        
        search_results = self.qdrant.client.search(
            collection_name=self.qdrant.collection_name,
            query_vector=question_vector,
            limit=3
        )
        
        context_chunks = [result.payload for result in search_results]
        print(f"Found {len(context_chunks)} relevant text chunks.")
        return context_chunks

    def search_tables(self, question: str, file_filter: str = None) -> List[Dict[str, Any]]:
        """Searches MongoDB for tables."""
        print("Searching tables in MongoDB...")
        query_filter = {}
        if file_filter:
            query_filter["source_filename"] = file_filter
            
        results = self.mongo.collection.find(query_filter).limit(5)
        
        table_context = list(results)
        
        for table in table_context:
            table.pop('_id', None)
            
        print(f"Found {len(table_context)} relevant tables.")
        return table_context

    def ask(self, question: str):
        """
        Main RAG query function.
        """
        vector_context = self.search_vectors(question)
        table_context = self.search_tables(question) 

        # 2. Build the LLM Prompt
        prompt = f"""
        You are an expert assistant for answering questions about complex documents.
        You will be given context from two sources:
        1. RELEVANT TEXT CHUNKS: (Semantically similar text from the documents)
        2. RELEVANT TABLES: (Structured tables from the documents, in HTML format)

        Your task is to answer the user's question based *only* on this provided context.
        If the answer is not found in the context, say "I could not find the answer in the provided documents."

        ---
        CONTEXT 1: RELEVANT TEXT CHUNKS
        ---
        {vector_context}

        ---
        CONTEXT 2: RELEVANT TABLES
        ---
        {table_context}

        ---
        USER QUESTION:
        ---
        {question}

        ---
        YOUR ANSWER:
        """
        
        # 3. Augment & Generate (Send to LLM)
        print("\nSynthesizing answer with local LLM (Ollama)...")
        try:
            # --- CHANGED: Use the Ollama API syntax ---
            response = self.llm_client.chat(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "You are a helpful document assistant that only uses provided context."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            answer = response['message']['content']
            return answer
            
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return "There was an error generating the answer."
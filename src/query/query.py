"""
query.py
Handles the RAG (Retrieval-Augmented Generation) query process.

THIS VERSION USES A LOCAL, 100% PRIVATE OLLAMA MODEL.
"""

from src.database.db_connectors import MongoConnector, QdrantConnector
from src.ingestion.embedding import EmbeddingModel
from ollama import Client
from typing import List, Dict, Any
from html.parser import HTMLParser
import re

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

    def html_table_to_markdown(self, html_content: str) -> str:
        """Convert HTML table to markdown format for better LLM parsing."""
        try:
            # Remove extra whitespace
            html_content = re.sub(r'\s+', ' ', html_content.strip())

            # Extract table rows
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html_content, re.IGNORECASE | re.DOTALL)

            if not rows:
                return html_content

            markdown_lines = []
            for i, row in enumerate(rows):
                # Extract cells (both td and th)
                cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row, re.IGNORECASE | re.DOTALL)
                # Clean cell content
                cells = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]

                # Create markdown row
                markdown_lines.append('| ' + ' | '.join(cells) + ' |')

                # Add header separator after first row
                if i == 0:
                    markdown_lines.append('| ' + ' | '.join(['---'] * len(cells)) + ' |')

            return '\n'.join(markdown_lines)
        except Exception as e:
            # If parsing fails, return original content
            return html_content

    def format_text_context(self, vector_context: List[Dict[str, Any]]) -> str:
        """Format text chunks for the LLM prompt."""
        if not vector_context:
            return "No relevant text chunks found."

        formatted_chunks = []
        for i, chunk in enumerate(vector_context, 1):
            text = chunk.get('text', '')
            source = chunk.get('source_filename', 'unknown')
            formatted_chunks.append(f"[Chunk {i} from {source}]\n{text}")

        return '\n\n'.join(formatted_chunks)

    def format_table_context(self, table_context: List[Dict[str, Any]]) -> str:
        """Format tables for the LLM prompt, converting HTML to markdown."""
        if not table_context:
            return "No relevant tables found."

        formatted_tables = []
        for i, table in enumerate(table_context, 1):
            content = table.get('content', '')
            content_type = table.get('content_type', 'unknown')
            source = table.get('source_filename', 'unknown')
            table_id = table.get('table_id', f'table_{i}')

            # Convert HTML tables to markdown
            if content_type == 'html' and '<table' in content.lower():
                content = self.html_table_to_markdown(content)

            formatted_tables.append(f"[Table {i} - {table_id} from {source}]\n{content}")

        return '\n\n'.join(formatted_tables)

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

    def ask(self, question: str, debug: bool = False):
        """
        Main RAG query function.

        Args:
            question: The question to ask
            debug: If True, prints the formatted context sent to the LLM
        """
        
        # 1. Retrieve Vector Context
        vector_context = self.search_vectors(question)
        
        # 2. Implement "Smart Retrieval"
        # Get the source file from the *most relevant* text chunk.
        source_file = None
        if vector_context:
            # The first result (index 0) is the most relevant one
            source_file = vector_context[0].get('source_filename')
            if source_file:
                print(f"Vector search identified: '{source_file}' as the most relevant document.")
            else:
                print("Vector search found chunks, but no source_filename metadata.")
        else:
            print("Vector search found no relevant text chunks.")

        # 3. Retrieve Table Context
        # Now, only search for tables from that *specific file* (if found).
        table_context = self.search_tables(question, file_filter=source_file)

        # 4. Format the context for the LLM
        formatted_text = self.format_text_context(vector_context)
        formatted_tables = self.format_table_context(table_context)

        # Debug output if requested
        if debug:
            print("\n" + "="*70)
            print("DEBUG: Formatted context being sent to LLM")
            print("="*70)
            print("\nFORMATTED TEXT CHUNKS:")
            print(formatted_text)
            print("\nFORMATTED TABLES:")
            print(formatted_tables)
            print("="*70 + "\n")

        # 5. Build the LLM Prompt with properly formatted context
        prompt = f"""You are an expert assistant for answering questions about complex documents.
You will be given context from two sources:
1. RELEVANT TEXT CHUNKS: Semantically similar text from the documents
2. RELEVANT TABLES: Structured tables from the documents in markdown format

Your task is to answer the user's question based *only* on this provided context.
- Read the tables carefully, paying attention to row and column headers
- Look for values at the intersection of relevant row and column headers
- If the answer is not found in the context, say "I could not find the answer in the provided documents."
- Be precise and cite specific values when answering from tables

---
CONTEXT 1: RELEVANT TEXT CHUNKS
---
{formatted_text}

---
CONTEXT 2: RELEVANT TABLES
---
{formatted_tables}

---
USER QUESTION:
---
{question}

---
YOUR ANSWER:
"""

        # 6. Send to LLM for answer generation
        print("\nSynthesizing answer with local LLM (Ollama)...")
        try:
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
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
    # Temperature presets for different use cases
    TEMPERATURE_DETERMINISTIC = 0.0  # Factual Q&A, testing, production consistency
    TEMPERATURE_BALANCED = 0.3       # Slight variation while staying factual
    TEMPERATURE_CREATIVE = 0.8       # Creative writing, brainstorming

    def __init__(self, temperature: float = None):
        """
        Initialize the Query Engine.

        Args:
            temperature: LLM temperature (0.0-1.0). Controls randomness in responses.
                        - None (default): Uses TEMPERATURE_DETERMINISTIC (0.0)
                        - 0.0: Deterministic - same input always gives same output
                        - 0.3: Balanced - slight variation while staying factual
                        - 0.8: Creative - diverse outputs for creative tasks
                        You can also use the class constants:
                        - QueryEngine.TEMPERATURE_DETERMINISTIC
                        - QueryEngine.TEMPERATURE_BALANCED
                        - QueryEngine.TEMPERATURE_CREATIVE
        """
        print("Initializing Query Engine...")
        self.mongo = MongoConnector()
        self.qdrant = QdrantConnector(collection_name="document_chunks")
        self.embedder = EmbeddingModel()

        # Set temperature (default to deterministic for consistent results)
        self.temperature = temperature if temperature is not None else self.TEMPERATURE_DETERMINISTIC
        print(f"LLM Temperature: {self.temperature} ({'Deterministic' if self.temperature == 0.0 else 'Balanced' if self.temperature <= 0.5 else 'Creative'})")

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

CRITICAL INSTRUCTIONS:

1. DOCUMENT CONTEXT MATTERS:
   - If a document is titled "Quarterly Financial Report - Q4 2023", then ALL data in that document (including tables) is from Q4 2023
   - If a document is titled "Annual Report 2023", then ALL data in it is from 2023
   - The document title, headers, and surrounding text provide temporal and contextual information for ALL data in that document
   - When answering about "Q4" or specific time periods, check if the document title indicates this time period

2. TABLE READING - READ EVERY SINGLE ROW:
   - Read EVERY row in the table from top to bottom, including the FIRST row after the header
   - When a table has a header row (like "| Phase | Duration | Start Date | End Date |"), the data rows come IMMEDIATELY after
   - The FIRST data row is just as important as any other row - DO NOT SKIP IT
   - Example: If you see "| Phase | ... |" followed by "| Requirements | ... |", then "Requirements" is the FIRST phase
   - Count the rows mentally: 1st row, 2nd row, 3rd row, etc. Include ALL of them

3. LISTING VALUES FROM A COLUMN:
   - When asked to "list all X" where X is a column name, extract EVERY value from that column
   - Start from the first data row and go to the last data row
   - Do not skip any rows in between
   - Example: If asked "list all phases" and the Phase column has 5 rows, list all 5 values

4. COMPLETE LISTS:
   - When listing items from a table, include ALL rows, not just some of them
   - Do not skip the first data row or any other rows
   - If the user asks for a list, provide the COMPLETE list from the table

5. PRECISION:
   - Be precise and cite specific values when answering from tables
   - If the answer is not found in the context, say "I could not find the answer in the provided documents."

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
                ],
                options={
                    "temperature": self.temperature,  # Use configured temperature
                    "top_p": 1.0                      # Disable nucleus sampling for consistency
                }
            )
            
            answer = response['message']['content']
            return answer
            
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return "There was an error generating the answer."


# Usage Examples
if __name__ == "__main__":
    """
    Example usage demonstrating different temperature settings.
    """
    print("="*80)
    print("QueryEngine Temperature Examples")
    print("="*80)

    # Example 1: Deterministic mode (default) - for testing and production
    print("\n1. DETERMINISTIC MODE (temperature=0.0)")
    print("   Use for: Testing, production queries, consistent results")
    print("-"*80)
    engine_deterministic = QueryEngine()  # Default is deterministic
    # Or explicitly: engine = QueryEngine(temperature=QueryEngine.TEMPERATURE_DETERMINISTIC)

    # Example 2: Balanced mode - for general use with slight variation
    print("\n2. BALANCED MODE (temperature=0.3)")
    print("   Use for: General queries with slight variation")
    print("-"*80)
    engine_balanced = QueryEngine(temperature=QueryEngine.TEMPERATURE_BALANCED)

    # Example 3: Creative mode - for brainstorming and diverse outputs
    print("\n3. CREATIVE MODE (temperature=0.8)")
    print("   Use for: Creative writing, brainstorming, diverse perspectives")
    print("-"*80)
    engine_creative = QueryEngine(temperature=QueryEngine.TEMPERATURE_CREATIVE)

    # Example 4: Custom temperature
    print("\n4. CUSTOM TEMPERATURE")
    print("   Use any value between 0.0 and 1.0")
    print("-"*80)
    engine_custom = QueryEngine(temperature=0.5)

    print("\n" + "="*80)
    print("Temperature Guide:")
    print("  0.0       = Deterministic (same input → same output)")
    print("  0.1-0.3   = Minimal variation (factual with slight diversity)")
    print("  0.4-0.6   = Moderate variation (balanced creativity)")
    print("  0.7-1.0   = High variation (creative, diverse outputs)")
    print("="*80)
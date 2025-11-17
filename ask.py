"""
ask.py
A command-line interface to ask questions to your RAG pipeline.

Usage:
python ask.py "Your question here"
"""

import sys
from query import QueryEngine

def main():
    if len(sys.argv) < 2:
        print("Usage: python ask.py \"Your question here\"")
        sys.exit(1)

    question = sys.argv[1]
    
    # Initialize the engine (this will load models)
    engine = QueryEngine()
    
    # Ask the question
    answer = engine.ask(question)
    
    print("\n" + "="*50 + " ANSWER " + "="*50)
    print(answer)
    print("="*108)

if __name__ == "__main__":
    main()
"""
ask.py
A command-line interface to ask questions to your RAG pipeline.

Usage:
python ask.py "Your question here"
python ask.py "Your question here" --debug  # Show formatted context
"""

import sys
from query import QueryEngine

def main():
    if len(sys.argv) < 2:
        print("Usage: python ask.py \"Your question here\" [--debug]")
        print("  --debug: Show the formatted context sent to the LLM")
        sys.exit(1)

    question = sys.argv[1]
    debug = "--debug" in sys.argv

    # Initialize the engine (this will load models)
    engine = QueryEngine()

    # Ask the question
    answer = engine.ask(question, debug=debug)

    print("\n" + "="*50 + " ANSWER " + "="*50)
    print(answer)
    print("="*108)

if __name__ == "__main__":
    main()
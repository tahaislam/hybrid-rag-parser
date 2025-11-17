#!/usr/bin/env python3
"""
Convenience wrapper for tests/test_rag_queries.py
This allows running the script from the root directory.
"""
if __name__ == "__main__":
    import runpy
    runpy.run_module("tests.test_rag_queries", run_name="__main__")

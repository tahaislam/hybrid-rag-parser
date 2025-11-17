#!/usr/bin/env python3
"""
Convenience wrapper for tests/generate_sample_pdfs.py
This allows running the script from the root directory.
"""
if __name__ == "__main__":
    import runpy
    runpy.run_module("tests.generate_sample_pdfs", run_name="__main__")

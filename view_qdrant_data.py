#!/usr/bin/env python3
"""
Convenience wrapper for src/utils/view_qdrant_data.py
This allows running the script from the root directory.
"""
if __name__ == "__main__":
    import runpy
    runpy.run_module("src.utils.view_qdrant_data", run_name="__main__")

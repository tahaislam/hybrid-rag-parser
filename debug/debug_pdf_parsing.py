#!/usr/bin/env python3
"""
Debug script to check what was actually extracted from financial_report.pdf
"""
from src.ingestion.ingest import DocumentProcessor
import os

pdf_path = "data/financial_report.pdf"

if not os.path.exists(pdf_path):
    print(f"ERROR: {pdf_path} not found!")
    print("Please run: python generate_sample_pdfs.py first")
    exit(1)

print(f"Processing {pdf_path}...")
print("="*80)

processor = DocumentProcessor()
tables, texts = processor.process_pdf(pdf_path)

print(f"\nFound {len(tables)} tables and {len(texts)} text chunks\n")

# Show all tables
for i, table in enumerate(tables, 1):
    print(f"\nTABLE {i}")
    print("="*80)
    print(f"Table ID: {table.get('table_id')}")
    print(f"Content Type: {table.get('content_type')}")
    print(f"Page: {table.get('metadata', {}).get('page_number', 'Unknown')}")

    content = table.get('content', '')
    print(f"\nContent Length: {len(content)} characters")

    if len(content) > 0:
        print("\nContent Preview (first 800 chars):")
        print("-"*80)
        print(content[:800])
        print("-"*80)
    else:
        print("\n⚠️  WARNING: This table has NO CONTENT!")
    print("="*80)

# Show text chunks
print("\n\nTEXT CHUNKS:")
print("="*80)
for i, text in enumerate(texts[:3], 1):  # Show first 3 chunks
    print(f"\nChunk {i}:")
    print(text[:300])
    print("...")

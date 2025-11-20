#!/usr/bin/env python3
"""
Debug the failing tests to see if it's vector search or table extraction
"""
from src.ingestion.ingest import DocumentProcessor
import os

pdfs_to_check = [
    ("data/research_results.pdf", "XGBoost", "40,000"),
    ("data/sales_report.pdf", "Marcus Schmidt", ""),
    ("data/project_budget.pdf", "Requirements", "Testing"),
]

processor = DocumentProcessor()

for pdf_path, keyword1, keyword2 in pdfs_to_check:
    if not os.path.exists(pdf_path):
        print(f"❌ {pdf_path} not found - run: python generate_sample_pdfs.py")
        continue

    print("\n" + "="*80)
    print(f"CHECKING: {pdf_path}")
    print("="*80)

    tables, texts = processor.process_pdf(pdf_path)

    print(f"\n📊 Found {len(tables)} tables, {len(texts)} text chunks")

    # Check if keywords are in tables
    for i, table in enumerate(tables, 1):
        content = table.get('content', '')
        found_items = []
        if keyword1 and keyword1 in content:
            found_items.append(keyword1)
        if keyword2 and keyword2 in content:
            found_items.append(keyword2)

        if found_items:
            print(f"\n✓ Table {i}: Found {found_items}")
            print(f"  Content preview: {content[:300]}...")
        else:
            print(f"\n⚠️  Table {i}: Missing expected keywords")
            if keyword1:
                print(f"  Looking for: '{keyword1}' - {'FOUND' if keyword1 in content else '❌ NOT FOUND'}")
            if keyword2:
                print(f"  Looking for: '{keyword2}' - {'FOUND' if keyword2 in content else '❌ NOT FOUND'}")
            print(f"  Content preview: {content[:300]}...")

    # Check if keywords are in text chunks
    text_found = []
    for text in texts:
        if keyword1 and keyword1 in text:
            text_found.append(keyword1)
        if keyword2 and keyword2 in text:
            text_found.append(keyword2)

    if text_found:
        print(f"\n✓ Text chunks contain: {set(text_found)}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("If keywords are NOT FOUND in tables, it's a table extraction issue.")
print("If keywords ARE FOUND in tables, it's a vector search issue.")

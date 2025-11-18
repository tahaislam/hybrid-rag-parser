#!/usr/bin/env python3
"""
Comprehensive test for financial_report.pdf table parsing
"""
import os
from src.ingestion.ingest import DocumentProcessor

print("="*80)
print("FINANCIAL REPORT PDF - TABLE PARSING TEST")
print("="*80)

pdf_path = "data/financial_report.pdf"

# Check if PDF exists
if not os.path.exists(pdf_path):
    print(f"\n❌ ERROR: {pdf_path} not found!")
    print("Run: python generate_sample_pdfs.py")
    exit(1)

print(f"\n✓ PDF found: {pdf_path}")
print(f"  Size: {os.path.getsize(pdf_path)} bytes")

# Parse the PDF
print("\n" + "-"*80)
print("PARSING PDF...")
print("-"*80)

processor = DocumentProcessor()
tables, texts = processor.process_pdf(pdf_path, strategy="auto")

print(f"\n📊 Extraction Results:")
print(f"   Tables: {len(tables)}")
print(f"   Text chunks: {len(texts)}")

# Analyze each table
print("\n" + "="*80)
print("TABLE ANALYSIS")
print("="*80)

expected_tables = [
    {
        'name': 'Revenue by Product Line',
        'should_contain': ['Cloud Services', '$950,000', 'Q4 2023']
    },
    {
        'name': 'Operating Expenses Breakdown',
        'should_contain': ['Marketing & Sales', '$380,000', 'Salaries']
    }
]

if len(tables) == 0:
    print("\n❌ CRITICAL: NO TABLES EXTRACTED!")
    print("   This means the PDF parsing failed completely.")
    print("\n   Possible causes:")
    print("   1. PDF is corrupted")
    print("   2. Tables are rendered as images")
    print("   3. unstructured library configuration issue")
else:
    for i, table in enumerate(tables, 1):
        print(f"\n--- TABLE {i} ---")
        print(f"Table ID: {table.get('table_id')}")
        print(f"Content Type: {table.get('content_type')}")
        print(f"Page: {table.get('metadata', {}).get('page_number', 'Unknown')}")

        content = table.get('content', '')
        print(f"Content Length: {len(content)} chars")

        if len(content) == 0:
            print("\n❌ EMPTY TABLE - NO CONTENT EXTRACTED!")
        else:
            print(f"\n✓ Content extracted ({len(content)} characters)")

            # Check if expected content is present
            if i <= len(expected_tables):
                expected = expected_tables[i-1]
                print(f"\nExpected table: {expected['name']}")
                print("Checking for key content:")

                found_all = True
                for key_text in expected['should_contain']:
                    if key_text in content:
                        print(f"  ✓ Found: '{key_text}'")
                    else:
                        print(f"  ❌ Missing: '{key_text}'")
                        found_all = False

                if found_all:
                    print(f"\n✓ Table {i} appears to be correctly parsed!")
                else:
                    print(f"\n⚠️  Table {i} is missing expected content")

            # Show preview
            print(f"\nContent Preview (first 500 chars):")
            print("-"*80)
            print(content[:500])
            if len(content) > 500:
                print("...")
            print("-"*80)

# Analyze text chunks
print("\n" + "="*80)
print("TEXT CHUNK ANALYSIS")
print("="*80)

revenue_mentioned = False
cloud_services_mentioned = False

for i, text in enumerate(texts[:5], 1):
    if 'revenue' in text.lower():
        revenue_mentioned = True
    if 'cloud services' in text.lower():
        cloud_services_mentioned = True

    print(f"\nChunk {i} ({len(text)} chars):")
    print(text[:200])
    if len(text) > 200:
        print("...")

print("\n" + "-"*80)
print("SUMMARY")
print("-"*80)

if len(tables) >= 2:
    print("✓ Expected number of tables found (2)")
else:
    print(f"⚠️  Found {len(tables)} tables, expected 2")

if revenue_mentioned:
    print("✓ 'Revenue' mentioned in text chunks")

if cloud_services_mentioned:
    print("✓ 'Cloud Services' mentioned in text chunks")
    print("  → This might mean table was parsed as text instead of table")

print("\n" + "="*80)
print("RECOMMENDATION")
print("="*80)

if len(tables) == 0:
    print("❌ No tables extracted - PDF generation or parsing failed")
    print("   Try regenerating: python generate_sample_pdfs.py")
elif len(tables) < 2:
    print("⚠️  Only one table extracted")
    print("   First table might be:")
    print("   1. Parsed as regular text (check text chunks)")
    print("   2. In wrong format (image-based)")
    print("   3. Too complex for unstructured library")
elif any(len(t.get('content', '')) == 0 for t in tables):
    print("⚠️  Some tables are empty")
    print("   This is a parsing issue, not generation")
    print("   Try different strategy: strategy='fast' or 'hi_res'")
else:
    print("✓ All tables appear to be extracted correctly")
    print("  If queries still fail, the issue is in:")
    print("  1. HTML→Markdown conversion")
    print("  2. LLM prompt/understanding")

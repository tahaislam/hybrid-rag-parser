#!/usr/bin/env python3
"""
Debug script to view the actual table content stored in MongoDB
"""
from src.database.db_connectors import MongoConnector

mongo = MongoConnector()

# Get all tables from financial_report.pdf
tables = list(mongo.collection.find({"source_filename": "financial_report.pdf"}))

print(f"\nFound {len(tables)} tables from financial_report.pdf\n")
print("="*80)

for i, table in enumerate(tables, 1):
    print(f"\nTABLE {i}")
    print("="*80)
    print(f"Table ID: {table.get('table_id')}")
    print(f"Content Type: {table.get('content_type')}")
    print(f"\nContent Preview (first 500 chars):")
    print("-"*80)
    content = table.get('content', '')
    print(content[:500])
    print("-"*80)
    print(f"\nFull Content Length: {len(content)} characters")
    print("="*80)

# Debug Scripts

This directory contains diagnostic and debugging scripts for troubleshooting the RAG system.

## Available Scripts

### 📊 `debug_database_content.py`
**Purpose**: Inspect what's actually stored in MongoDB and Qdrant databases

**Use when**:
- Verifying data was ingested correctly
- Checking if tables are stored with correct format
- Debugging retrieval issues

**Usage**:
```bash
python debug/debug_database_content.py
```

---

### 🧪 `debug_failing_tests.py`
**Purpose**: Debug specific failing test cases by checking if data exists in databases

**Use when**:
- Tests are failing and you need to verify data presence
- Checking if specific keywords are in tables or text chunks
- Isolating whether issue is data extraction or retrieval

**Usage**:
```bash
python debug/debug_failing_tests.py
```

---

### 📄 `debug_pdf_parsing.py`
**Purpose**: Debug PDF parsing and table extraction at the source

**Use when**:
- Tables aren't being extracted correctly
- Need to see raw output from unstructured library
- Troubleshooting PDF-specific parsing issues

**Usage**:
```bash
python debug/debug_pdf_parsing.py
```

---

### 📋 `debug_tables.py`
**Purpose**: Quick check of table content stored in MongoDB for a specific document

**Use when**:
- Need to see exact table content in database
- Verifying HTML table format is correct
- Quick check without full database dump

**Usage**:
```bash
python debug/debug_tables.py
```

**Example output**:
```
Found 2 tables from financial_report.pdf
Table 1 (table_3): <table><thead>...
Has Requirements: True
```

---

### 🔍 `debug_vector_search.py`
**Purpose**: Debug vector search and embedding similarity

**Use when**:
- Questions aren't retrieving relevant documents
- Need to check embedding quality
- Debugging vector similarity scores

**Usage**:
```bash
python debug/debug_vector_search.py
```

---

## When to Use These Scripts

### Common Debugging Workflow

1. **Test fails** → Run `debug_failing_tests.py` to verify data exists
2. **Data missing** → Run `debug_pdf_parsing.py` to check extraction
3. **Data exists but not retrieved** → Run `debug_vector_search.py` to check embeddings
4. **Need full picture** → Run `debug_database_content.py` for complete dump

### Quick Checks

```bash
# Check if specific table data exists
python debug/debug_tables.py

# See full database contents
python debug/debug_database_content.py

# Check vector search for a query
python debug/debug_vector_search.py
```

---

## Notes

- These scripts are **diagnostic tools** for development/debugging
- They are **not required** for normal operation
- They connect to the same databases as the main application
- Make sure Docker containers are running before using these scripts

---

## Related Documentation

- [RAG_IMPROVEMENTS.md](../RAG_IMPROVEMENTS.md) - Details on RAG system fixes
- [README.md](../README.md) - Main project documentation
- [TESTING.md](../TESTING.md) - Testing guide (if exists)

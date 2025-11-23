# Testing Guide for Hybrid RAG Parser

This guide explains how to generate sample data and test the RAG query system comprehensively.

## Overview

The testing suite includes:
- **5 diverse sample PDF files** with different table structures
- **20 comprehensive test cases** covering various query patterns
- **Automated validation** of expected answers
- **Performance metrics** for response times

## Quick Start

### 1. Generate Sample PDFs

First, install the PDF generation dependency:

```bash
pip install reportlab
```

Then generate the sample PDFs:

```bash
python generate_sample_pdfs.py
```

This creates 5 PDFs in the `data/` directory:
- `project_budget.pdf` - Software development budget and timeline
- `financial_report.pdf` - Quarterly revenue and expenses
- `research_results.pdf` - ML model performance comparison
- `product_specs.pdf` - Server hardware specifications
- `sales_report.pdf` - Regional sales data

### 2. Ingest the Sample Data

Process and store the PDFs in the databases:

```bash
python run_pipeline.py
```

This will:
- Extract tables and text from all PDFs
- Store tables in MongoDB
- Generate embeddings and store in Qdrant

### 3. Run the Test Suite

Execute the comprehensive test suite:

```bash
python test_rag_queries.py
```

For debug output (see formatted context sent to LLM):

```bash
python test_rag_queries.py --debug
```

## Sample PDFs Content

### 1. project_budget.pdf
**Purpose:** Test budget and timeline queries

**Tables:**
- Project Budget Breakdown (tasks, hours, rates, costs)
- Project Timeline (phases, durations, dates)

**Sample Questions:**
- "What is the estimated hours for software development?" → 160
- "What is the total project budget?" → $50,400
- "When does the development phase end?" → 2024-04-22

### 2. financial_report.pdf
**Purpose:** Test financial data queries

**Tables:**
- Revenue by Product Line (Q3/Q4 comparison)
- Operating Expenses Breakdown

**Sample Questions:**
- "What was the Q4 2023 revenue for Cloud Services?" → $950,000
- "What was the revenue growth percentage for Enterprise Software?" → 16.7%
- "How much was spent on Marketing & Sales?" → $380,000

### 3. research_results.pdf
**Purpose:** Test scientific/research data queries

**Tables:**
- Model Performance Comparison (accuracy, precision, recall, F1)
- Dataset Characteristics

**Sample Questions:**
- "Which machine learning model had the highest accuracy?" → Random Forest, 94.2%
- "What was the F1 score of XGBoost?" → 93.6%
- "How many samples were in the training set?" → 40,000

### 4. product_specs.pdf
**Purpose:** Test technical specification queries

**Tables:**
- Hardware Specifications
- Performance Benchmarks

**Sample Questions:**
- "What processor does the CloudServer Pro X500 use?" → Dual Intel Xeon Gold 6348
- "How much RAM does the X500 have?" → 512 GB
- "What is the storage IOPS for the X500?" → 2,500,000

### 5. sales_report.pdf
**Purpose:** Test regional and performance data queries

**Tables:**
- Sales by Region (quarterly breakdown)
- Top Sales Representatives

**Sample Questions:**
- "What were the total sales for Asia-Pacific in 2023?" → $4.7M
- "What were North America Q4 sales?" → $1.5M
- "Who was the top sales representative?" → Sarah Johnson, $2,100,000

## Test Cases Overview

The test suite includes 20 test cases covering:

### Simple Lookups (Tests 1-6)
- Single value extraction from table cells
- Row/column intersection queries
- Total and subtotal lookups

### Identification Queries (Tests 7, 15)
- Finding best performers or maximum values
- Identifying entities based on criteria

### Metric Extraction (Tests 8-12, 16)
- Extracting specific performance metrics
- Retrieving calculated values
- Hardware specifications

### Regional/Categorical Data (Tests 13-14)
- Regional totals and breakdowns
- Quarterly comparisons

### Complex Queries (Tests 17-20)
- Multi-value extractions
- Comparison between entities
- Summary queries across multiple rows

## Expected Test Results

All tests include expected answer validation. A test passes if:
- The answer contains the expected keywords/values
- Response time is reasonable (typically < 30 seconds)

Example passing test:
```
TEST: Simple Table Lookup - Single Value
QUESTION: What is the estimated hours for software development?
ANSWER: Based on the project budget table, the estimated hours for software development is 160 hours.
✓ PASSED: Answer contains expected content
Time taken: 5.23 seconds
```

## Interpreting Test Results

The test suite provides:

1. **Individual Test Results**
   - Pass/Fail status for each test
   - Response time per query
   - Full answer for manual verification

2. **Summary Statistics**
   - Total tests run
   - Pass/fail counts
   - Average response time

3. **Detailed Failure Analysis**
   - Questions that failed
   - Expected vs actual answers
   - Debugging suggestions

## Manual Testing

You can also test individual queries manually:

```bash
# Basic query
python ask.py "What is the total project budget?"

# With debug output
python ask.py "What is the total project budget?" --debug

# Python API
python -c "
from query import QueryEngine
engine = QueryEngine()
answer = engine.ask('What is the total project budget?')
print(answer)
"
```

## Troubleshooting Test Failures

### Common Issues

**1. Answer not found / "I could not find the answer"**
- Check if PDFs were ingested: `python view_qdrant_data.py stats`
- Verify tables are in MongoDB: Visit http://localhost:8081
- Run with `--debug` to see what context is being sent to LLM

**2. Wrong values extracted**
- The LLM may be reading the wrong table cell
- Check table formatting with `--debug`
- Verify markdown conversion is working correctly

**3. Slow response times**
- First query loads Ollama model (slow)
- Subsequent queries use cached model (faster)
- Consider using smaller/faster model: `mistral` or `llama2`

**4. Connection errors**
- Ensure Ollama is running: `curl http://localhost:11434/api/tags`
- Verify databases are running: `docker ps`
- Check model is pulled: `ollama list`

### Debugging Steps

1. **Verify data ingestion:**
   ```bash
   python view_qdrant_data.py stats
   # Should show 5 PDFs processed
   ```

2. **Check specific document:**
   ```bash
   python view_qdrant_data.py view project_budget.pdf
   ```

3. **Test with debug mode:**
   ```bash
   python ask.py "Your question" --debug
   # Shows formatted tables and context
   ```

4. **Check MongoDB tables:**
   - Visit http://localhost:8081
   - Login: admin / pass
   - Navigate to: hybrid_rag_db → document_tables
   - Verify tables are properly formatted

## Performance Benchmarks

Expected performance on a typical system:

| Metric | Target | Typical Range |
|--------|--------|---------------|
| Average response time | < 10s | 3-15s |
| First query (cold start) | < 30s | 10-30s |
| Subsequent queries | < 8s | 2-10s |
| Test suite total time | < 5min | 2-8min |

*Note: Performance depends on hardware, Ollama model size, and system load*

## Customizing Tests

You can add your own test cases to `test_rag_queries.py`:

```python
# Add to the run_all_tests() method
self.run_test(
    question="Your custom question?",
    expected_answer_contains=["keyword1", "keyword2"],
    test_name="Your Test Name"
)
```

## Next Steps

After successful testing:
1. Use the RAG system with your own PDFs
2. Adjust query parameters in `query.py` for better accuracy
3. Experiment with different Ollama models
4. Build a web interface or API on top of the query engine

## Support

If tests consistently fail:
1. Check the troubleshooting section above
2. Review the main README.md for setup instructions
3. Ensure all prerequisites are met (Docker, Ollama, Python packages)
4. Run `python check_setup.py` to verify installation

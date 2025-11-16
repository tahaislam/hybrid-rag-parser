# Hybrid RAG Parser

A table-aware document ingestion pipeline for Retrieval-Augmented Generation (RAG) systems that intelligently separates narrative text from structured tables.

## Overview

This project provides a smart document processing system that:
- Extracts tables and narrative text separately from PDF documents
- Prepares tables for storage in NoSQL databases (exact lookups)
- Prepares text for vector databases (semantic search)
- Supports migration to Microsoft Fabric (Real-Time Intelligence/Cosmos DB)

## Architecture

```
PDF Document
    ↓
Document Parser
    ↓
    ├──> 📊 Tables → NoSQL Database (MongoDB/Cosmos DB)
    └──> 📝 Text → Vector Database (Qdrant/Fabric)
```

## Features

- **Smart Table Detection**: Automatically identifies and extracts tables from PDFs
- **Multiple Parsing Strategies**: Choose between 'auto', 'fast', or 'hi_res' for different accuracy/speed tradeoffs
- **Flexible Output Formats**: Extract tables as HTML or plain text
- **Batch Processing**: Process entire directories of PDFs at once
- **Detailed Metadata**: Capture page numbers, coordinates, and file information
- **Migration Ready**: Designed for easy migration to Microsoft Fabric

## Requirements

**Python Version**: 3.9, 3.10, or 3.11 (3.12+ is NOT supported)

### System Dependencies

For Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libmagic1
```

For macOS:
```bash
brew install poppler tesseract libmagic
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hybrid-rag-parser
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python check_setup.py
   ```

## Quick Start

### Process a Single PDF

```python
from ingest import process_single_pdf

# Process a PDF file
tables, texts = process_single_pdf("data/sample1.pdf")

print(f"Extracted {len(tables)} tables")
print(f"Extracted {len(texts)} text chunks")
```

### Process All PDFs in a Directory

```python
from ingest import process_directory

# Process all PDFs in the data folder
results = process_directory("data/")

for filename, (tables, texts) in results.items():
    print(f"{filename}: {len(tables)} tables, {len(texts)} text chunks")
```

### Run from Command Line

```bash
# Process all PDFs in data/ directory
python ingest.py

# Process a specific PDF
python ingest.py path/to/your/document.pdf
```

## Viewing Parsed Content

### Option 1: Run Example Scripts

The project includes comprehensive examples:

```bash
# Run all examples
python example_usage.py
```

This will show you:
- How to process single files
- How to batch process directories
- How to customize parsing settings
- How to prepare data for database storage

### Option 2: Access Parsed Data Programmatically

```python
from ingest import process_single_pdf

# Process a PDF
tables, texts = process_single_pdf("data/sample1.pdf")

# View table data
for i, table in enumerate(tables):
    print(f"\nTable {i+1}:")
    print(f"  ID: {table['table_id']}")
    print(f"  Page: {table['metadata']['page_number']}")
    print(f"  Format: {table['content_type']}")
    print(f"  Content:\n{table['content']}")

# View text chunks
for i, text in enumerate(texts):
    print(f"\nText Chunk {i+1}:")
    print(f"  {text}")
```

### Option 3: Save Output to Files

```python
import json
from ingest import process_single_pdf

tables, texts = process_single_pdf("data/sample1.pdf")

# Save tables as JSON
with open("output_tables.json", "w") as f:
    json.dump(tables, indent=2, fp=f)

# Save text chunks
with open("output_texts.txt", "w") as f:
    for i, text in enumerate(texts, 1):
        f.write(f"=== Text Chunk {i} ===\n")
        f.write(text + "\n\n")

print("Results saved to output_tables.json and output_texts.txt")
```

## Understanding the Output

### Table Structure

Each table is returned as a dictionary with:

```python
{
    "table_id": "table_0",           # Unique identifier
    "content": "<table>...</table>", # Table content (HTML or text)
    "content_type": "html",          # Format: "html" or "text"
    "metadata": {
        "page_number": 1,            # Page where table appears
        "filename": "sample.pdf",    # Source file
        "file_directory": "data/",   # Source directory
        "coordinates": {...},        # Position on page
        "parent_id": "..."          # Document hierarchy
    }
}
```

### Text Chunks

Text is returned as a list of strings, with each string representing a coherent text segment:

```python
[
    "This is the document introduction...",
    "Section 1: Overview of the project...",
    "Key findings include...",
    ...
]
```

## Parsing Strategies

The parser supports three strategies:

| Strategy | Speed | Accuracy | Requirements |
|----------|-------|----------|--------------|
| `auto` | Fast | Good | Basic (default) |
| `fast` | Fastest | Good | Basic |
| `hi_res` | Slow | Best | Requires layoutparser* |

*Note: `hi_res` strategy has dependency conflicts. The `auto` and `fast` strategies work well for most use cases.

### Choosing a Strategy

```python
from ingest import DocumentProcessor

processor = DocumentProcessor()

# Default: Good balance
tables, texts = processor.process_pdf("file.pdf", strategy="auto")

# Fast processing
tables, texts = processor.process_pdf("file.pdf", strategy="fast")

# Best accuracy (may fail without layoutparser)
tables, texts = processor.process_pdf("file.pdf", strategy="hi_res")
```

## Project Structure

```
hybrid-rag-parser/
├── ingest.py              # Main document processing module
├── example_usage.py       # Comprehensive usage examples
├── check_setup.py         # Installation verification script
├── requirements.txt       # Python dependencies
├── requirements-minimal.txt  # Minimal dependencies
├── requirements-lite.txt     # Lightweight option
├── SETUP.md              # Detailed setup instructions
├── data/                 # Sample PDF files
│   ├── sample1.pdf
│   ├── sample2.pdf
│   └── sample3.pdf
└── README.md            # This file
```

## Next Steps

### Phase 1: Local Development (Current)
- [x] PDF parsing and table extraction
- [x] Text/table separation
- [ ] MongoDB integration for table storage
- [ ] Qdrant integration for vector embeddings
- [ ] Basic query interface

### Phase 2: Microsoft Fabric Migration
- [ ] Migrate to Cosmos DB for table storage
- [ ] Migrate to Fabric Real-Time Intelligence for vectors
- [ ] Implement hybrid query system
- [ ] Add production monitoring

## Troubleshooting

### Python Version Issues

If you see errors about Python version:

```bash
# Check your Python version
python --version

# Install Python 3.11 using pyenv
pyenv install 3.11.9
pyenv local 3.11.9

# Or use conda
conda create -n rag-pipeline python=3.11
conda activate rag-pipeline
```

### Missing System Dependencies

If you see errors about `poppler` or `tesseract`:

```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils tesseract-ocr libmagic1

# macOS
brew install poppler tesseract libmagic
```

### Import Errors

If you get `ModuleNotFoundError`:

```bash
# Ensure you're in the virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Empty Results

If no tables or text are extracted:
1. Check that your PDF contains actual text (not just images)
2. Try a different parsing strategy (`auto`, `fast`, or `hi_res`)
3. Verify the PDF isn't password-protected or corrupted

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions:
- Check the [SETUP.md](SETUP.md) file for detailed setup instructions
- Review the [example_usage.py](example_usage.py) for code examples
- Run `python check_setup.py` to verify your installation

## Acknowledgments

Built with:
- [unstructured.io](https://unstructured.io/) - Document parsing
- [pdf2image](https://github.com/Belval/pdf2image) - PDF processing
- [Tesseract](https://github.com/tesseract-ocr/tesseract) - OCR capabilities

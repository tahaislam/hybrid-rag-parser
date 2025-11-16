# Hybrid RAG Parser

A complete end-to-end table-aware document ingestion pipeline for Retrieval-Augmented Generation (RAG) systems that intelligently separates narrative text from structured tables and stores them in specialized databases.

## Overview

This project provides a production-ready document processing system that:
- Extracts tables and narrative text separately from PDF documents
- Stores tables in MongoDB (NoSQL) for exact lookups and structured queries
- Generates embeddings and stores text in Qdrant (Vector DB) for semantic search
- Provides a complete orchestration pipeline with Docker containerization
- Supports migration to Microsoft Fabric (Real-Time Intelligence/Cosmos DB)

## Architecture

```
PDF Document
    ↓
Document Parser (ingest.py)
    ├──> 📊 Tables → MongoDB (localhost:27017)
    │                  └─> Web UI: Mongo Express (localhost:8081)
    │
    └──> 📝 Text → Embeddings (embedding.py)
                      └─> sentence-transformers (384-dim vectors)
                          └─> Qdrant Vector DB (localhost:6333)
                               └─> Web UI (localhost:6334)

Orchestration: run_pipeline.py
Databases: docker-compose.yml
```

## Features

- **Smart Table Detection**: Automatically identifies and extracts tables from PDFs
- **Multiple Parsing Strategies**: Choose between 'auto', 'fast', or 'hi_res' for different accuracy/speed tradeoffs
- **Flexible Output Formats**: Extract tables as HTML or plain text
- **Batch Processing**: Process entire directories of PDFs at once
- **Vector Embeddings**: Convert text to 384-dimensional vectors using sentence-transformers
- **Dual Database Storage**: MongoDB for structured tables, Qdrant for vector search
- **Web UIs**: Visual interfaces for MongoDB (Mongo Express) and Qdrant
- **Docker Containerization**: One-command database setup
- **Full Pipeline Orchestration**: End-to-end processing with `run_pipeline.py`
- **Detailed Metadata**: Capture page numbers, coordinates, and file information
- **Migration Ready**: Designed for easy migration to Microsoft Fabric

## Requirements

**Python Version**: 3.9, 3.10, or 3.11 (3.12+ is NOT supported)

**Docker**: Required for running MongoDB and Qdrant databases

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

### Docker Installation

If you don't have Docker installed:
- **Ubuntu/Debian**: [Install Docker Engine](https://docs.docker.com/engine/install/ubuntu/)
- **macOS**: [Install Docker Desktop](https://docs.docker.com/desktop/install/mac-install/)
- **Windows**: [Install Docker Desktop](https://docs.docker.com/desktop/install/windows-install/)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd hybrid-rag-parser
```

### 2. Set Up Python Environment
```bash
# Create a virtual environment (recommended)
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python check_setup.py
```

### 3. Start the Databases with Docker
```bash
# Start MongoDB and Qdrant containers
docker-compose up -d

# Verify containers are running
docker ps
```

You should see three containers running:
- `hybrid-rag-mongo` - MongoDB database (port 27017)
- `hybrid-rag-qdrant` - Qdrant vector database (ports 6333, 6334)
- `hybrid-rag-mongo-express` - MongoDB web UI (port 8081)

### 4. Access the Web UIs (Optional)

- **MongoDB Web UI (Mongo Express)**: http://localhost:8081
  - Login Username: `admin`
  - Login Password: `pass`
  - Navigate to `hybrid_rag_db` → `document_tables` to view tables

- **Qdrant Web UI**: http://localhost:6334
  - No login required
  - View collections and vector points
  - Explore embeddings and metadata

## Quick Start

### Option 1: Run the Full Pipeline (Recommended)

Process all PDFs and store everything in databases:

```bash
python run_pipeline.py
```

This will:
1. Load all PDFs from the `data/` directory
2. Extract tables and text from each PDF
3. Store tables in MongoDB
4. Generate embeddings and store text vectors in Qdrant
5. Display progress for each file

### Option 2: Process Documents Without Database Storage

#### Process a Single PDF

```python
from ingest import process_single_pdf

# Process a PDF file
tables, texts = process_single_pdf("data/sample1.pdf")

print(f"Extracted {len(tables)} tables")
print(f"Extracted {len(texts)} text chunks")
```

#### Process All PDFs in a Directory

```python
from ingest import process_directory

# Process all PDFs in the data folder
results = process_directory("data/")

for filename, (tables, texts) in results.items():
    print(f"{filename}: {len(tables)} tables, {len(texts)} text chunks")
```

#### Run from Command Line

```bash
# Process all PDFs in data/ directory
python ingest.py

# Process a specific PDF
python ingest.py path/to/your/document.pdf
```

## Viewing Stored Data

### Option 1: Using Web UIs (Easiest)

After running `run_pipeline.py`, view your data in the web interfaces:

**MongoDB (Tables)**
1. Open http://localhost:8081 in your browser
2. Login with username: `admin`, password: `pass`
3. Navigate to `hybrid_rag_db` → `document_tables`
4. Browse extracted tables with all metadata

**Qdrant (Vector Embeddings)**
1. Open http://localhost:6334 in your browser
2. Click on the `document_chunks` collection
3. Click on any point ID to view its details
4. **Important**: Look at the **"payload"** section to see the actual text
   - The "vector" field shows 384 numbers (embedding) - ignore this
   - The "payload" field contains: `text`, `source_filename`, `chunk_index`
5. Expand the payload to read the text content

**Note**: If the Qdrant UI is hard to read, use the helper script instead:
```bash
python view_qdrant_data.py
```

### Option 2: Use the Qdrant Data Viewer Script (Recommended)

For easier viewing of Qdrant data, use the included helper script:

```bash
# View collection statistics and recent points
python view_qdrant_data.py

# View all text chunks from a specific file
python view_qdrant_data.py view sample1.pdf

# Search for similar text
python view_qdrant_data.py search "payment terms"

# Show detailed statistics
python view_qdrant_data.py stats
```

This script displays the actual text content in a readable format, without the confusing vector numbers.

### Option 3: Query Databases Programmatically

#### Query MongoDB for Tables

```python
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://root:examplepassword@localhost:27017/")
db = client["hybrid_rag_db"]
collection = db["document_tables"]

# Find all tables from a specific file
tables = collection.find({"source_filename": "sample1.pdf"})

for table in tables:
    print(f"Table ID: {table['table_id']}")
    print(f"Page: {table['metadata']['page_number']}")
    print(f"Content: {table['content'][:100]}...")
    print()
```

#### Query Qdrant for Similar Text

```python
from qdrant_client import QdrantClient
from embedding import EmbeddingModel

# Initialize
client = QdrantClient("localhost", port=6333)
embedder = EmbeddingModel()

# Search for similar content
query = "What are the key findings?"
query_vector = embedder.embed_texts([query])[0]

results = client.search(
    collection_name="document_chunks",
    query_vector=query_vector,
    limit=5
)

for result in results:
    print(f"Score: {result.score}")
    print(f"Text: {result.payload['text']}")
    print(f"Source: {result.payload['source_filename']}")
    print()
```

## Viewing Parsed Content (Before Database Storage)

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
├── ingest.py                 # Main document processing module
├── embedding.py              # Text embedding and vector generation
├── db_connectors.py          # MongoDB and Qdrant database connectors
├── run_pipeline.py           # Main orchestration script (run this!)
├── view_qdrant_data.py       # Helper script to view Qdrant data easily
├── docker-compose.yml        # Database container configuration
├── example_usage.py          # Comprehensive usage examples
├── check_setup.py            # Installation verification script
├── requirements.txt          # Python dependencies (full version)
├── requirements-minimal.txt  # Minimal dependencies
├── requirements-lite.txt     # Lightweight option
├── SETUP.md                  # Detailed setup instructions
├── .gitignore                # Git ignore rules
├── data/                     # Sample PDF files
│   ├── sample1.pdf
│   ├── sample2.pdf
│   └── sample3.pdf
└── README.md                 # This file
```

## Module Descriptions

| Module | Purpose |
|--------|---------|
| `ingest.py` | PDF parsing, table/text extraction |
| `embedding.py` | Generate 384-dim vectors using sentence-transformers |
| `db_connectors.py` | MongoDB and Qdrant connection management |
| `run_pipeline.py` | **Main entry point** - orchestrates full pipeline |
| `view_qdrant_data.py` | **View & search** Qdrant data in readable format |
| `docker-compose.yml` | Spin up MongoDB, Qdrant, and Mongo Express |
| `example_usage.py` | Usage examples for document processing |
| `check_setup.py` | Verify Python dependencies are installed |

## Configuration

### Default Settings

The pipeline uses the following default configurations:

| Component | Setting | Value |
|-----------|---------|-------|
| MongoDB | Host | localhost:27017 |
| MongoDB | Database | hybrid_rag_db |
| MongoDB | Collection | document_tables |
| MongoDB | Credentials | root/examplepassword |
| Qdrant | Host | localhost:6333 |
| Qdrant | Collection | document_chunks |
| Qdrant | Distance Metric | Cosine |
| Embedding Model | Name | all-MiniLM-L6-v2 |
| Embedding Model | Vector Size | 384 |
| PDF Directory | Path | ./data |
| Parse Strategy | Default | auto |
| Mongo Express | Web UI Username | admin |
| Mongo Express | Web UI Password | pass |

### Customizing Settings

**Change MongoDB password:**
1. Edit `docker-compose.yml` (lines 14-15 and 36-37)
2. Edit `db_connectors.py` (line 18)
3. Restart containers: `docker-compose down && docker-compose up -d`

**Change embedding model:**
1. Edit `embedding.py` (line 17)
2. Update `vector_size` based on the new model
3. Note: Changing models requires recreating the Qdrant collection

**Change PDF directory:**
1. Edit `run_pipeline.py` (line 23)

**Change parsing strategy:**
1. Edit `run_pipeline.py` (line 59)
2. Options: `"auto"` (recommended), `"fast"`, `"hi_res"`
3. Note: `"auto"` provides the best balance of speed and table detection accuracy

## Pipeline Workflow

When you run `python run_pipeline.py`, here's what happens:

1. **Initialization**
   - Load sentence-transformer model (all-MiniLM-L6-v2)
   - Connect to MongoDB (table storage)
   - Connect to Qdrant (vector storage)
   - Create/recreate Qdrant collection with 384-dim vectors

2. **For Each PDF in data/**
   - Parse PDF and extract elements
   - Separate tables from narrative text
   - Store tables in MongoDB with metadata
   - Generate embeddings for text chunks
   - Store vectors in Qdrant with payloads

3. **Results**
   - All tables queryable in MongoDB
   - All text searchable via semantic similarity in Qdrant
   - Access via web UIs or programmatic queries

## Development Roadmap

### Phase 1: Local Development ✅ COMPLETE
- [x] PDF parsing and table extraction
- [x] Text/table separation
- [x] MongoDB integration for table storage
- [x] Qdrant integration for vector embeddings
- [x] Sentence-transformer embeddings (384-dim)
- [x] Docker containerization
- [x] Web UIs for data visualization
- [x] Full pipeline orchestration

### Phase 2: Query Interface (In Progress)
- [ ] Hybrid query API (combine table lookups + vector search)
- [ ] RESTful API endpoints
- [ ] Query optimization
- [ ] Caching layer

### Phase 3: Microsoft Fabric Migration (Planned)
- [ ] Migrate MongoDB → Cosmos DB (MongoDB API)
- [ ] Migrate Qdrant → Fabric Real-Time Intelligence (KQL)
- [ ] Update db_connectors.py for Fabric compatibility
- [ ] Azure ML endpoint for embeddings
- [ ] Production monitoring and logging

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

### Docker Issues

**Containers won't start:**
```bash
# Check if Docker is running
docker --version
docker ps

# View container logs
docker-compose logs

# Restart containers
docker-compose down
docker-compose up -d
```

**Port conflicts (address already in use):**
```bash
# Check which process is using the port
sudo lsof -i :27017  # MongoDB
sudo lsof -i :6333   # Qdrant
sudo lsof -i :8081   # Mongo Express

# Either stop the conflicting service or modify ports in docker-compose.yml
```

**Cannot connect to databases:**
```bash
# Ensure containers are running
docker ps

# Test MongoDB connection
docker exec -it hybrid-rag-mongo mongosh -u root -p examplepassword

# Check Qdrant health
curl http://localhost:6333/health
```

**Clear all data and restart:**
```bash
# Stop containers and remove volumes
docker-compose down -v

# Restart fresh
docker-compose up -d
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

### Database Connection Errors

If `run_pipeline.py` fails to connect:
1. Ensure Docker containers are running: `docker ps`
2. Check database credentials in `db_connectors.py` match `docker-compose.yml`
3. Wait a few seconds after starting containers for databases to initialize

### Qdrant UI Shows Weird Characters

If you see strange encoded text in the Qdrant web UI:

**The Problem:** You're looking at the "vector" field (384 floating-point numbers) instead of the actual text.

**The Solution:**
1. In the Qdrant UI, click on a point ID
2. Scroll down to the **"payload"** section
3. Expand the payload to see:
   - `text`: The actual readable text
   - `source_filename`: Which PDF it came from
   - `chunk_index`: Position in the document

**Better Option:** Use the helper script for easier viewing:
```bash
python view_qdrant_data.py
```

This displays the text in a clean, readable format without the vector numbers.

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
- [unstructured.io](https://unstructured.io/) - Document parsing and table extraction
- [pdf2image](https://github.com/Belval/pdf2image) - PDF processing
- [Tesseract](https://github.com/tesseract-ocr/tesseract) - OCR capabilities
- [sentence-transformers](https://www.sbert.net/) - Text embeddings (all-MiniLM-L6-v2)
- [MongoDB](https://www.mongodb.com/) - NoSQL database for table storage
- [Qdrant](https://qdrant.tech/) - Vector database for semantic search
- [Docker](https://www.docker.com/) - Containerization
- [Mongo Express](https://github.com/mongo-express/mongo-express) - MongoDB web interface

## Docker Management

### Useful Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart a specific service
docker-compose restart mongo

# Stop and remove all data (volumes)
docker-compose down -v

# View resource usage
docker stats
```

### Accessing Database Shells

```bash
# MongoDB shell
docker exec -it hybrid-rag-mongo mongosh -u root -p examplepassword

# Check Qdrant collections
curl http://localhost:6333/collections
```

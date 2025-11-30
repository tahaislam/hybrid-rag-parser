# Hybrid RAG Parser - REST API Documentation

This document describes the REST API for the Hybrid RAG Parser system.

## Quick Start

### 1. Start the API Server

```bash
# Install dependencies
pip install -r requirements.txt

# Start the API server
python api_server.py

# Or with custom settings:
python api_server.py --host 0.0.0.0 --port 8000 --reload

# Or using uvicorn directly:
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start Dependencies with Docker Compose

```bash
# Start all services (MongoDB, Qdrant, Redis, Mongo Express)
docker-compose up -d

# Start with API server in Docker (optional)
docker-compose up -d  # Starts all services
python api_server.py  # Or run API locally
```

### 3. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health & Status

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "All services are operational",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### System Status
```http
GET /api/status
```

**Response:**
```json
{
  "overall_status": "healthy",
  "services": [
    {
      "name": "MongoDB",
      "status": "ok",
      "message": "Connected and operational"
    },
    {
      "name": "Qdrant",
      "status": "ok",
      "message": "Connected and operational"
    },
    {
      "name": "Cache",
      "status": "ok",
      "message": "Cache hit rate: 45.32%"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Query Endpoints

#### Hybrid RAG Query
```http
POST /api/query
Content-Type: application/json

{
  "question": "What are the main findings?",
  "file_filter": "document.pdf",
  "debug": false
}
```

**Response:**
```json
{
  "answer": "The main findings indicate...",
  "sources": [
    {
      "type": "text",
      "filename": "document.pdf",
      "content": "..."
    },
    {
      "type": "table",
      "filename": "document.pdf",
      "content": "..."
    }
  ],
  "debug_info": null
}
```

#### Vector Search
```http
POST /api/search/vectors
Content-Type: application/json

{
  "query": "revenue analysis",
  "limit": 3
}
```

**Response:**
```json
{
  "results": [
    {
      "text": "Revenue increased by 25% year-over-year...",
      "filename": "q4_report.pdf",
      "score": 0.92,
      "metadata": {
        "source": "financial_data"
      }
    }
  ],
  "query_time_ms": 45.2
}
```

#### Table Search
```http
POST /api/search/tables
Content-Type: application/json

{
  "query": "quarterly metrics",
  "file_filter": null,
  "limit": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "table_data": "| Quarter | Revenue | Growth |\n|---------|---------|--------|\n| Q1 | $1M | 5% |",
      "filename": "financial_data.pdf",
      "table_index": 0,
      "metadata": {
        "source": "financial_tables"
      }
    }
  ],
  "query_time_ms": 32.5
}
```

### Document Management

#### List Documents
```http
GET /api/documents
```

**Response:**
```json
{
  "documents": [
    {
      "filename": "document.pdf",
      "upload_date": "2024-01-15T10:00:00Z",
      "num_tables": 5,
      "num_chunks": 120,
      "file_size_bytes": 2048576
    }
  ],
  "total_count": 1
}
```

#### Ingest Document
```http
POST /api/ingest
Content-Type: multipart/form-data

file: <binary PDF data>
parse_strategy: auto
```

**Response:**
```json
{
  "filename": "document.pdf",
  "status": "success",
  "num_tables": 5,
  "num_chunks": 120,
  "message": "Successfully ingested document.pdf"
}
```

#### Delete Document
```http
DELETE /api/documents/{filename}
```

**Response:**
```json
{
  "status": "success",
  "message": "Deleted document: document.pdf",
  "tables_deleted": 5,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Clear Database
```http
POST /api/clear-db
```

**Response:**
```json
{
  "status": "success",
  "message": "All databases cleared successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Cache Management

#### Clear Cache
```http
POST /api/cache/clear
```

**Response:**
```json
{
  "status": "success",
  "message": "Query cache cleared successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Cache Statistics
```http
GET /api/cache/stats
```

**Response:**
```json
{
  "cache_enabled": true,
  "total_entries": 25,
  "hit_rate": 0.6532,
  "memory_usage_bytes": 102400,
  "last_cleared": "2024-01-15T09:00:00Z"
}
```

## Usage Examples

### Python Client

```python
from src.api.client import RAGClient

# Initialize client
client = RAGClient(base_url="http://localhost:8000")

# Check health
health = client.health_check()
print(f"Status: {health['status']}")

# Execute a query
response = client.query("What are the main findings?")
print(f"Answer: {response.answer}")

# Search vectors
vector_results = client.search_vectors("revenue analysis")
print(f"Found {len(vector_results.results)} results")

# Search tables
table_results = client.search_tables("quarterly metrics")
print(f"Found {len(table_results.results)} tables")

# List documents
docs = client.list_documents()
print(f"Total documents: {docs['total_count']}")

# Ingest document
result = client.ingest_document("data/sample.pdf")
print(f"Ingestion status: {result['status']}")

# Close connection
client.close()
```

### cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# System status
curl http://localhost:8000/api/status

# Execute query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main findings?",
    "file_filter": null,
    "debug": false
  }'

# Vector search
curl -X POST http://localhost:8000/api/search/vectors \
  -H "Content-Type: application/json" \
  -d '{
    "query": "revenue analysis",
    "limit": 3
  }'

# Table search
curl -X POST http://localhost:8000/api/search/tables \
  -H "Content-Type: application/json" \
  -d '{
    "query": "quarterly metrics",
    "file_filter": null,
    "limit": 5
  }'

# List documents
curl http://localhost:8000/api/documents

# Ingest document
curl -X POST http://localhost:8000/api/ingest \
  -F "file=@data/sample.pdf" \
  -F "parse_strategy=auto"

# Delete document
curl -X DELETE http://localhost:8000/api/documents/sample.pdf

# Clear cache
curl -X POST http://localhost:8000/api/cache/clear

# Cache statistics
curl http://localhost:8000/api/cache/stats

# Clear database
curl -X POST http://localhost:8000/api/clear-db
```

### JavaScript/Fetch Example

```javascript
// Query the RAG API
async function queryRAG(question) {
  const response = await fetch('http://localhost:8000/api/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question: question,
      debug: false,
    }),
  });

  const data = await response.json();
  return data;
}

// Usage
const answer = await queryRAG("What are the main findings?");
console.log(answer.answer);
```

## Configuration

### Environment Variables

```bash
# Server settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# Cache settings
CACHE_ENABLED=True
CACHE_TTL_SECONDS=3600
REDIS_URL=redis://localhost:6379  # Optional, uses in-memory cache if not set

# Database settings
MONGODB_URI=mongodb://localhost:27017
QDRANT_URL=http://localhost:6333

# Ingestion settings
UPLOAD_DIR=/tmp/rag_uploads
MAX_FILE_SIZE_MB=50
```

### Query Optimization Settings

```bash
# Vector search results
MAX_VECTOR_RESULTS=3
VECTOR_SEARCH_LIMIT=10

# Table search results
MAX_TABLE_RESULTS=5
```

## Error Handling

All error responses follow a consistent format:

```json
{
  "error": "Error type or message",
  "detail": "Detailed error information",
  "request_id": "unique-request-id",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Common HTTP Status Codes:**

- `200 OK`: Successful request
- `202 Accepted`: Request accepted (async processing)
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `413 Payload Too Large`: File size exceeds limit
- `500 Internal Server Error`: Server-side error

## Caching Strategy

The API implements a multi-layer caching strategy:

### Query Cache
- Caches entire query results (answer + sources)
- Key: Hash of question + file_filter
- TTL: Configurable (default: 1 hour)
- Backend: Redis (with in-memory fallback)

### Embedding Cache
- Caches computed embeddings
- In-memory storage for frequently queried terms
- Reduces embedding computation time

### Optimization Tips

1. **Use file_filter**: Narrows search scope, improves speed
2. **Adjust CACHE_TTL_SECONDS**: Higher for stable documents, lower for frequently updated content
3. **Enable Redis**: Better performance for high-load scenarios
4. **Monitor cache stats**: Use `/api/cache/stats` endpoint to track performance

## Performance Considerations

### Typical Response Times

- Vector search: 50-200ms
- Table search: 30-100ms
- Hybrid query: 100-500ms
- LLM response: 1-5 seconds (depends on model)

### Scaling

- **Single API instance**: ~100 concurrent queries
- **Multiple instances**: Use load balancer (HAProxy, Nginx)
- **Redis cache**: Reduces LLM load by ~60% for repeated queries
- **Vector DB optimization**: Adjust Qdrant collection parameters for your data

## Troubleshooting

### "Service Unhealthy" Error

Check system status:
```bash
curl http://localhost:8000/api/status
```

### MongoDB Connection Issues

```bash
# Verify MongoDB is running
docker ps | grep mongo

# Check MongoDB connection
mongosh --uri "mongodb://root:examplepassword@localhost:27017"
```

### Qdrant Issues

```bash
# Verify Qdrant is running
curl http://localhost:6334

# Access Qdrant web UI
# http://localhost:6334/dashboard
```

### Cache Issues

```bash
# Clear cache if having issues
curl -X POST http://localhost:8000/api/cache/clear

# Check cache stats
curl http://localhost:8000/api/cache/stats
```

## API Roadmap

- [ ] Authentication (API keys, JWT)
- [ ] Rate limiting
- [ ] Request signing/verification
- [ ] Batch query endpoint
- [ ] Streaming responses for large queries
- [ ] WebSocket support for real-time updates
- [ ] Analytics dashboard
- [ ] Custom model selection per query

## License

MIT License - See LICENSE file for details

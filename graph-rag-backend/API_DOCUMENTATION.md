# Graph RAG API Documentation

Complete API reference for the Graph RAG Platform.

## Base URL

```
http://localhost:8000
```

## Interactive Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Health & Status

### GET /
Get basic service information.

**Response:**
```json
{
  "service": "Graph RAG Backend",
  "version": "1.0.0",
  "status": "operational"
}
```

### GET /health
Check service health status.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "graph_db": "connected",
    "vector_store": "connected",
    "llm": "available"
  }
}
```

---

## Document Management

### POST /api/documents/upload
Upload and process a document into the knowledge graph.

**Request:**
- Content-Type: `multipart/form-data`
- Body: File upload (PDF, DOCX, TXT)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "document_id": "uuid-string",
  "filename": "document.pdf",
  "stages": [
    {
      "agent": "Document Parser",
      "action": "Extracting text chunks",
      "status": "complete",
      "timestamp": 0.523
    },
    {
      "agent": "LLM Ontology Extractor",
      "action": "Identifying entities and relationships",
      "status": "complete",
      "timestamp": 1.234
    }
  ],
  "graph_stats": {
    "entities": 45,
    "relationships": 120,
    "attributes": 180
  }
}
```

### GET /api/documents
List all processed documents.

**Response:**
```json
[
  {
    "id": "uuid-string",
    "filename": "document.pdf",
    "processed_at": "2025-10-18T10:30:00",
    "chunks": 25,
    "graph_stats": {
      "entities": 45,
      "relationships": 120
    }
  }
]
```

---

## Knowledge Graph

### GET /api/graph/stats
Get knowledge graph statistics.

**Response:**
```json
{
  "entities": 250,
  "relationships": 680,
  "attributes": 1200,
  "entity_types": {
    "Person": 45,
    "Organization": 12,
    "Location": 8,
    "Project": 15
  }
}
```

### GET /api/graph/ontology
Get the current ontology schema.

**Response:**
```json
{
  "version": "1.0",
  "entity_types": [
    {
      "name": "Person",
      "count": 45,
      "properties": [
        {"name": "name", "type": "str"},
        {"name": "role", "type": "str"}
      ]
    }
  ],
  "relationship_types": [
    {
      "name": "WORKS_IN",
      "count": 120
    }
  ],
  "total_entities": 250,
  "total_relationships": 680
}
```

### POST /api/graph/ontology/refine
Refine ontology using LLM assistance.

**Request:**
```json
{
  "action": "suggest_relationships",
  "entity_type1": "Person",
  "entity_type2": "Organization"
}
```

**Actions:**
- `suggest_relationships`: Suggest new relationships between entity types
- `merge_entity_types`: Merge similar entity types
- `add_hierarchy`: Add hierarchical relationships
- `improve_schema`: Get general schema improvements

**Response:**
```json
{
  "suggestions": [
    "Person_WORKS_FOR_Organization",
    "Person_LEADS_Organization",
    "Person_FOUNDED_Organization"
  ],
  "source": "llm"
}
```

### GET /api/graph/visualize
Get graph data for visualization.

**Parameters:**
- `limit` (optional, default: 100): Maximum number of nodes

**Response:**
```json
{
  "nodes": [
    {
      "id": "1",
      "label": "John Smith",
      "type": "Person"
    }
  ],
  "edges": [
    {
      "from": "1",
      "to": "2",
      "label": "WORKS_IN"
    }
  ],
  "stats": {
    "entities": 250,
    "relationships": 680
  }
}
```

---

## Query & Retrieval

### POST /api/query
Execute an agentic query with multi-modal retrieval.

**Request:**
```json
{
  "query": "Who manages the Marketing Department in Delhi?",
  "max_results": 10,
  "use_vector": true,
  "use_graph": true,
  "use_filter": true
}
```

**Parameters:**
- `query` (required): Natural language question
- `max_results` (optional, default: 10): Maximum results to return
- `use_vector` (optional, default: true): Enable vector similarity search
- `use_graph` (optional, default: true): Enable graph traversal
- `use_filter` (optional, default: true): Enable metadata filtering

**Response:**
```json
{
  "answer": "Based on the knowledge graph, the Marketing Department in Delhi is managed by Sarah Johnson. She oversees a team of 8 employees working on 3 active projects.",
  "sources": [
    {
      "type": "graph",
      "content": "Graph path at depth 1: Person: Sarah Johnson",
      "confidence": 0.95,
      "metadata": {"depth": 1}
    },
    {
      "type": "vector",
      "content": "Sarah Johnson leads the marketing initiatives...",
      "confidence": 0.92,
      "metadata": {"similarity": "92%"}
    },
    {
      "type": "filter",
      "content": "Filtered match: Department - Marketing",
      "confidence": 0.90,
      "metadata": {"location": "Delhi"}
    }
  ],
  "reasoning_chain": [
    {
      "agent": "Coordinator Agent",
      "action": "Analyzing query complexity",
      "status": "complete",
      "timestamp": 1729245600.123
    },
    {
      "agent": "Vector Search Agent",
      "action": "Finding semantically similar content",
      "status": "complete",
      "timestamp": 1729245600.456
    }
  ],
  "confidence": 0.94,
  "query_time_ms": 425.5
}
```

### POST /api/query/stream
Stream query results with reasoning chain (Server-Sent Events).

**Request:** Same as `/api/query`

**Response:** Stream of JSON objects
```
data: {"agent": "Coordinator Agent", "action": "Analyzing query", "status": "complete"}

data: {"agent": "Vector Search Agent", "action": "Searching...", "status": "complete"}

data: {"answer": "...", "sources": [...], "confidence": 0.94}
```

---

## Administration

### POST /api/admin/reset
Reset the entire knowledge graph (use with caution).

**Response:**
```json
{
  "status": "success",
  "message": "Database reset completed"
}
```

### GET /api/admin/metrics
Get comprehensive system metrics.

**Response:**
```json
{
  "queries": {
    "total": 150,
    "successful": 148,
    "failed": 2,
    "avg_latency_ms": 425.5,
    "latencies": [400, 450, 380, ...]
  },
  "documents": {
    "total_processed": 25,
    "total_entities": 1250,
    "total_relationships": 3420,
    "processing_times": [2000, 3500, 1800, ...]
  },
  "graph": {
    "total_nodes": 1250,
    "total_edges": 3420,
    "storage_mb": 2.45
  },
  "agents": {
    "coordinator": {
      "calls": 150,
      "avg_time_ms": 45.2
    },
    "vector_search": {
      "calls": 148,
      "avg_time_ms": 180.5
    },
    "graph_traversal": {
      "calls": 142,
      "avg_time_ms": 120.3
    }
  },
  "system": {
    "uptime_seconds": 3600,
    "start_time": 1729245600.0
  }
}
```

---

## Error Responses

All endpoints may return error responses with the following structure:

### 400 Bad Request
```json
{
  "detail": "Invalid query format"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "query"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Processing failed: connection timeout"
}
```

---

## Rate Limits

Currently no rate limits are enforced. For production deployment, implement rate limiting based on:
- API key
- IP address
- User account

---

## Authentication

The current version does not require authentication. For production:

**Recommended**: Implement Bearer token authentication

```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "Your question"}'
```

---

## Python SDK Example

```python
import requests

class GraphRAGClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def upload_document(self, file_path):
        with open(file_path, 'rb') as f:
            response = requests.post(
                f"{self.base_url}/api/documents/upload",
                files={'file': f}
            )
        return response.json()
    
    def query(self, question):
        response = requests.post(
            f"{self.base_url}/api/query",
            json={'query': question}
        )
        return response.json()

# Usage
client = GraphRAGClient()
result = client.query("Who is the CEO?")
print(result['answer'])
```

---

## WebSocket Support (Future)

Planned for v2.0: Real-time updates via WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Graph update:', data);
};
```

---

## Changelog

### v1.0.0 (2025-10-18)
- Initial release
- Document upload and processing
- Multi-modal retrieval
- Agentic query execution
- Neo4j and in-memory graph support
- Ontology management
- Entity resolution

---

## Support

For issues, questions, or feature requests:
- GitHub Issues: [your-repo]/issues
- Email: support@example.com
- Documentation: http://localhost:8000/docs
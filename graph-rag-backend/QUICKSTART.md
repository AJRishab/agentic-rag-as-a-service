# Graph RAG - Quick Start Guide

Get up and running in 5 minutes!

## ⚡ Prerequisites

- Python 3.8+
- Docker (optional, recommended)
- 4GB RAM minimum

## 🚀 Installation

### Method 1: Automated Setup (Recommended)

```bash
# Clone repository
git clone <your-repo-url>
cd graph-rag-backend

# Run setup script
chmod +x setup.sh
./setup.sh

# Start with Docker
make docker-up
```

### Method 2: Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p uploads vector_store logs services

# Create .env file
cp .env.example .env

# Start server
uvicorn main:app --reload
```

## 📝 Usage Examples

### 1. Upload a Document

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@example.pdf"
```

**Python:**
```python
import requests

with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/documents/upload',
        files={'file': f}
    )
print(response.json()['document_id'])
```

### 2. Query Knowledge Base

```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Who is the CEO?",
    "max_results": 10
  }'
```

**Python:**
```python
import requests

response = requests.post(
    'http://localhost:8000/api/query',
    json={'query': 'Who is the CEO?'}
)
result = response.json()
print(result['answer'])
```

### 3. Run Demo

```bash
# Full demonstration
python demo.py

# Specific command
python demo.py upload     # Upload sample document
python demo.py query "Your question"
python demo.py stats      # Show statistics
```

## 🔧 Configuration

Edit `.env` file:

```env
# Use in-memory graph (no setup required)
GRAPH_DB_TYPE=memory

# OR use Neo4j (requires Docker)
GRAPH_DB_TYPE=neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# LLM Provider
LLM_PROVIDER=ollama  # Free local LLM
# LLM_PROVIDER=openai  # Requires API key
```

## 📊 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| API | http://localhost:8000 | Main API endpoint |
| Swagger UI | http://localhost:8000/docs | Interactive API docs |
| ReDoc | http://localhost:8000/redoc | Alternative docs |
| Neo4j Browser | http://localhost:7474 | Graph visualization |
| Health Check | http://localhost:8000/health | Service status |

## 🎯 Common Commands

```bash
# Start server
make run

# Start with Docker
make docker-up

# Stop Docker services
make docker-down

# Run tests
make test

# View logs
make docker-logs

# Clean up
make clean
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>

# Or use different port
uvicorn main:app --port 8001
```

### Neo4j Not Connected
- System automatically uses in-memory fallback
- Check: `docker logs graphrag-neo4j`
- Solution: Set `GRAPH_DB_TYPE=memory` in `.env`

### Ollama Not Working
- LLM features use fallback rule-based extraction
- Check: `curl http://localhost:11434/api/tags`
- Solution: System continues with basic functionality

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Ensure services package exists
touch services/__init__.py
```

## 📚 Next Steps

1. **Read Full Documentation**: `README.md`
2. **Explore API**: http://localhost:8000/docs
3. **Try Examples**: `python demo.py`
4. **Upload Documents**: Start building your knowledge base
5. **Customize**: Modify configs for your use case

## 💡 Quick Tips

- **Start Simple**: Use in-memory mode first
- **Test Queries**: Try the demo script
- **Monitor**: Check `/api/admin/metrics`
- **Scale Up**: Add Neo4j when ready
- **Learn More**: Read API_DOCUMENTATION.md

## ✅ Verification

Confirm everything works:

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Upload test
echo "Test document content" > test.txt
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@test.txt"

# 3. Query test
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'

# 4. Stats
curl http://localhost:8000/api/graph/stats
```

All should return 200 OK!

## 🆘 Need Help?

- **Docs**: Check `README.md` and `API_DOCUMENTATION.md`
- **Issues**: GitHub Issues page
- **API Reference**: http://localhost:8000/docs
- **Examples**: See `demo.py`

---

**You're ready to go! 🎉**

Start with: `python demo.py`
# Deploy Backend to Render - Step by Step (3 Minutes)

## Prerequisites
- GitHub account with code pushed
- Render account (free at https://render.com)
- Your Groq API key
- Your Neo4j Aura credentials

## Step 1: Create Render Account (Skip if you have one)

1. Go to https://render.com
2. Click "Sign Up"
3. Choose "GitHub" to sign up with GitHub
4. Authorize Render to access your GitHub account
5. Done! ✅

## Step 2: Create New Web Service

1. Log in to https://dashboard.render.com
2. Click **"New +"** button (top right)
3. Select **"Web Service"**
4. Click **"Connect GitHub"** button
5. Search for **"graph-rag"** repo
6. Click **"Connect"** next to your repo
7. You'll be taken to the service creation form

## Step 3: Configure Web Service

Fill in the form with these values:

### Basic Settings
- **Name**: `graph-rag-backend`
- **Region**: Select closest to you (e.g., `us-west-1` for US West)
- **Branch**: `main`
- **Root Directory**: `graph-rag-backend`

### Build & Deploy
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Plan
- **Plan**: `Free` (Scroll down to see free option)

### Environment Variables
Click **"Advanced"** to expand, then **"Add Environment Variable"** for each:

```
LLM_PROVIDER=groq
GROQ_API_KEY=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
GROQ_MODEL=llama-3.1-8b-instant
GRAPH_DB_TYPE=neo4j
NEO4J_URI=neo4j+s://4971d414.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=b2xQmYrUILZeXt-3tAw0b5-yM-e2U08NtDUF2LzvjQk
APP_NAME=Graph RAG Platform
APP_VERSION=1.0.0
DEBUG=false
HOST=0.0.0.0
PORT=10000
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
CHUNK_SIZE=500
CHUNK_OVERLAP=50
MAX_CHUNKS_PER_DOC=1000
ENTITY_SIMILARITY_THRESHOLD=0.85
MAX_VECTOR_RESULTS=10
GRAPH_TRAVERSAL_DEPTH=2
RETRIEVAL_TIMEOUT_SECONDS=30
UPLOAD_DIR=./uploads
VECTOR_STORE_PATH=./vector_store
LOG_LEVEL=INFO
 
```

**Note**: Copy each key and value exactly as shown above.

## Step 4: Click Deploy

1. Scroll to bottom
2. Click **"Create Web Service"**
3. Render will start building your app
4. **Wait for deployment to complete** (2-3 minutes)

## Step 5: Get Your Backend URL

Once deployed:
1. Your service page will show a URL like: `https://graph-rag-backend-xxxxx.onrender.com`
2. Wait for status to show "Live" (green)
3. **COPY THIS URL** - you'll need it for frontend

## Step 6: Verify Backend is Running

Test the backend by visiting:
```
https://graph-rag-backend-xxxxx.onrender.com/
```

You should see:
```json
{
  "service": "Graph RAG Backend",
  "version": "1.0.0",
  "status": "operational"
}
```

## Troubleshooting

### Build Fails
- Check Render logs (click service → Logs tab)
- Common issues:
  - Missing `requirements.txt` in `graph-rag-backend/`
  - Syntax errors in Python code
  - Missing dependencies

### "Port already in use"
- Render uses dynamic port ($PORT variable)
- We handle this with `--port $PORT`
- Should work fine

### "Module not found" errors
- Check `requirements.txt` includes all dependencies
- Verify `main.py` is in `graph-rag-backend/` directory

### API returns 500 errors
- Check environment variables are set correctly
- Verify Neo4j Aura credentials
- Check Groq API key is valid

### "Failed to build"
- Click service → Logs
- Read error message
- Check Python syntax in updated files
- Rebuild manually or push to GitHub to trigger rebuild

## Environment Variables Reference

| Variable | Value | Purpose |
|----------|-------|---------|
| GROQ_API_KEY | gsk_J4NZMV... | LLM API authentication |
| GROQ_MODEL | llama-3.1-8b-instant | Fast model for inference |
| NEO4J_URI | neo4j+s://... | Cloud graph database |
| NEO4J_USER | neo4j | Database username |
| NEO4J_PASSWORD | b2xQmYr... | Database password |
| LLM_PROVIDER | groq | Which LLM to use |
| DEBUG | false | Production mode |
| PORT | $PORT | Render-provided dynamic port |

## After Successful Deployment

✅ Backend is live at: `https://graph-rag-backend-xxxxx.onrender.com`
✅ API endpoints accessible
✅ Groq integration working
✅ Neo4j Aura connected

Next: Deploy frontend to Vercel with this backend URL!

## Quick Links

- Render Dashboard: https://dashboard.render.com
- Service URL: https://graph-rag-backend-xxxxx.onrender.com
- Groq Console: https://console.groq.com
- Neo4j Aura: https://aura.neo4j.io

## Notes

- Free tier may have brief sleep periods (auto-wakes)
- Build time: ~2-3 minutes
- Deployment time: ~1 minute
- Total: ~3-4 minutes
- First cold start: ~10 seconds
- Subsequent requests: < 1 second

## Success Indicators

✓ Service shows "Live" status (green)
✓ `/` endpoint returns JSON with status "operational"
✓ Logs show no errors
✓ Environment variables all show correct values
✓ Backend URL accessible from anywhere

You're done! 🎉

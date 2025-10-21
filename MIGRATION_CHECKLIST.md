# Cloud Migration Checklist ✅

## Completed Tasks

- [x] Updated `.env` with Groq API key
- [x] Updated `.env` with Neo4j Aura credentials
- [x] Changed LLM provider from Ollama to Groq
- [x] Created Groq service (`groq_service.py`)
- [x] Updated document processor to use Groq
- [x] Added Groq SDK to requirements.txt
- [x] Updated config.py to support Groq
- [x] Updated frontend API URL to use environment variable
- [x] Created `.env.example` files for both services
- [x] Created deployment guide (CLOUD_DEPLOYMENT.md)
- [x] Installed Groq SDK locally

## Key Changes Made

### Backend
- **LLM**: Ollama (local) → Groq API (cloud)
- **Database**: Memory/Local Neo4j → Neo4j Aura (cloud)
- **New File**: `services/groq_service.py`
- **Updated**: `document_processor.py`, `config.py`, `requirements.txt`

### Frontend
- **API Base URL**: Now uses `REACT_APP_API_URL` environment variable
- Defaults to `localhost:8000` for local development
- Can be overridden for cloud deployment

## Local Testing

Backend is already running with your credentials. To verify Groq integration:

1. Check backend logs for "Groq extraction successful" message
2. Try uploading a document to test entity extraction
3. Verify queries work with the new setup

## Before Cloud Deployment

### Create `.env` file for backend:
```bash
cp graph-rag-backend/.env.example graph-rag-backend/.env
# Edit with your credentials (already done)
```

### Create `.env` file for frontend:
```bash
cp graph-rag-frontend/.env.example graph-rag-frontend/.env
# Leave as localhost for now
```

## Deployment Steps

### Step 1: Initialize Git
```bash
cd /path/to/graph-rag
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Step 2: Create .gitignore
Ensure it includes:
```
.env
.env.local
*.log
node_modules/
__pycache__/
venv/
.DS_Store
```

### Step 3: Commit and Push to GitHub
```bash
git add .
git commit -m "Prepare for cloud deployment with Groq and Neo4j Aura"
git branch -M main
git remote add origin https://github.com/your-username/graph-rag.git
git push -u origin main
```

### Step 4: Deploy Backend on Render
1. Go to https://render.com
2. Create new Web Service from GitHub
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env.example`
6. Deploy and get your backend URL (e.g., `https://graph-rag-backend.onrender.com`)

### Step 5: Deploy Frontend
**Option A - Vercel (Recommended):**
1. Go to https://vercel.com
2. Import GitHub repo
3. Set `REACT_APP_API_URL=<your-render-backend-url>`
4. Deploy

**Option B - Render Static Site:**
1. In Render dashboard, create Static Site
2. Build command: `npm run build`
3. Publish directory: `build`
4. Deploy

## Testing Checklist

After deployment:
- [ ] Backend API responds to `GET /`
- [ ] Frontend loads and shows API status as "connected"
- [ ] Document upload works
- [ ] Entity extraction uses Groq (check logs)
- [ ] Queries return results
- [ ] Graph visualization loads

## Credentials Used

Your credentials are already configured in the `.env` file:

**Groq API:**
- Key: `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`

**Neo4j Aura:**
- URI: `neo4j+s://4971d414.databases.neo4j.io`
- Username: `neo4j`
- Password: `b2xQmYrUILZeXt-3tAw0b5-yM-e2U08NtDUF2LzvjQk`

## Free Tier Limits

| Service | Limit | Status |
|---------|-------|--------|
| Groq API | ~600 requests/month | ✅ Sufficient |
| Neo4j Aura | 100k relationships, 15GB | ✅ Sufficient |
| Render | 750 compute hours/month | ✅ Sufficient |
| Vercel | Unlimited | ✅ OK |

## Monitoring

**After deployment, monitor:**
1. Groq API usage at https://console.groq.com
2. Neo4j instance at https://aura.neo4j.io
3. Backend logs on Render dashboard
4. Frontend errors in browser console

## Troubleshooting

If something breaks, check:

1. **Backend won't start**
   - Render logs show the error
   - Verify all env vars are set
   - Check Neo4j connectivity

2. **Frontend can't connect**
   - CORS enabled in FastAPI? (It is by default)
   - Is backend URL correct in frontend `.env`?
   - Check browser console for errors

3. **Groq errors**
   - API key valid?
   - Rate limit hit? (Check Groq console)
   - Network connectivity issue?

## Next Steps

1. Test locally with the current setup
2. Push to GitHub
3. Deploy backend to Render
4. Deploy frontend to Vercel
5. Test live deployment
6. Monitor usage

## Support

For issues:
- Groq: https://console.groq.com/docs
- Neo4j: https://aura.neo4j.io/docs
- Render: https://render.com/docs
- Vercel: https://vercel.com/docs

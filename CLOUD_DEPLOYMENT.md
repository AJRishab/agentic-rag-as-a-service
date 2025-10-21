# Cloud Deployment Guide - Graph RAG

This guide walks through deploying Graph RAG to the cloud using free tiers.

## Prerequisites

- GitHub account (for code hosting)
- Render account (for backend hosting)
- Vercel account (optional, for frontend hosting)
- Groq API key
- Neo4j Aura instance

## Step 1: Get Required Credentials

### 1.1 Groq API Key
1. Visit https://console.groq.com
2. Sign up/log in
3. Navigate to API keys
4. Copy your API key

### 1.2 Neo4j Aura Instance (Already Created)
Your credentials:
- URI: `neo4j+s://4971d414.databases.neo4j.io`
- Username: `neo4j`
- Password: `b2xQmYrUILZeXt-3tAw0b5-yM-e2U08NtDUF2LzvjQk`

## Step 2: Prepare Code for Deployment

### 2.1 Update Environment Variables

Backend (.env):
```bash
GROQ_API_KEY=your-groq-api-key
NEO4J_URI=neo4j+s://4971d414.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=b2xQmYrUILZeXt-3tAw0b5-yM-e2U08NtDUF2LzvjQk
LLM_PROVIDER=groq
GRAPH_DB_TYPE=neo4j
DEBUG=false
```

Frontend (.env):
```bash
REACT_APP_API_URL=https://your-render-backend.onrender.com
```

### 2.2 Update .gitignore

Make sure `.env` files are NOT committed to git:
```
.env
.env.local
*.log
node_modules/
/build
__pycache__/
```

## Step 3: Deploy Backend on Render

### 3.1 Push Code to GitHub
```bash
git init
git add .
git commit -m "Initial commit for cloud deployment"
git branch -M main
git remote add origin https://github.com/your-username/graph-rag.git
git push -u origin main
```

### 3.2 Create Render Service

1. Go to https://render.com
2. Sign up/log in
3. Click "New +" → "Web Service"
4. Connect GitHub repo
5. Configure:
   - **Name**: graph-rag-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Region**: Choose closest to you
   - **Plan**: Free

### 3.3 Set Environment Variables in Render

In Render dashboard for your service:
1. Go to Environment tab
2. Add all variables from `.env.example`:
   - GROQ_API_KEY
   - NEO4J_URI
   - NEO4J_USER
   - NEO4J_PASSWORD
   - LLM_PROVIDER=groq
   - GRAPH_DB_TYPE=neo4j
   - DEBUG=false

### 3.4 Deploy

Click "Deploy" and wait for build to complete. Your backend URL will be:
`https://your-service-name.onrender.com`

## Step 4: Deploy Frontend on Vercel (Optional) or Render

### Option A: Vercel (Recommended for React)

1. Go to https://vercel.com
2. Sign up/log in
3. Click "Add New..." → "Project"
4. Import GitHub repo
5. Set environment variable:
   - `REACT_APP_API_URL=https://your-render-backend.onrender.com`
6. Deploy

### Option B: Render

1. In Render dashboard, create new Static Site
2. Connect same GitHub repo (or use `/graph-rag-frontend` subdirectory)
3. Build Command: `npm run build`
4. Publish Directory: `build`
5. Set environment variable:
   - `REACT_APP_API_URL=https://your-render-backend.onrender.com`

## Step 5: Verify Deployment

1. Open frontend URL
2. Check "API Status" indicator
3. Try uploading a test document
4. Try querying

## Troubleshooting

### Backend Won't Start
- Check logs in Render dashboard
- Verify all env variables are set
- Ensure Neo4j Aura instance is accessible

### Frontend Can't Connect to Backend
- Check that backend URL in frontend `.env` is correct
- Verify CORS is enabled in backend (it is by default)
- Check browser console for error messages

### Groq API Errors
- Verify API key is correct
- Check Groq API status at console.groq.com
- Review rate limits

### Neo4j Connection Issues
- Verify URI, username, and password
- Check that instance is active in Neo4j Aura dashboard
- Ensure network connectivity

## Cost

- **Groq API**: Free tier (~600 requests/month)
- **Neo4j Aura**: Free tier (100k relationships, 15GB)
- **Render**: Free tier (limited compute, may sleep)
- **Vercel**: Free tier (unlimited deployments)

**Total Cost**: $0

## Next Steps

1. Monitor usage at each service's dashboard
2. Set up CI/CD for automatic deployments
3. Enable backups for Neo4j data
4. Monitor API costs on Groq console

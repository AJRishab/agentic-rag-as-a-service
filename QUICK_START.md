# 🚀 Quick Start - Graph RAG Platform

Your Graph RAG Platform is now ready to run! Both frontend and backend are set up and working.

## ⚡ Instant Start

### Option 1: PowerShell Script (Recommended)
```powershell
# Run this in PowerShell from the graph-rag directory
.\start.ps1
```

### Option 2: Batch File
```batch
# Double-click or run from command prompt
start.bat
```

### Option 3: Manual Start
```powershell
# Start Backend (in one terminal)
cd graph-rag-backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Start Frontend (in another terminal)
cd graph-rag-frontend
npm start
```

## 🌐 Access Your Platform

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main user interface |
| **Backend API** | http://localhost:8000 | REST API server |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |

## 🎯 What to Do Next

1. **Open the Frontend** → http://localhost:3000
2. **Upload a Document** → Use the "Document Upload" tab
3. **Explore Knowledge Graph** → Check the "Knowledge Graph" tab  
4. **Ask Questions** → Use the "Agentic Query" tab
5. **Check API Docs** → Visit http://localhost:8000/docs

## 📁 Project Structure

```
graph-rag/
├── 📂 graph-rag-backend/     # Python FastAPI server
├── 📂 graph-rag-frontend/    # React frontend  
├── 🚀 start.ps1             # PowerShell start script
├── 🚀 start.bat             # Batch start script  
└── 📝 QUICK_START.md         # This file
```

## 🔧 Dependencies Status

✅ **Backend Dependencies**: Installed and ready
- FastAPI, Uvicorn, Neo4j driver, Pydantic, etc.

✅ **Frontend Dependencies**: Installed and ready  
- React, Tailwind CSS, Lucide Icons, etc.

## 🐛 Troubleshooting

### Backend Issues
- **Port 8000 busy**: Stop other services or change port in config
- **Import errors**: Make sure you're in `graph-rag-backend` directory

### Frontend Issues  
- **Port 3000 busy**: Stop other React apps or use different port
- **Compilation errors**: Try `npm install` again

### Both Services
- **Can't connect**: Wait a few seconds for startup, check ports
- **Dependencies missing**: Re-run install commands

## 🎉 Success Indicators

You know everything is working when:
- ✅ Backend shows: `INFO: Uvicorn running on http://0.0.0.0:8000`
- ✅ Frontend shows: `webpack compiled successfully`
- ✅ Browser opens to http://localhost:3000
- ✅ Frontend shows "Connected" status (green dot)

## 💡 Pro Tips

1. **Keep both terminals open** - closing them stops the services
2. **Use the PowerShell script** - it handles startup automatically  
3. **Check logs** - both terminals show helpful debug information
4. **API-first development** - test endpoints at http://localhost:8000/docs

---

**Happy Graph RAGging! 🎉**

Your full-stack Graph RAG platform with agentic reasoning is now ready for intelligent document processing and querying!
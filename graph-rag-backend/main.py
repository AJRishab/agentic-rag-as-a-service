"""
Graph RAG Backend - Main FastAPI Application
Provides agentic retrieval with Neo4j graph database and OpenAI embeddings
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
from enum import Enum

from config import settings

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://localhost:3001",  # Alternative port
        "http://127.0.0.1:3001",  # Alternative port
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ============================================================================
# DATA MODELS
# ============================================================================

class ProcessingStage(BaseModel):
    agent: str
    action: str
    status: str
    timestamp: float


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    stages: List[ProcessingStage]
    graph_stats: Dict[str, int]


class QueryRequest(BaseModel):
    query: str
    max_results: int = 10
    use_vector: bool = True
    use_graph: bool = True
    use_filter: bool = True


class EvidenceSource(BaseModel):
    type: str  # 'graph', 'vector', 'filter'
    content: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[EvidenceSource]
    reasoning_chain: List[ProcessingStage]
    confidence: float
    query_time_ms: float


class GraphStats(BaseModel):
    entities: int
    relationships: int
    attributes: int
    entity_types: Dict[str, int]


class OntologyElement(BaseModel):
    name: str
    type: str  # 'entity', 'relationship', 'attribute'
    properties: Dict[str, Any]


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/")
async def root():
    return {
        "service": "Graph RAG Backend",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "graph_db": "connected",
            "vector_store": "connected",
            "llm": "available"
        }
    }


# ============================================================================
# DOCUMENT INGESTION ENDPOINTS
# ============================================================================

@app.post("/api/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document into knowledge graph
    Supports PDF, DOCX, TXT, and plain text
    """
    from services.document_processor import DocumentProcessor
    from services.graph_constructor import GraphConstructor
    
    processor = DocumentProcessor()
    constructor = GraphConstructor()
    
    try:
        # Read file content
        content = await file.read()
        
        # Process document through pipeline
        result = await processor.process_document(
            filename=file.filename,
            content=content
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.get("/api/documents", response_model=List[Dict[str, Any]])
async def list_documents():
    """List all processed documents"""
    from services.document_processor import DocumentProcessor
    
    processor = DocumentProcessor()
    return await processor.list_documents()


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its associated graph data"""
    from services.document_processor import DocumentProcessor
    
    processor = DocumentProcessor()
    result = await processor.delete_document(document_id)
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    
    return result


# ============================================================================
# GRAPH ENDPOINTS
# ============================================================================

@app.get("/api/graph/stats", response_model=GraphStats)
async def get_graph_stats():
    """Get knowledge graph statistics"""
    from services.graph_service import GraphService
    
    graph_service = GraphService()
    return await graph_service.get_stats()


@app.get("/api/graph/ontology")
async def get_ontology():
    """Get current ontology schema"""
    from services.ontology_manager import OntologyManager
    
    ontology_mgr = OntologyManager()
    return await ontology_mgr.get_ontology()


@app.post("/api/graph/ontology/refine")
async def refine_ontology(refinement: Dict[str, Any]):
    """Refine ontology using LLM assistance"""
    from services.ontology_manager import OntologyManager
    
    ontology_mgr = OntologyManager()
    return await ontology_mgr.refine_with_llm(refinement)


@app.get("/api/graph/visualize")
async def visualize_graph(limit: int = 100):
    """Get graph data for visualization"""
    from services.graph_service import GraphService
    
    graph_service = GraphService()
    return await graph_service.get_visualization_data(limit)


# ============================================================================
# QUERY ENDPOINTS
# ============================================================================

@app.post("/api/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    """
    Execute agentic query with multi-modal retrieval
    Combines vector search, graph traversal, and logical filtering
    """
    from services.agentic_retrieval import AgenticRetrieval
    
    retrieval_system = AgenticRetrieval()
    
    try:
        result = await retrieval_system.execute_query(
            query=request.query,
            max_results=request.max_results,
            use_vector=request.use_vector,
            use_graph=request.use_graph,
            use_filter=request.use_filter
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.post("/api/query/stream")
async def stream_query(request: QueryRequest):
    """Stream query results with reasoning chain"""
    from fastapi.responses import StreamingResponse
    from services.agentic_retrieval import AgenticRetrieval
    
    retrieval_system = AgenticRetrieval()
    
    async def generate():
        async for chunk in retrieval_system.stream_query(request.query):
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.post("/api/admin/reset")
async def reset_database():
    """Reset entire knowledge graph (use with caution)"""
    from services.graph_service import GraphService
    
    graph_service = GraphService()
    await graph_service.reset()
    return {"status": "success", "message": "Database reset completed"}


@app.get("/api/admin/metrics")
async def get_metrics():
    """Get system performance metrics"""
    from services.metrics_collector import MetricsCollector
    
    metrics = MetricsCollector()
    return await metrics.get_all_metrics()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
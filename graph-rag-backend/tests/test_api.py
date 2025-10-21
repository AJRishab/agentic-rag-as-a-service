"""
API Integration Tests
Tests for Graph RAG API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from main import app
import io


client = TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "service" in response.json()
        assert response.json()["service"] == "Graph RAG Backend"
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestDocumentEndpoints:
    """Test document upload and processing"""
    
    def test_upload_text_document(self):
        """Test uploading a text document"""
        # Create a simple text file
        file_content = b"This is a test document about artificial intelligence and machine learning."
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
        
        response = client.post("/api/documents/upload", files=files)
        assert response.status_code == 200
        
        data = response.json()
        assert "document_id" in data
        assert "filename" in data
        assert "stages" in data
        assert len(data["stages"]) > 0
    
    def test_list_documents(self):
        """Test listing processed documents"""
        response = client.get("/api/documents")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestGraphEndpoints:
    """Test graph-related endpoints"""
    
    def test_get_graph_stats(self):
        """Test retrieving graph statistics"""
        response = client.get("/api/graph/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "entities" in data
        assert "relationships" in data
    
    def test_get_ontology(self):
        """Test retrieving ontology"""
        response = client.get("/api/graph/ontology")
        assert response.status_code == 200
        
        data = response.json()
        assert "entity_types" in data
        assert "relationship_types" in data
    
    def test_visualize_graph(self):
        """Test graph visualization endpoint"""
        response = client.get("/api/graph/visualize?limit=50")
        assert response.status_code == 200
        
        data = response.json()
        assert "nodes" in data
        assert "edges" in data


class TestQueryEndpoints:
    """Test query and retrieval endpoints"""
    
    def test_execute_query(self):
        """Test executing a query"""
        query_data = {
            "query": "What is artificial intelligence?",
            "max_results": 10,
            "use_vector": True,
            "use_graph": True,
            "use_filter": False
        }
        
        response = client.post("/api/query", json=query_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "reasoning_chain" in data
        assert "confidence" in data
    
    def test_query_with_filters(self):
        """Test query with filtering enabled"""
        query_data = {
            "query": "Find employees in Delhi",
            "max_results": 5,
            "use_vector": True,
            "use_graph": True,
            "use_filter": True
        }
        
        response = client.post("/api/query", json=query_data)
        assert response.status_code == 200


class TestAdminEndpoints:
    """Test admin and metrics endpoints"""
    
    def test_get_metrics(self):
        """Test retrieving system metrics"""
        response = client.get("/api/admin/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "queries" in data
        assert "documents" in data
        assert "graph" in data
        assert "system" in data


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_upload_without_file(self):
        """Test upload endpoint without file"""
        response = client.post("/api/documents/upload")
        assert response.status_code == 422  # Validation error
    
    def test_query_without_text(self):
        """Test query endpoint without query text"""
        query_data = {
            "query": "",
            "max_results": 10
        }
        
        response = client.post("/api/query", json=query_data)
        # Should handle empty query gracefully
        assert response.status_code in [200, 400]


@pytest.mark.asyncio
class TestIntegrationFlow:
    """Test end-to-end integration flow"""
    
    async def test_full_pipeline(self):
        """Test complete document upload and query flow"""
        
        # Step 1: Upload document
        file_content = b"""
        John Smith works at TechCorp in Delhi.
        He manages the Engineering Department.
        The department is working on Project Alpha.
        """
        files = {"file": ("test_doc.txt", io.BytesIO(file_content), "text/plain")}
        
        upload_response = client.post("/api/documents/upload", files=files)
        assert upload_response.status_code == 200
        doc_id = upload_response.json()["document_id"]
        
        # Step 2: Check graph stats
        stats_response = client.get("/api/graph/stats")
        assert stats_response.status_code == 200
        
        # Step 3: Query the knowledge
        query_data = {
            "query": "Who works at TechCorp?",
            "max_results": 10
        }
        
        query_response = client.post("/api/query", json=query_data)
        assert query_response.status_code == 200
        
        result = query_response.json()
        assert len(result["sources"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
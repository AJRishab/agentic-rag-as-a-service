"""
Graph Database Service
Unified interface for Neo4j and AWS Neptune with in-memory fallback
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import json
import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings


class GraphDBInterface(ABC):
    """Abstract interface for graph databases"""
    
    @abstractmethod
    async def create_node(self, label: str, properties: Dict[str, Any]) -> str:
        pass
    
    @abstractmethod
    async def create_relationship(self, source_id: str, target_id: str, 
                                   rel_type: str, properties: Dict[str, Any] = None) -> str:
        pass
    
    @abstractmethod
    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict]:
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, int]:
        pass


class Neo4jAdapter(GraphDBInterface):
    """Neo4j database adapter"""
    
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        # Use config settings if parameters not provided
        uri = uri or settings.NEO4J_URI
        user = user or settings.NEO4J_USER
        password = password or settings.NEO4J_PASSWORD
        try:
            from neo4j import GraphDatabase
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.available = True
        except Exception as e:
            print(f"Neo4j not available: {e}")
            self.available = False
            self.driver = None
    
    async def create_node(self, label: str, properties: Dict[str, Any]) -> str:
        if not self.available:
            return f"mock_{label}_{properties.get('name', 'node')}"
        
        with self.driver.session() as session:
            result = session.run(
                f"CREATE (n:{label} $props) RETURN id(n) as node_id",
                props=properties
            )
            return str(result.single()["node_id"])
    
    async def create_relationship(self, source_id: str, target_id: str, 
                                   rel_type: str, properties: Dict[str, Any] = None) -> str:
        if not self.available:
            return f"mock_rel_{source_id}_{target_id}"
        
        props = properties or {}
        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH (a), (b)
                WHERE id(a) = $source_id AND id(b) = $target_id
                CREATE (a)-[r:{rel_type} $props]->(b)
                RETURN id(r) as rel_id
                """,
                source_id=int(source_id),
                target_id=int(target_id),
                props=props
            )
            return str(result.single()["rel_id"])
    
    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict]:
        if not self.available:
            return []
        
        with self.driver.session() as session:
            result = session.run(query, **(params or {}))
            return [record.data() for record in result]
    
    async def get_stats(self) -> Dict[str, int]:
        if not self.available:
            return {'entities': 0, 'relationships': 0, 'attributes': 0}
        
        with self.driver.session() as session:
            # Count nodes
            node_result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = node_result.single()["count"]
            
            # Count relationships
            rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = rel_result.single()["count"]
            
            return {
                'entities': node_count,
                'relationships': rel_count,
                'attributes': node_count * 3  # Estimate
            }
    
    def close(self):
        if self.driver:
            self.driver.close()


class InMemoryGraphDB(GraphDBInterface):
    """In-memory graph database for testing without external dependencies"""
    
    def __init__(self):
        self.nodes = {}
        self.relationships = []
        self.node_counter = 0
        self.rel_counter = 0
    
    async def create_node(self, label: str, properties: Dict[str, Any]) -> str:
        node_id = str(self.node_counter)
        self.node_counter += 1
        
        self.nodes[node_id] = {
            'id': node_id,
            'label': label,
            'properties': properties
        }
        return node_id
    
    async def create_relationship(self, source_id: str, target_id: str, 
                                   rel_type: str, properties: Dict[str, Any] = None) -> str:
        rel_id = str(self.rel_counter)
        self.rel_counter += 1
        
        self.relationships.append({
            'id': rel_id,
            'source': source_id,
            'target': target_id,
            'type': rel_type,
            'properties': properties or {}
        })
        return rel_id
    
    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict]:
        # Simple query execution - pattern matching
        results = []
        
        if "MATCH (n)" in query:
            # Return all nodes
            results = list(self.nodes.values())
        elif "MATCH ()-[r]->()" in query:
            # Return all relationships
            results = self.relationships
        
        return results
    
    async def get_stats(self) -> Dict[str, int]:
        entity_types = {}
        for node in self.nodes.values():
            label = node['label']
            entity_types[label] = entity_types.get(label, 0) + 1
        
        return {
            'entities': len(self.nodes),
            'relationships': len(self.relationships),
            'attributes': sum(len(n['properties']) for n in self.nodes.values()),
            'entity_types': entity_types
        }


class GraphService:
    """Main graph service with pluggable backend"""
    
    def __init__(self, db_type: str = None):
        # Use config setting if not specified
        db_type = db_type or settings.GRAPH_DB_TYPE
        
        if db_type == "neo4j":
            self.db = Neo4jAdapter()
            if not self.db.available:
                print("Neo4j unavailable, falling back to in-memory")
                self.db = InMemoryGraphDB()
        else:
            self.db = InMemoryGraphDB()
        
        self.vector_store = {}  # Simple dict-based vector store
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive graph statistics"""
        return await self.db.get_stats()
    
    async def get_visualization_data(self, limit: int = 100) -> Dict[str, Any]:
        """Get graph data for visualization"""
        stats = await self.db.get_stats()
        
        # Get sample nodes and relationships
        nodes = await self.db.execute_query(f"MATCH (n) RETURN n LIMIT {limit}")
        relationships = await self.db.execute_query(
            f"MATCH (a)-[r]->(b) RETURN a, r, b LIMIT {limit}"
        )
        
        # Format for visualization
        vis_nodes = []
        vis_edges = []
        
        # For in-memory DB
        if isinstance(self.db, InMemoryGraphDB):
            for node in list(self.db.nodes.values())[:limit]:
                vis_nodes.append({
                    'id': node['id'],
                    'label': node['properties'].get('name', node['label']),
                    'type': node['label']
                })
            
            for rel in self.db.relationships[:limit]:
                vis_edges.append({
                    'from': rel['source'],
                    'to': rel['target'],
                    'label': rel['type']
                })
        
        return {
            'nodes': vis_nodes,
            'edges': vis_edges,
            'stats': stats
        }
    
    async def search_by_vector(self, query_embedding: List[float], k: int = 10) -> List[Dict]:
        """Vector similarity search"""
        # Simple cosine similarity
        from numpy import dot
        from numpy.linalg import norm
        
        results = []
        for key, item in self.vector_store.items():
            embedding = item['embedding']
            similarity = dot(query_embedding, embedding) / (norm(query_embedding) * norm(embedding))
            
            results.append({
                'id': key,
                'text': item['text'],
                'similarity': float(similarity),
                'metadata': item.get('metadata', {})
            })
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:k]
    
    async def search_by_graph(self, entity: str, depth: int = 2) -> List[Dict]:
        """Graph traversal search"""
        # Simple BFS traversal
        if isinstance(self.db, InMemoryGraphDB):
            # Find starting node
            start_nodes = [n for n in self.db.nodes.values() 
                          if entity.lower() in n['properties'].get('name', '').lower()]
            
            if not start_nodes:
                return []
            
            visited = set()
            results = []
            queue = [(start_nodes[0]['id'], 0)]
            
            while queue:
                node_id, curr_depth = queue.pop(0)
                
                if node_id in visited or curr_depth > depth:
                    continue
                
                visited.add(node_id)
                node = self.db.nodes.get(node_id)
                if node:
                    results.append({
                        'node': node,
                        'depth': curr_depth
                    })
                
                # Find connected nodes
                for rel in self.db.relationships:
                    if rel['source'] == node_id:
                        queue.append((rel['target'], curr_depth + 1))
                    elif rel['target'] == node_id:
                        queue.append((rel['source'], curr_depth + 1))
            
            return results
        
        return []
    
    async def search_by_filter(self, filters: Dict[str, Any]) -> List[Dict]:
        """Attribute-based filtering"""
        results = []
        
        if isinstance(self.db, InMemoryGraphDB):
            for node in self.db.nodes.values():
                match = True
                for key, value in filters.items():
                    if node['properties'].get(key) != value:
                        match = False
                        break
                
                if match:
                    results.append(node)
        
        return results
    
    async def reset(self):
        """Reset the entire graph"""
        if isinstance(self.db, InMemoryGraphDB):
            self.db.nodes.clear()
            self.db.relationships.clear()
            self.db.node_counter = 0
            self.db.rel_counter = 0
        
        self.vector_store.clear()
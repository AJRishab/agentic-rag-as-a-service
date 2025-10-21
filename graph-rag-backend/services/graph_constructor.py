"""
Graph Constructor Service
Builds knowledge graph from extracted ontology and embeddings
"""

import time
from typing import Dict, Any, List


class GraphConstructor:
    """Constructs knowledge graph from document processing results"""
    
    def __init__(self):
        from services.graph_service import GraphService
        self.graph_service = GraphService()
        self.entity_map = {}  # Maps entity names to node IDs
    
    async def build_graph(self, doc_id: str, ontology: Dict[str, Any], 
                         embeddings: Dict[str, Any]) -> Dict[str, Any]:
        """Build graph from ontology and embeddings"""
        start = time.time()
        
        entities = ontology.get('entities', [])
        relationships = ontology.get('relationships', [])
        
        # Create document node
        doc_node_id = await self.graph_service.db.create_node(
            'Document',
            {
                'id': doc_id,
                'name': f'Document_{doc_id[:8]}',
                'created_at': time.time()
            }
        )
        
        # Create entity nodes
        entity_count = 0
        for i, entity in enumerate(entities):
            entity_name = entity.get('name', f'Entity_{i}')
            entity_type = entity.get('type', 'Unknown')
            
            # Get embedding if available
            embedding = None
            if i < len(embeddings.get('entities', [])):
                embedding = embeddings['entities'][i]
            
            # Create node
            node_id = await self.graph_service.db.create_node(
                entity_type,
                {
                    'name': entity_name,
                    'type': entity_type,
                    'doc_id': doc_id,
                    **entity.get('attributes', {})
                }
            )
            
            # Store mapping
            self.entity_map[entity_name] = node_id
            
            # Link to document
            await self.graph_service.db.create_relationship(
                doc_node_id,
                node_id,
                'CONTAINS',
                {'confidence': 1.0}
            )
            
            # Store embedding in vector store
            if embedding:
                self.graph_service.vector_store[node_id] = {
                    'embedding': embedding,
                    'text': entity_name,
                    'metadata': {
                        'type': entity_type,
                        'doc_id': doc_id
                    }
                }
            
            entity_count += 1
        
        # Create relationships
        rel_count = 0
        for rel in relationships:
            source_name = rel.get('source')
            target_name = rel.get('target')
            rel_type = rel.get('type', 'RELATED_TO').upper().replace(' ', '_')
            
            # Get node IDs
            source_id = self.entity_map.get(source_name)
            target_id = self.entity_map.get(target_name)
            
            if source_id and target_id:
                await self.graph_service.db.create_relationship(
                    source_id,
                    target_id,
                    rel_type,
                    {'confidence': 0.8}
                )
                rel_count += 1
        
        # Store text chunks as embeddings
        chunks = embeddings.get('texts', [])
        chunk_embeddings = embeddings.get('chunks', [])
        
        for i, (chunk, embedding) in enumerate(zip(chunks, chunk_embeddings)):
            chunk_id = f"{doc_id}_chunk_{i}"
            self.graph_service.vector_store[chunk_id] = {
                'embedding': embedding,
                'text': chunk,
                'metadata': {
                    'doc_id': doc_id,
                    'chunk_index': i
                }
            }
        
        return {
            'agent': 'Graph Constructor',
            'action': 'Building Neo4j graph',
            'status': 'complete',
            'timestamp': time.time() - start,
            'result': {
                'entities': entity_count,
                'relationships': rel_count,
                'attributes': entity_count * 3  # Estimate
            }
        }
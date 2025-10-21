"""
Entity Resolution and Deduplication Service
Identifies and merges duplicate entities across documents
"""

import time
from typing import Dict, Any, List, Tuple
from difflib import SequenceMatcher
import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings


class EntityResolver:
    """Resolves and deduplicates entities"""
    
    def __init__(self):
        from services.graph_service import GraphService
        self.graph_service = GraphService()
        self.similarity_threshold = settings.ENTITY_SIMILARITY_THRESHOLD
    
    async def resolve_entities(self, doc_id: str) -> Dict[str, Any]:
        """Find and merge duplicate entities"""
        start = time.time()
        
        # Get all entities from the graph
        if hasattr(self.graph_service.db, 'nodes'):
            nodes = list(self.graph_service.db.nodes.values())
        else:
            nodes = await self.graph_service.db.execute_query("MATCH (n) RETURN n")
        
        # Group by type
        entity_groups = {}
        for node in nodes:
            node_type = node.get('label', 'Unknown')
            if node_type not in entity_groups:
                entity_groups[node_type] = []
            entity_groups[node_type].append(node)
        
        # Find duplicates within each type
        merged_count = 0
        for entity_type, entities in entity_groups.items():
            duplicates = self._find_duplicates(entities)
            
            for dup_group in duplicates:
                if len(dup_group) > 1:
                    await self._merge_entities(dup_group)
                    merged_count += len(dup_group) - 1
        
        return {
            'merged_entities': merged_count,
            'total_entities': len(nodes),
            'processing_time': time.time() - start
        }
    
    def _find_duplicates(self, entities: List[Dict]) -> List[List[Dict]]:
        """Find duplicate entities using similarity matching"""
        duplicates = []
        processed = set()
        
        for i, entity1 in enumerate(entities):
            if i in processed:
                continue
            
            dup_group = [entity1]
            name1 = entity1.get('properties', {}).get('name', '').lower()
            
            for j, entity2 in enumerate(entities[i+1:], start=i+1):
                if j in processed:
                    continue
                
                name2 = entity2.get('properties', {}).get('name', '').lower()
                
                # Check similarity
                similarity = self._calculate_similarity(name1, name2)
                
                if similarity >= self.similarity_threshold:
                    dup_group.append(entity2)
                    processed.add(j)
            
            if len(dup_group) > 1:
                duplicates.append(dup_group)
            
            processed.add(i)
        
        return duplicates
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity using various methods"""
        
        # Exact match
        if str1 == str2:
            return 1.0
        
        # Sequence matcher
        seq_sim = SequenceMatcher(None, str1, str2).ratio()
        
        # Token overlap
        tokens1 = set(str1.split())
        tokens2 = set(str2.split())
        
        if tokens1 and tokens2:
            token_sim = len(tokens1 & tokens2) / len(tokens1 | tokens2)
        else:
            token_sim = 0.0
        
        # Combined similarity
        return (seq_sim * 0.6) + (token_sim * 0.4)
    
    async def _merge_entities(self, entities: List[Dict]):
        """Merge duplicate entities into a single canonical entity"""
        
        # Choose canonical entity (first one or most complete)
        canonical = max(entities, key=lambda e: len(e.get('properties', {})))
        canonical_id = canonical['id']
        
        # Merge properties
        merged_props = canonical.get('properties', {}).copy()
        
        for entity in entities:
            if entity['id'] == canonical_id:
                continue
            
            # Merge properties
            for key, value in entity.get('properties', {}).items():
                if key not in merged_props:
                    merged_props[key] = value
            
            # Update relationships to point to canonical
            await self._redirect_relationships(entity['id'], canonical_id)
            
            # Remove duplicate node
            if hasattr(self.graph_service.db, 'nodes'):
                self.graph_service.db.nodes.pop(entity['id'], None)
        
        # Update canonical entity with merged properties
        if hasattr(self.graph_service.db, 'nodes'):
            self.graph_service.db.nodes[canonical_id]['properties'] = merged_props
    
    async def _redirect_relationships(self, old_id: str, new_id: str):
        """Redirect relationships from old entity to new canonical entity"""
        
        if hasattr(self.graph_service.db, 'relationships'):
            for rel in self.graph_service.db.relationships:
                if rel['source'] == old_id:
                    rel['source'] = new_id
                if rel['target'] == old_id:
                    rel['target'] = new_id
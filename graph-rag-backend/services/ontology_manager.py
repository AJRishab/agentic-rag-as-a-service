"""
Ontology Manager Service
Manages and refines knowledge graph ontology using LLM assistance
"""

import json
from typing import Dict, Any, List
import time

import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings


class OntologyManager:
    """Manages ontology schema and refinement"""
    
    def __init__(self):
        from services.graph_service import GraphService
        self.graph_service = GraphService()
        self.ontology = {
            'version': '1.0',
            'entity_types': [],
            'relationship_types': [],
            'attribute_schema': {},
            'hierarchies': []
        }
    
    async def get_ontology(self) -> Dict[str, Any]:
        """Get current ontology schema"""
        
        # Extract ontology from graph
        stats = await self.graph_service.get_stats()
        
        entity_types = []
        if 'entity_types' in stats:
            for entity_type, count in stats['entity_types'].items():
                entity_types.append({
                    'name': entity_type,
                    'count': count,
                    'properties': self._infer_properties(entity_type)
                })
        
        # Get relationship types
        relationship_types = []
        if hasattr(self.graph_service.db, 'relationships'):
            rel_types = set()
            for rel in self.graph_service.db.relationships:
                rel_types.add(rel['type'])
            
            for rel_type in rel_types:
                count = sum(1 for r in self.graph_service.db.relationships if r['type'] == rel_type)
                relationship_types.append({
                    'name': rel_type,
                    'count': count
                })
        
        return {
            'version': self.ontology['version'],
            'entity_types': entity_types,
            'relationship_types': relationship_types,
            'total_entities': stats.get('entities', 0),
            'total_relationships': stats.get('relationships', 0)
        }
    
    def _infer_properties(self, entity_type: str) -> List[Dict[str, str]]:
        """Infer properties for an entity type"""
        
        if not hasattr(self.graph_service.db, 'nodes'):
            return []
        
        # Find all nodes of this type
        nodes = [n for n in self.graph_service.db.nodes.values() 
                if n['label'] == entity_type]
        
        if not nodes:
            return []
        
        # Collect all unique properties
        properties = {}
        for node in nodes:
            for key, value in node.get('properties', {}).items():
                if key not in properties:
                    properties[key] = type(value).__name__
        
        return [
            {'name': key, 'type': val_type}
            for key, val_type in properties.items()
        ]
    
    async def refine_with_llm(self, refinement: Dict[str, Any]) -> Dict[str, Any]:
        """Refine ontology using LLM assistance"""
        
        action = refinement.get('action')
        
        if action == 'suggest_relationships':
            return await self._suggest_relationships(refinement)
        elif action == 'merge_entity_types':
            return await self._merge_entity_types(refinement)
        elif action == 'add_hierarchy':
            return await self._add_hierarchy(refinement)
        elif action == 'improve_schema':
            return await self._improve_schema()
        else:
            return {'error': 'Unknown action'}
    
    async def _suggest_relationships(self, refinement: Dict) -> Dict:
        """Suggest new relationships using LLM"""
        
        entity_type1 = refinement.get('entity_type1')
        entity_type2 = refinement.get('entity_type2')
        
        prompt = f"""Suggest meaningful relationships between {entity_type1} and {entity_type2}.
        
List 3-5 potential relationship types that make semantic sense.
Format: relationship_name (direction)

Relationships:"""
        
        try:
            import requests
            response = requests.post(
                settings.OLLAMA_ENDPOINT,
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=20
            )
            
            if response.status_code == 200:
                suggestions = response.json().get('response', '')
                relationships = [s.strip() for s in suggestions.split('\n') if s.strip()]
            else:
                relationships = self._default_relationships(entity_type1, entity_type2)
        except:
            relationships = self._default_relationships(entity_type1, entity_type2)
        
        return {
            'suggestions': relationships[:5],
            'source': 'llm' if len(relationships) > 2 else 'default'
        }
    
    def _default_relationships(self, type1: str, type2: str) -> List[str]:
        """Default relationship suggestions"""
        return [
            f"{type1}_RELATED_TO_{type2}",
            f"{type1}_CONTAINS_{type2}",
            f"{type1}_WORKS_WITH_{type2}",
            f"{type1}_MANAGES_{type2}"
        ]
    
    async def _merge_entity_types(self, refinement: Dict) -> Dict:
        """Merge similar entity types"""
        
        source_type = refinement.get('source_type')
        target_type = refinement.get('target_type')
        
        if not hasattr(self.graph_service.db, 'nodes'):
            return {'error': 'Graph database not available'}
        
        merged_count = 0
        
        # Find all nodes of source type and change to target type
        for node_id, node in self.graph_service.db.nodes.items():
            if node['label'] == source_type:
                node['label'] = target_type
                merged_count += 1
        
        return {
            'merged_count': merged_count,
            'source_type': source_type,
            'target_type': target_type
        }
    
    async def _add_hierarchy(self, refinement: Dict) -> Dict:
        """Add hierarchical relationship"""
        
        parent_type = refinement.get('parent_type')
        child_type = refinement.get('child_type')
        
        # Add to ontology
        hierarchy = {
            'parent': parent_type,
            'child': child_type,
            'relationship': 'IS_A'
        }
        
        self.ontology['hierarchies'].append(hierarchy)
        
        return {
            'hierarchy': hierarchy,
            'status': 'added'
        }
    
    async def _improve_schema(self) -> Dict:
        """Use LLM to suggest schema improvements"""
        
        current_ontology = await self.get_ontology()
        
        prompt = f"""Analyze this knowledge graph ontology and suggest improvements:

Entity Types: {[e['name'] for e in current_ontology['entity_types']]}
Relationship Types: {[r['name'] for r in current_ontology['relationship_types']]}

Suggest 3 improvements:
1. Missing entity types
2. Missing relationships
3. Schema optimizations

Suggestions:"""
        
        try:
            import requests
            response = requests.post(
                settings.OLLAMA_ENDPOINT,
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                suggestions = response.json().get('response', 'No suggestions available')
            else:
                suggestions = "Unable to generate suggestions"
        except:
            suggestions = "LLM service unavailable. Default suggestions: Add temporal relationships, consider entity attributes, implement entity hierarchies."
        
        return {
            'current_ontology': current_ontology,
            'suggestions': suggestions,
            'timestamp': time.time()
        }
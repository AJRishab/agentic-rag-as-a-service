"""
Cypher Query Generator
Automatically generates Neo4j Cypher queries from natural language
"""

import re
from typing import Dict, Any, List, Optional


class CypherGenerator:
    """Generates Cypher queries from natural language"""
    
    def __init__(self):
        self.query_patterns = {
            'find': self._generate_find_query,
            'list': self._generate_list_query,
            'count': self._generate_count_query,
            'relationship': self._generate_relationship_query,
            'path': self._generate_path_query
        }
    
    async def generate_cypher(self, natural_query: str, ontology: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Cypher query from natural language"""
        
        # Analyze query intent
        intent = self._detect_intent(natural_query)
        
        # Extract entities and relationships
        entities = self._extract_entities(natural_query, ontology)
        relationships = self._extract_relationships(natural_query)
        filters = self._extract_filters(natural_query)
        
        # Generate appropriate Cypher query
        generator = self.query_patterns.get(intent, self._generate_generic_query)
        cypher, params = generator(entities, relationships, filters)
        
        return {
            'cypher': cypher,
            'parameters': params,
            'intent': intent,
            'confidence': self._calculate_confidence(natural_query, cypher)
        }
    
    def _detect_intent(self, query: str) -> str:
        """Detect query intent from natural language"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['find', 'search', 'get', 'show']):
            return 'find'
        elif any(word in query_lower for word in ['list', 'all', 'every']):
            return 'list'
        elif any(word in query_lower for word in ['count', 'how many', 'number of']):
            return 'count'
        elif any(word in query_lower for word in ['connect', 'relate', 'link', 'between']):
            return 'relationship'
        elif any(word in query_lower for word in ['path', 'route', 'connection']):
            return 'path'
        else:
            return 'find'
    
    def _extract_entities(self, query: str, ontology: Dict) -> List[str]:
        """Extract entity types from query"""
        entities = []
        query_lower = query.lower()
        
        # Check against known entity types from ontology
        for entity_type in ontology.get('entity_types', []):
            type_name = entity_type.get('name', '').lower()
            if type_name in query_lower:
                entities.append(entity_type['name'])
        
        # Extract capitalized words as potential entities
        capitalized = re.findall(r'\b[A-Z][a-z]+\b', query)
        entities.extend(capitalized)
        
        return list(set(entities))
    
    def _extract_relationships(self, query: str) -> List[str]:
        """Extract relationship keywords"""
        relationships = []
        query_lower = query.lower()
        
        # Common relationship verbs
        rel_verbs = ['manages', 'works', 'leads', 'reports', 'owns', 'contains']
        
        for verb in rel_verbs:
            if verb in query_lower:
                relationships.append(verb.upper())
        
        return relationships
    
    def _extract_filters(self, query: str) -> Dict[str, Any]:
        """Extract filter conditions"""
        filters = {}
        
        # Location filters
        location_match = re.search(r'in\s+([A-Z][a-z]+)', query)
        if location_match:
            filters['location'] = location_match.group(1)
        
        # Name filters
        name_match = re.search(r'named\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', query)
        if name_match:
            filters['name'] = name_match.group(1)
        
        # Date filters
        year_match = re.search(r'(20\d{2})', query)
        if year_match:
            filters['year'] = year_match.group(1)
        
        return filters
    
    def _generate_find_query(self, entities: List[str], 
                            relationships: List[str], 
                            filters: Dict) -> tuple:
        """Generate MATCH query for finding entities"""
        
        if not entities:
            entity_label = "n"
            cypher = f"MATCH ({entity_label})"
        else:
            entity_label = entities[0]
            cypher = f"MATCH (n:{entity_label})"
        
        # Add filters
        where_clauses = []
        params = {}
        
        for key, value in filters.items():
            param_name = f"param_{key}"
            where_clauses.append(f"n.{key} = ${param_name}")
            params[param_name] = value
        
        if where_clauses:
            cypher += " WHERE " + " AND ".join(where_clauses)
        
        cypher += " RETURN n LIMIT 10"
        
        return cypher, params
    
    def _generate_list_query(self, entities: List[str], 
                            relationships: List[str], 
                            filters: Dict) -> tuple:
        """Generate query to list all entities"""
        
        entity_label = entities[0] if entities else "n"
        cypher = f"MATCH (n:{entity_label}) RETURN n.name as name, n.type as type LIMIT 50"
        
        return cypher, {}
    
    def _generate_count_query(self, entities: List[str], 
                              relationships: List[str], 
                              filters: Dict) -> tuple:
        """Generate COUNT query"""
        
        entity_label = entities[0] if entities else "n"
        cypher = f"MATCH (n:{entity_label})"
        
        params = {}
        if filters:
            where_clauses = []
            for key, value in filters.items():
                param_name = f"param_{key}"
                where_clauses.append(f"n.{key} = ${param_name}")
                params[param_name] = value
            
            cypher += " WHERE " + " AND ".join(where_clauses)
        
        cypher += " RETURN count(n) as count"
        
        return cypher, params
    
    def _generate_relationship_query(self, entities: List[str], 
                                     relationships: List[str], 
                                     filters: Dict) -> tuple:
        """Generate query for relationships between entities"""
        
        if len(entities) >= 2:
            entity1 = entities[0]
            entity2 = entities[1]
            
            rel_type = relationships[0] if relationships else "r"
            
            cypher = f"""
            MATCH (a:{entity1})-[r:{rel_type}]->(b:{entity2})
            RETURN a.name as source, type(r) as relationship, b.name as target
            LIMIT 20
            """
        else:
            # Generic relationship query
            cypher = """
            MATCH (a)-[r]->(b)
            RETURN a.name as source, type(r) as relationship, b.name as target
            LIMIT 20
            """
        
        return cypher.strip(), {}
    
    def _generate_path_query(self, entities: List[str], 
                            relationships: List[str], 
                            filters: Dict) -> tuple:
        """Generate shortest path query"""
        
        if len(entities) >= 2:
            cypher = f"""
            MATCH path = shortestPath((a:{entities[0]})-[*..5]-(b:{entities[1]}))
            RETURN path
            LIMIT 5
            """
        else:
            cypher = """
            MATCH path = (a)-[*..3]-(b)
            RETURN path
            LIMIT 10
            """
        
        return cypher.strip(), {}
    
    def _generate_generic_query(self, entities: List[str], 
                                relationships: List[str], 
                                filters: Dict) -> tuple:
        """Fallback generic query"""
        
        cypher = "MATCH (n) RETURN n LIMIT 10"
        return cypher, {}
    
    def _calculate_confidence(self, query: str, cypher: str) -> float:
        """Calculate confidence in generated query"""
        
        confidence = 0.5  # Base confidence
        
        # Increase confidence if query has clear structure
        if "MATCH" in cypher and "RETURN" in cypher:
            confidence += 0.2
        
        # Increase if filters are present
        if "WHERE" in cypher:
            confidence += 0.15
        
        # Increase if specific entity types found
        if re.findall(r':\w+', cypher):
            confidence += 0.15
        
        return min(confidence, 0.95)


class GremlinGenerator:
    """Generates Gremlin queries for AWS Neptune"""
    
    async def generate_gremlin(self, natural_query: str) -> Dict[str, Any]:
        """Generate Gremlin query from natural language"""
        
        query_lower = natural_query.lower()
        
        # Simple Gremlin query patterns
        if 'find' in query_lower or 'search' in query_lower:
            gremlin = "g.V().hasLabel('Entity').limit(10)"
        elif 'count' in query_lower:
            gremlin = "g.V().count()"
        elif 'relationship' in query_lower or 'connected' in query_lower:
            gremlin = "g.V().outE().inV().path().limit(10)"
        else:
            gremlin = "g.V().limit(10)"
        
        return {
            'gremlin': gremlin,
            'confidence': 0.7
        }
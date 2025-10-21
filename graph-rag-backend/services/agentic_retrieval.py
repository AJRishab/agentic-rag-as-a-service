"""
Agentic Retrieval System
Multi-agent orchestration for intelligent query execution
"""

import time
import asyncio
from typing import List, Dict, Any, AsyncGenerator
import json
from enum import Enum

import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings


class AgentType(Enum):
    COORDINATOR = "Coordinator Agent"
    VECTOR_SEARCH = "Vector Search Agent"
    GRAPH_TRAVERSAL = "Graph Traversal Agent"
    FILTER = "Filter Agent"
    SYNTHESIS = "Synthesis Agent"
    CYPHER_GEN = "Cypher Generation Agent"


class AgenticRetrieval:
    """Main agentic retrieval orchestrator"""
    
    def __init__(self):
        from services.graph_service import GraphService
        self.graph_service = GraphService()
        self.reasoning_chain = []
    
    async def execute_query(self, query: str, max_results: int = 10,
                           use_vector: bool = True, use_graph: bool = True,
                           use_filter: bool = True) -> Dict[str, Any]:
        """Execute query with multi-agent coordination"""
        
        self.reasoning_chain = []
        start_time = time.time()
        
        # Step 1: Coordinator analyzes query
        await self._add_reasoning_step(
            AgentType.COORDINATOR,
            "Analyzing query complexity and determining retrieval strategy"
        )
        
        query_analysis = await self._analyze_query(query)
        
        # Step 2: Parallel retrieval from multiple sources
        retrieval_tasks = []
        
        if use_vector:
            retrieval_tasks.append(self._vector_search(query, max_results))
        
        if use_graph:
            retrieval_tasks.append(self._graph_search(query, query_analysis))
        
        if use_filter and query_analysis.get('filters'):
            retrieval_tasks.append(self._filter_search(query_analysis['filters']))
        
        # Execute searches in parallel
        results = await asyncio.gather(*retrieval_tasks, return_exceptions=True)
        
        # Step 3: Synthesis
        await self._add_reasoning_step(
            AgentType.SYNTHESIS,
            "Ranking and merging results from all sources"
        )
        
        synthesized = await self._synthesize_results(results, query)
        
        # Calculate confidence
        confidence = self._calculate_confidence(synthesized)
        
        query_time = (time.time() - start_time) * 1000
        
        return {
            'answer': synthesized['answer'],
            'sources': synthesized['sources'],
            'reasoning_chain': self.reasoning_chain,
            'confidence': confidence,
            'query_time_ms': query_time
        }
    
    async def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine retrieval strategy"""
        query_lower = query.lower()
        
        analysis = {
            'type': 'general',
            'entities': [],
            'filters': {},
            'requires_graph': False,
            'requires_vector': True
        }
        
        # Detect question type
        if any(word in query_lower for word in ['who', 'what', 'where']):
            analysis['type'] = 'factual'
            analysis['requires_graph'] = True
        elif any(word in query_lower for word in ['how', 'why', 'explain']):
            analysis['type'] = 'explanatory'
            analysis['requires_vector'] = True
        elif any(word in query_lower for word in ['find', 'search', 'list']):
            analysis['type'] = 'retrieval'
            analysis['requires_graph'] = True
        
        # Extract potential filters
        if 'in' in query_lower and any(city in query_lower for city in ['delhi', 'mumbai', 'bangalore']):
            for city in ['delhi', 'mumbai', 'bangalore']:
                if city in query_lower:
                    analysis['filters']['location'] = city.capitalize()
        
        # Extract entities (simple capitalized words)
        import re
        potential_entities = re.findall(r'\b[A-Z][a-z]+\b', query)
        analysis['entities'] = potential_entities
        
        return analysis
    
    async def _vector_search(self, query: str, k: int = 10) -> Dict[str, Any]:
        """Vector similarity search"""
        await self._add_reasoning_step(
            AgentType.VECTOR_SEARCH,
            "Finding semantically similar content using embeddings"
        )
        
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            query_embedding = model.encode(query).tolist()
        except:
            # Fallback to mock embedding
            query_embedding = [0.1] * 384
        
        results = await self.graph_service.search_by_vector(query_embedding, k)
        
        return {
            'type': 'vector',
            'results': results
        }
    
    async def _graph_search(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Graph traversal search"""
        await self._add_reasoning_step(
            AgentType.GRAPH_TRAVERSAL,
            "Exploring relationship paths in knowledge graph"
        )
        
        results = []
        
        # Search for entities mentioned in query
        for entity in analysis.get('entities', []):
            graph_results = await self.graph_service.search_by_graph(entity, depth=2)
            results.extend(graph_results)
        
        # If no entities, try keyword search
        if not results:
            # Simple keyword extraction
            words = query.split()
            for word in words:
                if len(word) > 3 and word[0].isupper():
                    graph_results = await self.graph_service.search_by_graph(word, depth=2)
                    results.extend(graph_results)
        
        return {
            'type': 'graph',
            'results': results
        }
    
    async def _filter_search(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Attribute-based filtering"""
        await self._add_reasoning_step(
            AgentType.FILTER,
            f"Applying metadata constraints: {filters}"
        )
        
        results = await self.graph_service.search_by_filter(filters)
        
        return {
            'type': 'filter',
            'results': results
        }
    
    async def _synthesize_results(self, results: List[Dict], query: str) -> Dict[str, Any]:
        """Combine and rank results from all sources"""
        
        all_sources = []
        combined_context = []
        
        for result_set in results:
            if isinstance(result_set, Exception):
                continue
            
            result_type = result_set.get('type')
            items = result_set.get('results', [])
            
            if result_type == 'vector':
                for item in items[:5]:  # Top 5 vector results
                    all_sources.append({
                        'type': 'vector',
                        'content': item.get('text', ''),
                        'confidence': item.get('similarity', 0.0),
                        'metadata': {'similarity': f"{item.get('similarity', 0)*100:.0f}%"}
                    })
                    combined_context.append(item.get('text', ''))
            
            elif result_type == 'graph':
                for item in items[:5]:  # Top 5 graph results
                    node = item.get('node', {})
                    depth = item.get('depth', 0)
                    
                    node_info = f"{node.get('label', 'Node')}: {node.get('properties', {}).get('name', 'Unknown')}"
                    all_sources.append({
                        'type': 'graph',
                        'content': f"Graph path at depth {depth}: {node_info}",
                        'confidence': max(0.3, 1.0 - (depth * 0.2)),
                        'metadata': {'depth': depth}
                    })
                    combined_context.append(node_info)
            
            elif result_type == 'filter':
                for item in items[:3]:  # Top 3 filtered results
                    all_sources.append({
                        'type': 'filter',
                        'content': f"Filtered match: {item.get('label', 'Node')} - {item.get('properties', {}).get('name', 'Unknown')}",
                        'confidence': 0.9,
                        'metadata': item.get('properties', {})
                    })
        
        # Generate answer using LLM or template
        answer = await self._generate_answer(query, combined_context, all_sources)
        
        return {
            'answer': answer,
            'sources': all_sources[:10]  # Limit to top 10 sources
        }
    
    async def _generate_answer(self, query: str, context: List[str], sources: List[Dict]) -> str:
        """Generate answer using LLM or template-based approach"""
        
        # Try LLM-based generation
        try:
            prompt = f"""Based on the following context, answer the question.

Context:
{chr(10).join(context[:3])}

Question: {query}

Answer (be concise and specific):"""
            
            answer = await self._call_llm(prompt)
            return answer
        except:
            # Fallback to template-based answer
            return self._template_answer(query, sources)
    
    async def _call_llm(self, prompt: str) -> str:
        """Call LLM for answer generation"""
        import requests
        
        try:
            # Try Ollama
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
                result = response.json()
                return result.get('response', '').strip()
        except:
            pass
        
        raise Exception("LLM unavailable")
    
    def _template_answer(self, query: str, sources: List[Dict]) -> str:
        """Generate template-based answer"""
        
        if not sources:
            return "I couldn't find relevant information to answer your query. Please try rephrasing or provide more context."
        
        # Count source types
        vector_count = sum(1 for s in sources if s['type'] == 'vector')
        graph_count = sum(1 for s in sources if s['type'] == 'graph')
        filter_count = sum(1 for s in sources if s['type'] == 'filter')
        
        # Build answer
        answer_parts = []
        
        if graph_count > 0:
            answer_parts.append(f"Based on the knowledge graph analysis")
        if vector_count > 0:
            answer_parts.append(f"semantic search results")
        if filter_count > 0:
            answer_parts.append(f"filtered matches")
        
        answer = f"{' and '.join(answer_parts)}, I found {len(sources)} relevant pieces of information. "
        
        # Add specific findings
        top_source = sources[0]
        if top_source['type'] == 'graph':
            answer += top_source['content']
        elif top_source['type'] == 'vector':
            answer += f"The most relevant content indicates: {top_source['content'][:200]}..."
        else:
            answer += f"The filtered results show: {top_source['content']}"
        
        return answer
    
    def _calculate_confidence(self, synthesized: Dict) -> float:
        """Calculate overall confidence score"""
        sources = synthesized.get('sources', [])
        
        if not sources:
            return 0.0
        
        # Average confidence weighted by source type
        weights = {'vector': 0.4, 'graph': 0.4, 'filter': 0.2}
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for source in sources:
            source_type = source['type']
            confidence = source['confidence']
            weight = weights.get(source_type, 0.3)
            
            weighted_sum += confidence * weight
            total_weight += weight
        
        return min(0.95, weighted_sum / total_weight if total_weight > 0 else 0.5)
    
    async def _add_reasoning_step(self, agent: AgentType, action: str):
        """Add step to reasoning chain"""
        step = {
            'agent': agent.value,
            'action': action,
            'status': 'complete',
            'timestamp': time.time()
        }
        self.reasoning_chain.append(step)
        await asyncio.sleep(0.1)  # Simulate processing time
    
    async def stream_query(self, query: str) -> AsyncGenerator[str, None]:
        """Stream query results with reasoning chain"""
        
        # Stream reasoning steps
        for step in self.reasoning_chain:
            yield json.dumps(step)
            await asyncio.sleep(0.2)
        
        # Execute query
        result = await self.execute_query(query)
        
        # Stream final result
        yield json.dumps(result)
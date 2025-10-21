"""
Metrics Collector Service
Tracks system performance and usage metrics
"""

import time
from typing import Dict, Any
from collections import defaultdict


class MetricsCollector:
    """Collects and reports system metrics"""
    
    def __init__(self):
        self.metrics = {
            'queries': {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'avg_latency_ms': 0,
                'latencies': []
            },
            'documents': {
                'total_processed': 0,
                'total_entities': 0,
                'total_relationships': 0,
                'processing_times': []
            },
            'graph': {
                'total_nodes': 0,
                'total_edges': 0,
                'storage_mb': 0
            },
            'agents': {
                'coordinator': {'calls': 0, 'avg_time_ms': 0},
                'vector_search': {'calls': 0, 'avg_time_ms': 0},
                'graph_traversal': {'calls': 0, 'avg_time_ms': 0},
                'filter': {'calls': 0, 'avg_time_ms': 0},
                'synthesis': {'calls': 0, 'avg_time_ms': 0}
            },
            'system': {
                'uptime_seconds': 0,
                'start_time': time.time()
            }
        }
    
    async def get_all_metrics(self) -> Dict[str, Any]:
        """Get all system metrics"""
        
        # Update uptime
        self.metrics['system']['uptime_seconds'] = int(
            time.time() - self.metrics['system']['start_time']
        )
        
        # Calculate averages
        if self.metrics['queries']['latencies']:
            self.metrics['queries']['avg_latency_ms'] = sum(
                self.metrics['queries']['latencies']
            ) / len(self.metrics['queries']['latencies'])
        
        return self.metrics
    
    def record_query(self, latency_ms: float, success: bool = True):
        """Record query metrics"""
        self.metrics['queries']['total'] += 1
        
        if success:
            self.metrics['queries']['successful'] += 1
        else:
            self.metrics['queries']['failed'] += 1
        
        self.metrics['queries']['latencies'].append(latency_ms)
        
        # Keep only last 100 latencies
        if len(self.metrics['queries']['latencies']) > 100:
            self.metrics['queries']['latencies'].pop(0)
    
    def record_document_processing(self, entities: int, relationships: int, 
                                   processing_time_ms: float):
        """Record document processing metrics"""
        self.metrics['documents']['total_processed'] += 1
        self.metrics['documents']['total_entities'] += entities
        self.metrics['documents']['total_relationships'] += relationships
        self.metrics['documents']['processing_times'].append(processing_time_ms)
        
        if len(self.metrics['documents']['processing_times']) > 100:
            self.metrics['documents']['processing_times'].pop(0)
    
    def record_agent_call(self, agent_name: str, time_ms: float):
        """Record agent execution metrics"""
        agent_key = agent_name.lower().replace(' ', '_').replace('agent', '').strip('_')
        
        if agent_key in self.metrics['agents']:
            self.metrics['agents'][agent_key]['calls'] += 1
            
            # Update average time
            current_avg = self.metrics['agents'][agent_key]['avg_time_ms']
            current_calls = self.metrics['agents'][agent_key]['calls']
            
            new_avg = ((current_avg * (current_calls - 1)) + time_ms) / current_calls
            self.metrics['agents'][agent_key]['avg_time_ms'] = new_avg
    
    def update_graph_metrics(self, nodes: int, edges: int):
        """Update graph size metrics"""
        self.metrics['graph']['total_nodes'] = nodes
        self.metrics['graph']['total_edges'] = edges
        
        # Estimate storage (rough approximation)
        self.metrics['graph']['storage_mb'] = (nodes * 0.001) + (edges * 0.0005)
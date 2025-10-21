"""
Services Package
Core services for Graph RAG platform
"""

from .document_processor import DocumentProcessor
from .graph_constructor import GraphConstructor
from .graph_service import GraphService, GraphDBInterface, Neo4jAdapter, InMemoryGraphDB
from .entity_resolver import EntityResolver
from .ontology_manager import OntologyManager
from .agentic_retrieval import AgenticRetrieval
from .metrics_collector import MetricsCollector

__all__ = [
    'DocumentProcessor',
    'GraphConstructor',
    'GraphService',
    'GraphDBInterface',
    'Neo4jAdapter',
    'InMemoryGraphDB',
    'EntityResolver',
    'OntologyManager',
    'AgenticRetrieval',
    'MetricsCollector'
]

__version__ = '1.0.0'
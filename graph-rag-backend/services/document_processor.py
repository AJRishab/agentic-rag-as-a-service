"""
Document Processing Pipeline
Extracts text, generates embeddings, and prepares for graph construction
"""

import time
import uuid
import re
from typing import List, Dict, Any, Tuple
from datetime import datetime
import json
import io

# For free LLM - using Ollama or HuggingFace
import requests

import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

# --- Persistent Storage for Processed Documents ---
PROCESSED_DOCS_FILE = "processed_docs.json"
_processed_docs: List[Dict[str, Any]] = []

def _load_processed_docs():
    """Load the list of processed documents from a file."""
    global _processed_docs
    if os.path.exists(PROCESSED_DOCS_FILE):
        try:
            with open(PROCESSED_DOCS_FILE, "r") as f:
                _processed_docs = json.load(f)
        except json.JSONDecodeError:
            _processed_docs = []

def _save_processed_docs():
    """Save the list of processed documents to a file."""
    with open(PROCESSED_DOCS_FILE, "w") as f:
        json.dump(_processed_docs, f, indent=2)

# Load documents on startup
_load_processed_docs()
# ---

class DocumentProcessor:
    def __init__(self):
        self.llm_endpoint = settings.OLLAMA_ENDPOINT
        self.ollama_model = settings.OLLAMA_MODEL
        
    async def process_document(self, filename: str, content: bytes) -> Dict[str, Any]:
        """Main document processing pipeline"""
        doc_id = str(uuid.uuid4())
        stages = []
        start_time = time.time()
        
        # Stage 1: Text Extraction
        stages.append(await self._stage_extract_text(content, filename))
        text = stages[-1].get('result', '')
        
        if not text:
            raise ValueError("Text extraction failed or document is empty.")

        # Stage 2: Chunk Text
        stages.append(await self._stage_chunk_text(text))
        chunks = stages[-1].get('result', [])
        
        # Stage 3: Extract Entities & Relationships
        stages.append(await self._stage_extract_ontology(chunks))
        ontology = stages[-1].get('result', {})
        
        # Stage 4: Generate Embeddings
        stages.append(await self._stage_generate_embeddings(chunks, ontology))
        embeddings = stages[-1].get('result', {})
        
        # Stage 5: Construct Graph
        from services.graph_constructor import GraphConstructor
        constructor = GraphConstructor()
        stages.append(await constructor.build_graph(doc_id, ontology, embeddings))
        graph_stats = stages[-1].get('result', {})
        
        # Stage 6: Entity Resolution
        stages.append(await self._stage_entity_resolution(doc_id))
        
        # Save document metadata
        doc_metadata = {
            'id': doc_id,
            'filename': filename,
            'processed_at': datetime.now().isoformat(),
            'chunks': len(chunks),
            'graph_stats': graph_stats
        }
        _processed_docs.append(doc_metadata)
        _save_processed_docs()  # Save after each processing
        
        return {
            'document_id': doc_id,
            'filename': filename,
            'stages': [self._format_stage(s) for s in stages],
            'graph_stats': graph_stats
        }
    
    async def _stage_extract_text(self, content: bytes, filename: str) -> Dict:
        """Extract text from various file formats"""
        start = time.time()
        text = ""
        try:
            if filename.endswith('.txt'):
                text = content.decode('utf-8')
            elif filename.endswith('.pdf'):
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                for page in pdf_reader.pages:
                    text += page.extract_text()
            elif filename.endswith('.docx'):
                import docx
                doc = docx.Document(io.BytesIO(content))
                for para in doc.paragraphs:
                    text += para.text + '\n'
            else:
                text = content.decode('utf-8', errors='ignore')
            
            return {
                'agent': 'Document Parser',
                'action': 'Extracting text chunks',
                'status': 'complete',
                'timestamp': time.time() - start,
                'result': text
            }
        except Exception as e:
            return {
                'agent': 'Document Parser',
                'action': f'Text extraction failed: {e}',
                'status': 'error',
                'timestamp': time.time() - start,
                'error': str(e),
                'result': ''
            }
    
    async def _stage_chunk_text(self, text: str, chunk_size: int = 500) -> Dict:
        """Split text into chunks"""
        start = time.time()
        
        # Simple sentence-aware chunking
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return {
            'agent': 'Text Chunker',
            'action': f'Created {len(chunks)} text chunks',
            'status': 'complete',
            'timestamp': time.time() - start,
            'result': chunks
        }
    
    async def _stage_extract_ontology(self, chunks: List[str]) -> Dict:
        """Extract entities and relationships using LLM"""
        start = time.time()
        
        # Combine chunks for ontology extraction
        sample_text = ' '.join(chunks[:3])  # Use first 3 chunks
        
        prompt = f"""Extract entities and relationships from the following text.
        
Text: {sample_text}

Output as JSON with this structure:
{{
    "entities": [
        {{"name": "entity name", "type": "entity type", "attributes": {{}}}},
    ],
    "relationships": [
        {{"source": "entity1", "target": "entity2", "type": "relationship type"}},
    ]
}}

JSON:"""
        
        try:
            # Try Ollama (free, local LLM)
            ontology = await self._call_ollama(prompt)
        except Exception as e:
            # Fallback to rule-based extraction
            print(f"LLM call failed: {e}. Falling back to rule-based extraction.")
            ontology = self._fallback_extraction(sample_text)
        
        return {
            'agent': 'LLM Ontology Extractor',
            'action': 'Identifying entities and relationships',
            'status': 'complete',
            'timestamp': time.time() - start,
            'result': ontology
        }
    
    def _parse_llm_json_response(self, llm_output: str) -> Dict:
        """Safely parse JSON from LLM output, handling imperfections."""
        try:
            # Find the start of the JSON object
            json_start = llm_output.find('{')
            if json_start == -1:
                return {}
            # Find the end of the JSON object
            json_end = llm_output.rfind('}')
            if json_end == -1:
                return {}
            
            json_string = llm_output[json_start:json_end+1]
            return json.loads(json_string)
        except json.JSONDecodeError:
            # Fallback for malformed JSON
            return {}

    async def _call_ollama(self, prompt: str, model: str = None) -> Dict:
        """Call Ollama API for LLM inference"""
        if model is None:
            model = self.ollama_model
            
        response = requests.post(
            self.llm_endpoint,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        
        response.raise_for_status() # Will raise an exception for non-200 status codes
        
        result = response.json()
        llm_output = result.get('response', '{}')
        
        parsed_json = self._parse_llm_json_response(llm_output)
        if not parsed_json.get('entities') and not parsed_json.get('relationships'):
            # If parsing fails or gives empty result, try a fallback
            return self._fallback_extraction(prompt) # Use prompt as context for fallback

        return parsed_json

    def _fallback_extraction(self, text: str) -> Dict:
        """Simple rule-based entity extraction as fallback"""
        # Basic named entity recognition patterns
        entities = []
        relationships = []
        
        # Extract capitalized words as potential entities
        words = re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b', text)
        
        entity_types = ['Person', 'Organization', 'Location', 'Project', 'Department']
        for i, word in enumerate(set(words[:20])):  # Limit to 20 entities
            entities.append({
                'name': word,
                'type': entity_types[i % len(entity_types)],
                'attributes': {'source': 'rule_based'}
            })
        
        # Create some relationships
        for i in range(min(len(entities) - 1, 15)):
            relationships.append({
                'source': entities[i]['name'],
                'target': entities[i + 1]['name'],
                'type': 'related_to'
            })
        
        return {
            'entities': entities,
            'relationships': relationships
        }
    
    async def _stage_generate_embeddings(self, chunks: List[str], ontology: Dict) -> Dict:
        """Generate embeddings using sentence transformers"""
        start = time.time()
        
        try:
            from sentence_transformers import SentenceTransformer
            
            # Use sentence transformer model from settings
            model = SentenceTransformer(settings.EMBEDDING_MODEL)
            
            # Generate embeddings for chunks
            chunk_embeddings = model.encode(chunks).tolist()
            
            # Generate embeddings for entities
            entity_texts = [e['name'] for e in ontology.get('entities', [])]
            entity_embeddings = model.encode(entity_texts).tolist() if entity_texts else []
            
            embeddings = {
                'chunks': chunk_embeddings,
                'entities': entity_embeddings,
                'texts': chunks,
                'entity_names': entity_texts
            }
            
        except Exception as e:
            # Fallback to mock embeddings
            embeddings = {
                'chunks': [[0.1] * 384 for _ in chunks],
                'entities': [[0.1] * 384 for _ in ontology.get('entities', [])],
                'texts': chunks,
                'entity_names': [e['name'] for e in ontology.get('entities', [])]
            }
        
        return {
            'agent': 'Embedding Generator',
            'action': 'Creating vector embeddings',
            'status': 'complete',
            'timestamp': time.time() - start,
            'result': embeddings
        }
    
    async def _stage_entity_resolution(self, doc_id: str) -> Dict:
        """Deduplicate and resolve entities"""
        start = time.time()
        
        from services.entity_resolver import EntityResolver
        resolver = EntityResolver()
        
        stats = await resolver.resolve_entities(doc_id)
        
        return {
            'agent': 'Entity Resolver',
            'action': 'Deduplicating entities',
            'status': 'complete',
            'timestamp': time.time() - start,
            'result': stats
        }
    
    def _format_stage(self, stage: Dict) -> Dict:
        """Format stage for API response"""
        return {
            'agent': stage.get('agent', 'Unknown'),
            'action': stage.get('action', ''),
            'status': stage.get('status', 'complete'),
            'timestamp': stage.get('timestamp', 0)
        }
    
    async def list_documents(self) -> List[Dict]:
        """List all processed documents"""
        return _processed_docs
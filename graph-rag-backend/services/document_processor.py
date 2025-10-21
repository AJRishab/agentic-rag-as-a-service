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
        """Extract entities and relationships using Groq LLM"""
        start = time.time()
        
        # Combine chunks for ontology extraction
        sample_text = ' '.join(chunks[:3])  # Use first 3 chunks
        
        try:
            # Try Groq API (free, fast)
            from services.groq_service import GroqService
            groq = GroqService()
            ontology = groq.extract_entities(sample_text)
            print(f"✅ Groq extraction successful: {len(ontology.get('entities', []))} entities, {len(ontology.get('relationships', []))} relationships")
        except Exception as e:
            # Fallback to rule-based extraction
            print(f"⚠️ Groq call failed: {e}. Using rule-based extraction.")
            ontology = self._fallback_extraction(sample_text)
            print(f"✅ Rule-based extraction: {len(ontology.get('entities', []))} entities, {len(ontology.get('relationships', []))} relationships")
        
        return {
            'agent': 'LLM Ontology Extractor (Groq)',
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
            
        # Use correct Ollama API endpoint
        ollama_url = f"{self.llm_endpoint}/api/generate"
        
        response = requests.post(
            ollama_url,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=10  # Reduced timeout
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
        """Intelligent rule-based entity extraction with improved patterns"""
        entities = []
        relationships = []
        
        # Enhanced patterns for different entity types
        patterns = {
            'Person': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # John Smith
            'Organization': r'\b[A-Z][a-zA-Z\s]*(?:Inc|Corp|LLC|Ltd|Company|Department|Team)\b',
            'Location': r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*(?:\s(?:City|Office|Building|Center))\b',
            'Project': r'\b(?:Project|Initiative|Program)\s+[A-Z][a-zA-Z\s]+\b',
            'Department': r'\b[A-Z][a-zA-Z\s]*(?:Department|Division|Unit|Group)\b',
            'Position': r'\b(?:Manager|Director|CEO|CTO|VP|President|Lead|Senior|Junior)\b',
            'Date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b[A-Z][a-z]+\s+\d{1,2},?\s+\d{4}\b',
            'Document': r'\b[A-Z][a-zA-Z\s]*(?:Report|Document|Policy|Manual|Guide)\b'
        }
        
        # Extract entities by type
        seen_entities = set()
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text)
            for match in matches[:5]:  # Limit per type
                if match not in seen_entities and len(match.strip()) > 2:
                    seen_entities.add(match)
                    entities.append({
                        'name': match.strip(),
                        'type': entity_type,
                        'attributes': {
                            'source': 'rule_based',
                            'pattern': pattern,
                            'confidence': 0.8
                        }
                    })
        
        # Add general capitalized entities if we don't have enough
        if len(entities) < 8:
            general_words = re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b', text)
            for word in set(general_words):
                if word not in seen_entities and len(word) > 3:
                    seen_entities.add(word)
                    entities.append({
                        'name': word,
                        'type': 'Entity',
                        'attributes': {'source': 'rule_based', 'confidence': 0.6}
                    })
                    if len(entities) >= 12:
                        break
        
        # Create intelligent relationships
        relationship_patterns = [
            (r'(\w+)\s+works\s+(?:at|for)\s+(\w+)', 'EMPLOYED_BY'),
            (r'(\w+)\s+manages?\s+(\w+)', 'MANAGES'),
            (r'(\w+)\s+reports?\s+to\s+(\w+)', 'REPORTS_TO'),
            (r'(\w+)\s+(?:is|are)\s+(?:in|part of)\s+(\w+)', 'MEMBER_OF'),
            (r'(\w+)\s+and\s+(\w+)', 'RELATED_TO')
        ]
        
        # Look for pattern-based relationships
        for pattern, rel_type in relationship_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for source, target in matches[:5]:
                if source != target:
                    relationships.append({
                        'source': source,
                        'target': target,
                        'type': rel_type,
                        'attributes': {'source': 'rule_based', 'confidence': 0.7}
                    })
        
        # Add sequential relationships for remaining entities
        entity_names = [e['name'] for e in entities]
        for i in range(min(len(entity_names) - 1, 8)):
            relationships.append({
                'source': entity_names[i],
                'target': entity_names[i + 1],
                'type': 'RELATED_TO',
                'attributes': {'source': 'rule_based', 'confidence': 0.5}
            })
        
        return {
            'entities': entities[:15],  # Limit total entities
            'relationships': relationships[:12]  # Limit total relationships
        }
    
    async def _stage_generate_embeddings(self, chunks: List[str], ontology: Dict) -> Dict:
        """Generate embeddings using sentence transformers"""
        start = time.time()
        
        try:
            from sentence_transformers import SentenceTransformer
            
            # Use standard sentence-transformers model (not Ollama format)
            # Fallback to all-MiniLM-L6-v2 if Ollama model name is used
            embedding_model_name = settings.EMBEDDING_MODEL
            if ":latest" in embedding_model_name or "mahonzhan/" in embedding_model_name:
                embedding_model_name = "all-MiniLM-L6-v2"
            
            model = SentenceTransformer(embedding_model_name)
            
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
    
    async def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Delete a document and return metadata about what was deleted"""
        global _processed_docs
        
        # Find and remove the document
        doc_to_delete = None
        for i, doc in enumerate(_processed_docs):
            if doc['id'] == document_id:
                doc_to_delete = _processed_docs.pop(i)
                break
        
        if not doc_to_delete:
            return None
        
        # Delete from graph database
        from services.graph_service import GraphService
        graph_service = GraphService()
        
        # Get entities/relationships count for this document before deletion
        stats_before = await graph_service.get_stats()
        
        # Delete document-specific graph data
        await graph_service.delete_document_data(document_id)
        
        # Get stats after deletion
        stats_after = await graph_service.get_stats()
        
        # Save updated document list
        _save_processed_docs()
        
        return {
            'document_id': document_id,
            'filename': doc_to_delete.get('filename'),
            'entities_count': stats_before.get('entities', 0) - stats_after.get('entities', 0),
            'relationships_count': stats_before.get('relationships', 0) - stats_after.get('relationships', 0),
            'deleted_at': datetime.now().isoformat()
        }

"""
Groq API Service
Handles LLM operations using Groq's fast inference API
"""

import os
import json
import time
from typing import Dict, Any, Optional
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings


class GroqService:
    """Service for interacting with Groq API"""
    
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not set in environment variables")
        
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
        except ImportError:
            print("⚠️  Groq SDK not installed. Install with: pip install groq")
            self.client = None
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities and relationships using Groq LLM"""
        if not self.client:
            return {"entities": [], "relationships": []}
        
        # Limit text for API
        text_limited = text[:1000]
        
        prompt = f"""Extract entities and relationships from this text. Return valid JSON only.

Text: {text_limited}

Return JSON with this exact structure:
{{"entities": [{{"name": "EntityName", "type": "EntityType"}}], "relationships": [{{"source": "Entity1", "target": "Entity2", "type": "relation"}}]}}

Extract max 10 entities and 8 relationships. Be concise."""
        
        try:
            message = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.1,  # Low temp for consistent JSON
                max_tokens=500,
            )
            
            response_text = message.choices[0].message.content
            return self._parse_json_response(response_text)
            
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            return {"entities": [], "relationships": []}
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Safely parse JSON from LLM response"""
        try:
            # Find JSON in response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                return {"entities": [], "relationships": []}
            
            json_str = response[json_start:json_end]
            parsed = json.loads(json_str)
            
            # Validate structure
            if "entities" not in parsed:
                parsed["entities"] = []
            if "relationships" not in parsed:
                parsed["relationships"] = []
            
            return parsed
            
        except json.JSONDecodeError:
            return {"entities": [], "relationships": []}
    
    def generate_answer(self, prompt: str, context: str = "") -> str:
        """Generate conversational answer based on prompt"""
        if not self.client:
            return "Unable to generate answer."
        
        # Prompt is already formatted, just use it directly
        full_prompt = prompt if context == "" else f"{prompt}\n\nAdditional context:\n{context[:1000]}"
        
        try:
            message = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=500,
            )
            
            return message.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Groq generation error: {e}")
            return "Unable to generate answer at this time."


# Fallback rule-based extraction for when Groq is unavailable
def fallback_extraction(text: str) -> Dict[str, Any]:
    """Rule-based extraction when API is unavailable"""
    import re
    
    entities = []
    relationships = []
    
    patterns = {
        'Person': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
        'Organization': r'\b[A-Z][a-zA-Z\s]*(?:Inc|Corp|LLC|Ltd|Company|Department|Team)\b',
        'Location': r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*(?:\s(?:City|Office|Building|Center))\b',
        'Project': r'\b(?:Project|Initiative|Program)\s+[A-Z][a-zA-Z\s]+\b',
    }
    
    seen_entities = set()
    for entity_type, pattern in patterns.items():
        matches = re.findall(pattern, text)
        for match in matches[:5]:
            if match not in seen_entities and len(match.strip()) > 2:
                seen_entities.add(match)
                entities.append({
                    'name': match.strip(),
                    'type': entity_type,
                    'attributes': {'source': 'rule_based', 'confidence': 0.8}
                })
    
    return {"entities": entities, "relationships": relationships}

#!/usr/bin/env python3
"""Test query functionality"""

import requests
import json

API_BASE = "http://localhost:8000"

def test_query():
    """Test the complete query workflow"""
    
    # Test query
    query = "What company is this document about?"
    
    print(f"🤔 Asking: '{query}'")
    
    response = requests.post(f"{API_BASE}/api/query", json={
        "query": query,
        "max_results": 10,
        "use_vector": True,
        "use_graph": True,
        "use_filter": True
    })
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Query successful!")
        print(f"📝 Answer: {result.get('answer', 'No answer provided')}")
        print(f"🎯 Confidence: {result.get('confidence', 0) * 100:.0f}%")
        
        sources = result.get('sources', [])
        print(f"📚 Sources ({len(sources)}):")
        for i, source in enumerate(sources, 1):
            print(f"  {i}. [{source['type']}] {source['content'][:100]}...")
            
        reasoning = result.get('reasoning_chain', [])
        print(f"🧠 Reasoning Chain ({len(reasoning)} steps):")
        for i, step in enumerate(reasoning, 1):
            print(f"  {i}. {step['agent']}: {step['action']}")
            
    else:
        print(f"❌ Query failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_query()
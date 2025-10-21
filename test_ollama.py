#!/usr/bin/env python3
"""Test Ollama API endpoint"""

import requests
import json

def test_ollama():
    """Test Ollama API directly"""
    
    # Test the correct endpoint
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": "tinyllama",
        "prompt": "Hello, world!",
        "stream": False
    }
    
    print("🔌 Testing Ollama API...")
    print(f"📡 URL: {url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📝 Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    test_ollama()
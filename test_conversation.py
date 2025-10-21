#!/usr/bin/env python3
"""Test conversational queries"""

import requests
import json

API_BASE = "http://localhost:8000"

def ask_question(question):
    """Ask a conversational question"""
    print(f"\n🤔 User: {question}")
    
    response = requests.post(f"{API_BASE}/api/query", json={
        "query": question,
        "max_results": 5,
        "use_vector": True,
        "use_graph": True,
        "use_filter": True
    })
    
    if response.status_code == 200:
        result = response.json()
        answer = result.get('answer', 'No answer provided')
        confidence = result.get('confidence', 0) * 100
        
        print(f"🤖 AI: {answer}")
        print(f"   Confidence: {confidence:.0f}%")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False

def test_conversation():
    """Test a natural conversation about the document"""
    
    questions = [
        "What company is this document about?",
        "What kind of financial information does it contain?", 
        "What time period does this cover?",
        "How much revenue did they make?",
        "What are their main expenses?",
        "Is this a quarterly or annual report?"
    ]
    
    print("🎯 Starting conversational test with your Graph RAG system...")
    
    for question in questions:
        success = ask_question(question)
        if not success:
            print("Stopping due to error")
            break
    
    print("\n✅ Conversation test completed!")

if __name__ == "__main__":
    test_conversation()
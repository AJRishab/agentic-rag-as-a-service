#!/usr/bin/env python3
"""Test document delete functionality"""

import requests
import json

API_BASE = "http://localhost:8000"

def test_delete_workflow():
    """Test the complete delete workflow"""
    
    # 1. List current documents
    print("📋 Listing current documents...")
    response = requests.get(f"{API_BASE}/api/documents")
    if response.status_code == 200:
        docs = response.json()
        print(f"Found {len(docs)} documents:")
        for doc in docs:
            print(f"  - {doc['id']}: {doc['filename']} ({doc.get('chunks', 0)} chunks)")
    else:
        print("❌ Failed to list documents")
        return
    
    if not docs:
        print("⚠️ No documents to delete. Upload a document first.")
        return
    
    # 2. Get current graph stats
    print("\n📊 Current graph stats:")
    response = requests.get(f"{API_BASE}/api/graph/stats")
    if response.status_code == 200:
        stats_before = response.json()
        print(f"  Entities: {stats_before['entities']}")
        print(f"  Relationships: {stats_before['relationships']}")
        print(f"  Attributes: {stats_before['attributes']}")
    
    # 3. Delete the first document
    doc_to_delete = docs[0]
    doc_id = doc_to_delete['id']
    
    print(f"\n🗑️ Deleting document: {doc_id} ({doc_to_delete['filename']})")
    
    response = requests.delete(f"{API_BASE}/api/documents/{doc_id}")
    
    if response.status_code == 200:
        delete_result = response.json()
        print("✅ Delete successful!")
        print(f"  Deleted entities: {delete_result['deleted_entities']}")
        print(f"  Deleted relationships: {delete_result['deleted_relationships']}")
        print(f"  Message: {delete_result['message']}")
    else:
        print(f"❌ Delete failed: {response.status_code}")
        print(response.text)
        return
    
    # 4. Check updated stats
    print("\n📊 Updated graph stats:")
    response = requests.get(f"{API_BASE}/api/graph/stats")
    if response.status_code == 200:
        stats_after = response.json()
        print(f"  Entities: {stats_after['entities']}")
        print(f"  Relationships: {stats_after['relationships']}")
        print(f"  Attributes: {stats_after['attributes']}")
    
    # 5. List documents again
    print("\n📋 Remaining documents:")
    response = requests.get(f"{API_BASE}/api/documents")
    if response.status_code == 200:
        remaining_docs = response.json()
        print(f"Found {len(remaining_docs)} documents:")
        for doc in remaining_docs:
            print(f"  - {doc['id']}: {doc['filename']}")
    
    print("\n✅ Delete test completed!")

if __name__ == "__main__":
    test_delete_workflow()
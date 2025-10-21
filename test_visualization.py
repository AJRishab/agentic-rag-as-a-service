#!/usr/bin/env python3
"""Test graph visualization data"""

import requests
import json

API_BASE = "http://localhost:8000"

def test_visualization():
    """Test the graph visualization endpoint"""
    
    print("📊 Testing Graph Visualization Data...")
    
    # Get visualization data
    response = requests.get(f"{API_BASE}/api/graph/visualize")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Visualization data retrieved successfully!")
        
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        stats = data.get('stats', {})
        
        print(f"\n📈 Graph Statistics:")
        print(f"  Entities: {stats.get('entities', 0)}")
        print(f"  Relationships: {stats.get('relationships', 0)}")
        print(f"  Attributes: {stats.get('attributes', 0)}")
        
        print(f"\n🔍 Visualization Data:")
        print(f"  Nodes: {len(nodes)}")
        print(f"  Edges: {len(edges)}")
        
        if nodes:
            print(f"\n📝 Sample Nodes:")
            for i, node in enumerate(nodes[:5]):
                print(f"  {i+1}. {node.get('label', 'N/A')} ({node.get('type', 'Unknown')})")
            if len(nodes) > 5:
                print(f"  ... and {len(nodes) - 5} more nodes")
        
        if edges:
            print(f"\n🔗 Sample Relationships:")
            for i, edge in enumerate(edges[:3]):
                print(f"  {i+1}. {edge.get('from', '?')} → {edge.get('label', 'connected')} → {edge.get('to', '?')}")
            if len(edges) > 3:
                print(f"  ... and {len(edges) - 3} more relationships")
                
        # Check entity types
        entity_types = stats.get('entity_types', {})
        if entity_types:
            print(f"\n🏷️ Entity Types:")
            for entity_type, count in entity_types.items():
                print(f"  {entity_type}: {count}")
        
    else:
        print(f"❌ Failed to get visualization data: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_visualization()
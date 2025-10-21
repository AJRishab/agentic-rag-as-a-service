#!/usr/bin/env python3
"""Test Neo4j connection"""

from neo4j import GraphDatabase
import sys

def test_connection():
    uri = "neo4j://127.0.0.1:7687"
    user = "neo4j"
    password = "Chandra@nigger69"
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        with driver.session() as session:
            result = session.run("RETURN 'Connection successful' as message")
            record = result.single()
            print(f"✅ {record['message']}")
            
            # Test a simple query
            result = session.run("MATCH (n) RETURN count(n) as node_count")
            count = result.single()["node_count"]
            print(f"📊 Current node count: {count}")
            
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
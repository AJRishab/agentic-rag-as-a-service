"""
Graph RAG Platform Demo Script
Demonstrates all features of the platform
"""

import requests
import json
import time
from pathlib import Path


class GraphRAGDemo:
    """Demo client for Graph RAG API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def print_section(self, title: str):
        """Print section header"""
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60 + "\n")
    
    def print_json(self, data: dict):
        """Pretty print JSON data"""
        print(json.dumps(data, indent=2))
    
    def check_health(self):
        """Check API health"""
        self.print_section("Health Check")
        
        response = self.session.get(f"{self.base_url}/health")
        print(f"Status: {response.status_code}")
        self.print_json(response.json())
        
        return response.status_code == 200
    
    def upload_sample_document(self):
        """Upload a sample document"""
        self.print_section("Document Upload")
        
        # Create sample document
        sample_text = """
        TechCorp Company Overview
        
        TechCorp is a leading technology company based in Delhi, India.
        
        Leadership Team:
        - Sarah Johnson is the CEO and founder of TechCorp
        - Michael Chen serves as the CTO
        - Priya Sharma leads the Marketing Department
        
        Departments:
        - Engineering Department (50 employees)
        - Marketing Department (15 employees)
        - Sales Department (20 employees)
        
        Current Projects:
        - Project Alpha: AI-powered customer service platform
        - Project Beta: Cloud migration initiative
        - Project Gamma: Mobile app development
        
        Locations:
        - Headquarters: Delhi
        - Branch Office: Bangalore
        - Remote team: Mumbai
        
        The Engineering Department is working on Project Alpha and Project Beta.
        Sarah Johnson manages the entire organization.
        Priya Sharma's team handles all marketing initiatives.
        """
        
        # Save to temporary file
        temp_file = Path("temp_demo_doc.txt")
        temp_file.write_text(sample_text)
        
        try:
            # Upload document
            with open(temp_file, 'rb') as f:
                files = {'file': ('company_overview.txt', f, 'text/plain')}
                response = self.session.post(
                    f"{self.base_url}/api/documents/upload",
                    files=files
                )
            
            print(f"Upload Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\nDocument ID: {data['document_id']}")
                print(f"Filename: {data['filename']}")
                print(f"\nProcessing Stages:")
                for stage in data['stages']:
                    print(f"  ✓ {stage['agent']}: {stage['action']}")
                
                print(f"\nGraph Statistics:")
                stats = data['graph_stats']
                print(f"  Entities: {stats['entities']}")
                print(f"  Relationships: {stats['relationships']}")
                print(f"  Attributes: {stats['attributes']}")
                
                return data['document_id']
            else:
                print(f"Error: {response.text}")
                return None
        
        finally:
            # Cleanup
            if temp_file.exists():
                temp_file.unlink()
    
    def list_documents(self):
        """List all processed documents"""
        self.print_section("Document List")
        
        response = self.session.get(f"{self.base_url}/api/documents")
        
        if response.status_code == 200:
            documents = response.json()
            print(f"Total documents: {len(documents)}")
            
            for doc in documents:
                print(f"\n  • {doc['filename']}")
                print(f"    ID: {doc['id']}")
                print(f"    Processed: {doc['processed_at']}")
        else:
            print(f"Error: {response.text}")
    
    def get_graph_stats(self):
        """Get graph statistics"""
        self.print_section("Graph Statistics")
        
        response = self.session.get(f"{self.base_url}/api/graph/stats")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"Total Entities: {stats['entities']}")
            print(f"Total Relationships: {stats['relationships']}")
            print(f"Total Attributes: {stats['attributes']}")
            
            if 'entity_types' in stats:
                print("\nEntity Types:")
                for entity_type, count in stats['entity_types'].items():
                    print(f"  • {entity_type}: {count} nodes")
        else:
            print(f"Error: {response.text}")
    
    def get_ontology(self):
        """Get knowledge graph ontology"""
        self.print_section("Knowledge Graph Ontology")
        
        response = self.session.get(f"{self.base_url}/api/graph/ontology")
        
        if response.status_code == 200:
            ontology = response.json()
            
            print(f"Ontology Version: {ontology.get('version', 'N/A')}")
            print(f"\nEntity Types: {len(ontology.get('entity_types', []))}")
            for entity_type in ontology.get('entity_types', [])[:5]:
                print(f"  • {entity_type['name']} ({entity_type['count']} instances)")
            
            print(f"\nRelationship Types: {len(ontology.get('relationship_types', []))}")
            for rel_type in ontology.get('relationship_types', [])[:5]:
                print(f"  • {rel_type['name']} ({rel_type['count']} instances)")
        else:
            print(f"Error: {response.text}")
    
    def execute_query(self, query: str, show_reasoning: bool = True):
        """Execute a query"""
        self.print_section(f"Query: {query}")
        
        payload = {
            "query": query,
            "max_results": 10,
            "use_vector": True,
            "use_graph": True,
            "use_filter": True
        }
        
        print("Executing query...")
        start_time = time.time()
        
        response = self.session.post(
            f"{self.base_url}/api/query",
            json=payload
        )
        
        elapsed = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            
            if show_reasoning:
                print("\nReasoning Chain:")
                for step in result['reasoning_chain']:
                    print(f"  → {step['agent']}")
                    print(f"    {step['action']}")
            
            print(f"\n{'─' * 60}")
            print(f"ANSWER:")
            print(f"{'─' * 60}")
            print(f"\n{result['answer']}\n")
            print(f"{'─' * 60}")
            
            print(f"\nEvidence Sources ({len(result['sources'])}):")
            for i, source in enumerate(result['sources'][:5], 1):
                print(f"\n  {i}. Type: {source['type'].upper()}")
                print(f"     Content: {source['content'][:100]}...")
                print(f"     Confidence: {source['confidence']:.2f}")
            
            print(f"\nOverall Confidence: {result['confidence']:.1%}")
            print(f"Query Time: {result['query_time_ms']:.0f}ms")
            print(f"Total Time: {elapsed:.0f}ms")
            
            return result
        else:
            print(f"Error: {response.text}")
            return None
    
    def run_demo_queries(self):
        """Run a series of demo queries"""
        
        queries = [
            "Who is the CEO of TechCorp?",
            "What departments exist in the company?",
            "Which projects is the Engineering Department working on?",
            "Where are the company offices located?",
            "Who manages the Marketing Department?",
            "Tell me about Project Alpha"
        ]
        
        for query in queries:
            self.execute_query(query, show_reasoning=False)
            time.sleep(1)  # Brief pause between queries
    
    def get_metrics(self):
        """Get system metrics"""
        self.print_section("System Metrics")
        
        response = self.session.get(f"{self.base_url}/api/admin/metrics")
        
        if response.status_code == 200:
            metrics = response.json()
            
            print("Query Metrics:")
            query_metrics = metrics['queries']
            print(f"  Total Queries: {query_metrics['total']}")
            print(f"  Successful: {query_metrics['successful']}")
            print(f"  Failed: {query_metrics['failed']}")
            print(f"  Avg Latency: {query_metrics['avg_latency_ms']:.1f}ms")
            
            print("\nDocument Metrics:")
            doc_metrics = metrics['documents']
            print(f"  Total Processed: {doc_metrics['total_processed']}")
            print(f"  Total Entities: {doc_metrics['total_entities']}")
            print(f"  Total Relationships: {doc_metrics['total_relationships']}")
            
            print("\nGraph Metrics:")
            graph_metrics = metrics['graph']
            print(f"  Total Nodes: {graph_metrics['total_nodes']}")
            print(f"  Total Edges: {graph_metrics['total_edges']}")
            print(f"  Storage: {graph_metrics['storage_mb']:.2f} MB")
            
            print("\nSystem Metrics:")
            system_metrics = metrics['system']
            uptime = system_metrics['uptime_seconds']
            hours = uptime // 3600
            minutes = (uptime % 3600) // 60
            print(f"  Uptime: {hours}h {minutes}m")
        else:
            print(f"Error: {response.text}")
    
    def run_full_demo(self):
        """Run complete demonstration"""
        
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + " " * 15 + "Graph RAG Platform Demo" + " " * 20 + "║")
        print("╚" + "═" * 58 + "╝")
        
        # 1. Health check
        if not self.check_health():
            print("\n❌ API is not available. Please start the server first.")
            return
        
        # 2. Upload document
        doc_id = self.upload_sample_document()
        if not doc_id:
            print("\n❌ Document upload failed.")
            return
        
        time.sleep(1)
        
        # 3. List documents
        self.list_documents()
        
        time.sleep(1)
        
        # 4. Get graph stats
        self.get_graph_stats()
        
        time.sleep(1)
        
        # 5. Get ontology
        self.get_ontology()
        
        time.sleep(1)
        
        # 6. Run demo queries
        self.run_demo_queries()
        
        time.sleep(1)
        
        # 7. Get metrics
        self.get_metrics()
        
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + " " * 19 + "Demo Complete!" + " " * 22 + "║")
        print("╚" + "═" * 58 + "╝\n")


def main():
    """Main entry point"""
    demo = GraphRAGDemo()
    
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "health":
            demo.check_health()
        elif command == "upload":
            demo.upload_sample_document()
        elif command == "stats":
            demo.get_graph_stats()
        elif command == "ontology":
            demo.get_ontology()
        elif command == "metrics":
            demo.get_metrics()
        elif command == "query":
            if len(sys.argv) > 2:
                query = " ".join(sys.argv[2:])
                demo.execute_query(query)
            else:
                print("Usage: python demo.py query <your question>")
        else:
            print(f"Unknown command: {command}")
            print("\nAvailable commands:")
            print("  health    - Check API health")
            print("  upload    - Upload sample document")
            print("  stats     - Show graph statistics")
            print("  ontology  - Show ontology")
            print("  metrics   - Show system metrics")
            print("  query     - Execute a query")
            print("  (no args) - Run full demo")
    else:
        # Run full demo
        demo.run_full_demo()


if __name__ == "__main__":
    main()
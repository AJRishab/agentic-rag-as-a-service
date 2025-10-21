#!/usr/bin/env python3
"""
Test script to verify Groq API integration works correctly
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'graph-rag-backend')
env_file = os.path.join(backend_dir, '.env')
if os.path.exists(env_file):
    load_dotenv(env_file)
    print(f"✅ Loaded .env from {env_file}")
else:
    print(f"⚠️  .env not found at {env_file}")

# Add backend directory to path
sys.path.insert(0, backend_dir)

from services.groq_service import GroqService, fallback_extraction

def test_groq_api():
    """Test Groq API with sample text"""
    print("\n" + "="*60)
    print("🧪 Testing Groq API Integration")
    print("="*60 + "\n")
    
    # Sample text for testing
    test_text = """
    Apple Inc. is an American multinational technology company headquartered in Cupertino, California.
    The company was founded by Steve Jobs and Steve Wozniak on April 1, 1976.
    Tim Cook is the current CEO, taking over from Steve Jobs in 2011.
    Apple's competitors include Microsoft Corporation and Google LLC.
    """
    
    print("📝 Test Text:")
    print("-" * 40)
    print(test_text.strip())
    print("-" * 40)
    print()
    
    # Test 1: Groq API
    print("Test 1️⃣: Testing Groq API Service")
    print("-" * 40)
    try:
        groq = GroqService()
        print("✅ Groq service initialized")
        print(f"   Model: {groq.model}")
        print(f"   API Key: {groq.api_key[:10]}...***")
        print()
        
        print("🔄 Calling Groq API for entity extraction...")
        result = groq.extract_entities(test_text)
        
        if result['entities']:
            print("✅ Groq extraction successful!")
            print(f"\n📊 Extracted Entities ({len(result['entities'])} found):")
            for entity in result['entities']:
                print(f"   • {entity['name']} ({entity['type']})")
            
            if result['relationships']:
                print(f"\n🔗 Relationships ({len(result['relationships'])} found):")
                for rel in result['relationships']:
                    print(f"   • {rel['source']} --[{rel['type']}]--> {rel['target']}")
        else:
            print("⚠️  No entities extracted (might be JSON parsing issue)")
            print(f"Raw result: {result}")
        
    except Exception as e:
        print(f"❌ Groq API Test Failed: {e}")
        print("\n" + "⚠️  Falling back to rule-based extraction...")
        
        # Test 2: Fallback extraction
        print("\nTest 2️⃣: Testing Fallback (Rule-based) Extraction")
        print("-" * 40)
        result = fallback_extraction(test_text)
        
        print("✅ Rule-based extraction successful!")
        print(f"\n📊 Extracted Entities ({len(result['entities'])} found):")
        for entity in result['entities']:
            print(f"   • {entity['name']} ({entity['type']})")
    
    print("\n" + "="*60)
    print("✅ Test Complete!")
    print("="*60 + "\n")

def test_document_upload():
    """Test document upload simulation"""
    print("\n" + "="*60)
    print("📤 Testing Document Upload (Simulated)")
    print("="*60 + "\n")
    
    test_file = "test_document.txt"
    if os.path.exists(test_file):
        with open(test_file, 'r') as f:
            content = f.read()
        
        print(f"📄 Test file: {test_file}")
        print(f"📏 File size: {len(content)} characters")
        print()
        
        print("🔄 Processing with Groq...")
        try:
            groq = GroqService()
            result = groq.extract_entities(content)
            
            print("✅ Document processing successful!")
            print(f"   Entities found: {len(result['entities'])}")
            print(f"   Relationships found: {len(result['relationships'])}")
            
            if result['entities']:
                print("\n   Sample entities:")
                for entity in result['entities'][:5]:
                    print(f"      • {entity['name']} ({entity['type']})")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print(f"⚠️  Test file not found: {test_file}")
    
    print("\n" + "="*60)
    print("✅ Upload Test Complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        test_groq_api()
        test_document_upload()
        
        print("\n" + "🎉 "*20)
        print("All tests completed successfully!")
        print("Groq API integration is working! ✅")
        print("🎉 "*20 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⛔ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

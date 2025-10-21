#!/usr/bin/env python3
"""Test document upload to backend API"""

import requests
import json

def upload_document(file_path, api_url="http://localhost:8000/api/documents/upload"):
    """Upload document to the API endpoint"""
    try:
        with open(file_path, 'rb') as file:
            files = {'file': (file_path, file, 'text/plain')}
            response = requests.post(api_url, files=files)
            
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("Success! Document uploaded and processed.")
            result = response.json()
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    upload_document("test_doc.txt")
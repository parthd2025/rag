#!/usr/bin/env python3

import sys
import os
sys.path.append('backend')

from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.main import app

# Create test client
client = TestClient(app)

def test_delete_endpoint():
    print("Testing delete endpoint...")
    
    # First, check what documents exist
    response = client.get("/documents")
    result = response.json()
    print(f"Current response: {result}")
    
    # Extract documents list from response
    documents = result.get("documents", [])
    
    # Try to delete first available document if any exist
    if documents and len(documents) > 0:
        doc_name = documents[0].get("name") or documents[0].get("id")
        print(f"\nAttempting to delete document: {doc_name}")
        response = client.delete(f"/documents/{doc_name}")
        print(f"Delete response status: {response.status_code}")
        print(f"Delete response: {response.text}")
    else:
        print("\n⚠️  No documents available to delete")
        print("Tip: Upload a document first via the API or Streamlit UI")
    
    if response.status_code == 200:
        print("✅ Delete endpoint working!")
    else:
        print("❌ Delete endpoint failed")

if __name__ == "__main__":
    test_delete_endpoint()
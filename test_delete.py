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
    print(f"Current documents: {response.json()}")
    
    # Try to delete a document
    response = client.delete("/documents/baseline-overview")
    print(f"Delete response status: {response.status_code}")
    print(f"Delete response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Delete endpoint working!")
    else:
        print("❌ Delete endpoint failed")

if __name__ == "__main__":
    test_delete_endpoint()
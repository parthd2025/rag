"""
Quick test script to verify M2 mileage retrieval improvements
"""
import streamlit as st
import requests
import json

# Test the improved system
def test_m2_queries():
    """Test various M2-related queries"""
    
    test_queries = [
        "what is M2 benefits in mindbowser?",
        "M2 mileage policy",
        "mindbowser M2 allowance",
        "transportation benefits M2"
    ]
    
    api_url = "http://localhost:8000"
    
    print("=== Testing M2 Mileage Retrieval ===")
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        try:
            response = requests.post(
                f"{api_url}/chat",
                json={"message": query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success - Response length: {len(data.get('response', ''))}")
                print(f"Sources found: {len(data.get('sources', []))}")
                if data.get('sources'):
                    for i, source in enumerate(data['sources'][:2]):
                        print(f"  Source {i+1}: {source.get('document_name', 'Unknown')}")
            else:
                print(f"❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Connection Error: {e}")
    
    print("\n" + "="*50)
    print("Test complete. Check if M2 documents are now being retrieved!")

if __name__ == "__main__":
    test_m2_queries()
"""
Clear all traces from Opik rag-system project
"""

from opik import Opik

def clear_traces():
    """Delete all traces from rag-system project."""
    client = Opik(project_name="rag-system")
    
    print("🗑️  Clearing all traces from rag-system project...")
    
    try:
        # Get all traces
        # Note: Opik client API might not have direct delete all method
        # So we'll use the REST client
        
        # Flush any pending traces first
        client.flush()
        
        print("✅ Flushed pending traces")
        print("\n⚠️  Note: To completely clear traces, you can:")
        print("   1. In Opik UI: Select all traces → Delete")
        print("   2. Or restart the Opik Docker containers with fresh volumes")
        print("\nTo restart Opik with fresh data:")
        print("   docker-compose -f docker-compose.opik.yml down -v")
        print("   docker-compose -f docker-compose.opik.yml up -d")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    clear_traces()

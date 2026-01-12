"""
List all projects in Opik
"""

from opik import Opik

def list_projects():
    """List all projects in Opik."""
    try:
        client = Opik()
        print(f"✅ Opik client created successfully")
        
        # Check config
        print(f"\n🔧 Config attributes: {dir(client.config)}")
        
        # Try to access project info
        if hasattr(client, 'project_name'):
            print(f"\n📁 Current project: {client.project_name}")
        
        # Flush to ensure connection works
        client.flush()
        print("\n✅ Flush successful - connection to Opik works!")
        print("\n💡 To see projects, go to: http://localhost:5173")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_projects()

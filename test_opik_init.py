"""
OPIK Diagnostic Script
======================

This script tests OPIK initialization and helps diagnose issues.

Usage:
    python test_opik_init.py

What it checks:
1. OPIK package installation
2. Environment configuration
3. Connection to OPIK server
4. Project creation
5. Trace logging
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_environment():
    """Check environment variables."""
    print("\n" + "="*60)
    print("1. ENVIRONMENT CONFIGURATION")
    print("="*60)
    
    env_vars = [
        "OPIK_URL_OVERRIDE",
        "OPIK_WORKSPACE", 
        "OPIK_PROJECT_NAME",
        "OPIK_ENABLED",
        "OPIK_API_KEY"
    ]
    
    for var in env_vars:
        value = os.getenv(var, "(not set)")
        print(f"  {var}: {value}")
    
    # Load from .env if exists
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        print(f"\n  ✅ Found .env file: {env_file}")
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print("  ✅ Loaded .env file")
        
        print("\n  After loading .env:")
        for var in env_vars:
            value = os.getenv(var, "(not set)")
            print(f"    {var}: {value}")
    else:
        print(f"\n  ⚠️ No .env file found at {env_file}")


def check_opik_package():
    """Check OPIK package installation."""
    print("\n" + "="*60)
    print("2. OPIK PACKAGE CHECK")
    print("="*60)
    
    try:
        import opik
        print(f"  ✅ OPIK package installed")
        print(f"  Version: {getattr(opik, '__version__', 'unknown')}")
        
        # Check available exports
        available = [attr for attr in dir(opik) if not attr.startswith('_')]
        print(f"  Available exports: {', '.join(available[:10])}...")
        
        return True
    except ImportError as e:
        print(f"  ❌ OPIK package NOT installed: {e}")
        print("  Install with: pip install opik")
        return False


def check_opik_connection():
    """Check connection to OPIK server."""
    print("\n" + "="*60)
    print("3. OPIK CONNECTION CHECK")
    print("="*60)
    
    url = os.getenv("OPIK_URL_OVERRIDE", "http://localhost:5173/api")
    
    # Remove /api suffix for health check
    base_url = url.replace("/api", "")
    health_url = f"{base_url}/api/ready"
    
    print(f"  Checking: {health_url}")
    
    try:
        import httpx
        response = httpx.get(health_url, timeout=5.0)
        if response.status_code == 200:
            print(f"  ✅ OPIK server is running")
            print(f"  Response: {response.text[:100]}")
            return True
        else:
            print(f"  ⚠️ OPIK server responded with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Cannot connect to OPIK: {e}")
        print("\n  Troubleshooting:")
        print("  1. Check if OPIK Docker containers are running:")
        print("     docker ps --filter 'name=opik'")
        print("  2. Start OPIK if not running:")
        print("     cd opik && .\\opik.ps1")
        print(f"  3. Open OPIK UI: {base_url}")
        return False


def test_opik_initialization():
    """Test OPIK initialization using our module."""
    print("\n" + "="*60)
    print("4. OPIK INITIALIZATION TEST")
    print("="*60)
    
    try:
        from backend.opik_config import (
            initialize_opik,
            get_opik_manager,
            OpikConfig
        )
        
        # Show config
        config = OpikConfig()
        print(f"  Config: {config}")
        
        # Initialize
        print("\n  Initializing OPIK...")
        success, message = initialize_opik()
        
        if success:
            print(f"  ✅ {message}")
        else:
            print(f"  ❌ {message}")
        
        # Get status
        manager = get_opik_manager()
        status = manager.get_status()
        
        print("\n  OPIK Status:")
        for key, value in status.items():
            print(f"    {key}: {value}")
        
        return success
        
    except Exception as e:
        print(f"  ❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_trace_creation():
    """Test creating a trace."""
    print("\n" + "="*60)
    print("5. TRACE CREATION TEST")
    print("="*60)
    
    try:
        from backend.opik_config import get_opik_manager
        
        manager = get_opik_manager()
        
        if not manager.available:
            print("  ⚠️ OPIK not available, skipping trace test")
            return False
        
        print("  Creating test trace...")
        
        trace = manager.create_trace(
            name="diagnostic_test_trace",
            input={"test": "diagnostic", "query": "Is OPIK working?"},
            tags=["diagnostic", "test"],
            metadata={"script": "test_opik_init.py"}
        )
        
        if trace:
            print(f"  ✅ Trace created: {getattr(trace, 'id', 'unknown')}")
            
            # Add a span
            span = trace.span(
                name="test_span",
                input={"step": "testing"}
            )
            span.end(output={"result": "success"})
            
            # End trace
            trace.end(output={"status": "diagnostic complete"})
            
            # Flush
            print("  Flushing traces...")
            manager.flush()
            print("  ✅ Traces flushed")
            
            ui_url = manager.config.url_override.replace("/api", "")
            print(f"\n  📊 View traces at: {ui_url}")
            print(f"  📁 Project: {manager.config.project_name}")
            
            return True
        else:
            print("  ❌ Failed to create trace")
            return False
            
    except Exception as e:
        print(f"  ❌ Error creating trace: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all diagnostic checks."""
    print("\n" + "="*60)
    print("OPIK DIAGNOSTIC TOOL")
    print("="*60)
    print("This tool checks your OPIK integration and helps diagnose issues.")
    
    # Run checks
    check_environment()
    
    if not check_opik_package():
        print("\n❌ OPIK package not installed. Install it first.")
        return
    
    connection_ok = check_opik_connection()
    
    if not connection_ok:
        print("\n⚠️ OPIK server not reachable. Start it first.")
        print("Continuing with initialization test anyway...")
    
    init_ok = test_opik_initialization()
    
    if init_ok:
        test_trace_creation()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if init_ok:
        print("✅ OPIK is properly configured and working!")
        print("\nNext steps:")
        print("1. Run your RAG application")
        print("2. Make some queries")
        print("3. Check OPIK UI for traces")
        
        from backend.opik_config import get_opik_manager
        manager = get_opik_manager()
        ui_url = manager.config.url_override.replace("/api", "")
        print(f"\nOPIK UI: {ui_url}")
    else:
        print("❌ OPIK initialization failed. Check the errors above.")
        print("\nCommon solutions:")
        print("1. Ensure OPIK Docker containers are running")
        print("2. Check environment variables in .env")
        print("3. Verify network connectivity")


if __name__ == "__main__":
    main()

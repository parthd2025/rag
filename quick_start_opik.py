"""
Quick Start: Enhanced Opik Integration
======================================

This script helps you quickly restart the server with enhanced Opik tracking.
"""

import subprocess
import sys
import os
import time

def check_opik_installed():
    """Check if Opik is installed."""
    try:
        import opik
        print("✅ Opik is installed")
        return True
    except ImportError:
        print("❌ Opik is NOT installed")
        print("\n📦 Installing Opik...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "opik"], check=True)
            print("✅ Opik installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Opik")
            return False

def check_opik_configured():
    """Check if Opik is configured."""
    print("\n🔧 Checking Opik configuration...")
    
    # Check for Opik config
    opik_config_file = os.path.expanduser("~/.opik.config")
    if os.path.exists(opik_config_file):
        print("✅ Opik is configured")
        return True
    
    # Check environment variables
    if os.getenv("OPIK_API_KEY"):
        print("✅ Opik API key found in environment")
        return True
    
    print("⚠️  Opik not configured")
    print("\n📝 To configure Opik, run:")
    print("   opik configure")
    print("\n   Or set environment variables:")
    print("   OPIK_API_KEY=your_api_key")
    print("   OPIK_WORKSPACE=your_workspace")
    
    return False

def show_summary():
    """Show implementation summary."""
    print("\n" + "="*70)
    print("Enhanced Opik Integration - Implementation Summary")
    print("="*70)
    
    print("\n✅ Files Created/Modified:")
    print("   1. backend/services/chat_service_enhanced.py - Enhanced chat service")
    print("   2. backend/main.py - Updated with enhanced tracking")
    print("   3. test_enhanced_opik.py - Test script")
    print("   4. ENHANCED_OPIK_GUIDE.md - Complete documentation")
    
    print("\n🎯 What's New:")
    print("   • Nested spans showing complete RAG flow")
    print("   • Query preprocessing tracking")
    print("   • Document retrieval metrics")
    print("   • Reranking/filtering stats")
    print("   • Context building details")
    print("   • LLM generation with token counts")
    print("   • Cost estimation per query")
    print("   • Performance metrics at each step")
    
    print("\n📊 Enhanced Traces Include:")
    print("   ├─ query_preprocessing")
    print("   ├─ document_retrieval")
    print("   ├─ document_reranking")
    print("   ├─ context_building")
    print("   └─ llm_generation")
    
    print("\n🎨 Rich Metadata:")
    print("   • User IDs and timestamps")
    print("   • Document names and counts")
    print("   • Similarity scores and confidence")
    print("   • Token usage (input/output/total)")
    print("   • Cost estimates")
    print("   • Processing times")
    print("   • Model information")

def show_next_steps():
    """Show next steps."""
    print("\n" + "="*70)
    print("🚀 Next Steps")
    print("="*70)
    
    print("\n1. Restart your FastAPI server:")
    print("   • Stop current server (if running)")
    print("   • Run: uvicorn backend.main:app --reload --port 8000")
    
    print("\n2. Test the enhanced tracking:")
    print("   • Run: python test_enhanced_opik.py")
    print("   • Or make a query through your frontend")
    
    print("\n3. View traces in Opik dashboard:")
    print("   • Go to: https://www.comet.com/opik")
    print("   • Look for project: 'rag-system'")
    print("   • Click on traces to see nested spans")
    
    print("\n4. Verify enhanced traces:")
    print("   ✓ Trace name: 'rag_query_complete' (not just 'RAG Query')")
    print("   ✓ 5 nested spans visible")
    print("   ✓ Rich JSON input/output at each step")
    print("   ✓ Token counts and costs displayed")
    print("   ✓ Performance metrics shown")
    
    print("\n📚 Documentation:")
    print("   • Read: ENHANCED_OPIK_GUIDE.md")
    print("   • For customization and advanced features")

def main():
    """Main function."""
    print("\n" + "="*70)
    print("🎯 Enhanced Opik Integration - Quick Start")
    print("="*70)
    
    # Check installation
    if not check_opik_installed():
        print("\n❌ Cannot proceed without Opik")
        return
    
    # Check configuration
    configured = check_opik_configured()
    
    # Show summary
    show_summary()
    
    # Show next steps
    show_next_steps()
    
    if not configured:
        print("\n⚠️  Note: Opik is not configured. Traces will not be sent.")
        print("   The system will work but without remote tracking.")
    
    print("\n" + "="*70)
    print("✨ Setup Complete!")
    print("="*70)
    print("\n💡 Tip: Check the ENHANCED_OPIK_GUIDE.md for detailed usage")
    print()

if __name__ == "__main__":
    main()

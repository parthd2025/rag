"""
RAG Backend - Quick Health Check Script
Validates that all components are properly installed and configured.
"""

import sys
from pathlib import Path

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print("✅ Python version:", f"{version.major}.{version.minor}")
        return True
    print("❌ Python 3.10+ required, found:", f"{version.major}.{version.minor}")
    return False


def check_imports():
    """Check if all required packages are installed."""
    packages = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "sentence_transformers": "Sentence Transformers",
        "faiss": "FAISS",
        "PyPDF2": "PyPDF2",
        "docx": "python-docx",
        "streamlit": "Streamlit",
        "requests": "Requests",
        "numpy": "NumPy",
    }
    
    all_installed = True
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - Install with: pip install -r requirements.txt")
            all_installed = False
    
    return all_installed


def check_llm_optional():
    """Check for optional LLM packages."""
    packages = {
        "transformers": "Transformers (for HuggingFace models)",
        "torch": "PyTorch (for GPU support)",
    }
    
    print("\nOptional LLM packages:")
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"⚠️  {name} - For enhanced functionality")


def check_directories():
    """Check if required directories exist."""
    dirs = {
        "backend": "Backend code",
        "frontend": "Frontend code",
        "data": "Data storage",
        "models": "LLM models",
    }
    
    all_exist = True
    for dir_name, description in dirs.items():
        path = Path(dir_name)
        if path.exists():
            print(f"✅ {dir_name}/ - {description}")
        else:
            print(f"❌ {dir_name}/ - {description} - Missing!")
            all_exist = False
    
    return all_exist


def check_cloud_setup():
    """Check if Groq API is configured."""
    import os
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        print("✅ Groq API key configured")
        return True
    else:
        print("⚠️  GROQ_API_KEY not found in environment")
        print("   Get a free API key at: https://console.groq.com/keys")
        return False


def check_api():
    """Try to connect to running API (if available)."""
    try:
        import requests
        response = requests.get("http://localhost:8001/health", timeout=2)
        if response.status_code == 200:
            print("✅ API running at http://localhost:8001")
            return True
    except:
        print("ℹ️  API not running (start with: python backend/main.py)")
        return False


def main():
    print("\n" + "="*50)
    print("RAG Chatbot - Health Check")
    print("="*50 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_imports),
        ("Directories", check_directories),
        ("Groq API Setup", check_cloud_setup),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 40)
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error during check: {e}")
            results.append((name, False))
    
    check_llm_optional()
    
    print("\n" + "="*50)
    print("Optional: API Connection")
    print("="*50 + "\n")
    check_api()
    
    # Summary
    print("\n" + "="*50)
    print("Summary")
    print("="*50)
    
    all_passed = all(result for _, result in results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print("\n" + "="*50)
    if all_passed:
        print("✅ Everything looks good! Ready to run RAG chatbot.")
        print("\nNext steps:")
        print("1. Start backend:  cd backend && python main.py")
        print("2. Start frontend: cd frontend && streamlit run app.py")
        print("3. Open browser:   http://localhost:8501")
    else:
        print("❌ Some checks failed. Please fix issues above.")
        print("\nFor help, see: QUICKSTART.md or SETUP.md")
    print("="*50 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

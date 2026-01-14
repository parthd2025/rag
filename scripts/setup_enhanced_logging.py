#!/usr/bin/env python3
"""
Quick setup script for enhanced logging in RAG system.

This script:
1. Creates the log directory structure
2. Verifies the new logger_config_enhanced.py is in place
3. Shows you which files to update
4. Provides sample commands for monitoring

Usage:
    python setup_enhanced_logging.py
    python setup_enhanced_logging.py --check
    python setup_enhanced_logging.py --migrate document_service
"""

import os
import sys
import argparse
from pathlib import Path


class LoggingSetup:
    """Helper class for enhanced logging setup."""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            # Find project root (where src/ exists)
            self.project_root = Path(__file__).parent.parent
        else:
            self.project_root = Path(project_root)
        
        self.logs_dir = self.project_root / "logs"
        self.src_dir = self.project_root / "src"
        self.backend_dir = self.src_dir / "backend"
    
    def print_header(self, text: str, width: int = 70):
        """Print formatted header."""
        print("\n" + "=" * width)
        print(f"  {text}")
        print("=" * width + "\n")
    
    def print_section(self, text: str):
        """Print section header."""
        print(f"\n{'─' * 70}")
        print(f"  {text}")
        print(f"{'─' * 70}\n")
    
    def create_directory_structure(self) -> bool:
        """Create log directory structure."""
        self.print_section("📁 Creating Log Directory Structure")
        
        directories = [
            self.logs_dir,
            self.logs_dir / "components",
            self.logs_dir / "frontend",
            self.logs_dir / "debug",
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"  ✅ {directory.relative_to(self.project_root)}")
            except Exception as e:
                print(f"  ❌ {directory}: {e}")
                return False
        
        return True
    
    def verify_logger_config(self) -> bool:
        """Verify enhanced logger config exists."""
        self.print_section("🔍 Verifying Enhanced Logger Config")
        
        logger_file = self.backend_dir / "logger_config_enhanced.py"
        
        if logger_file.exists():
            print(f"  ✅ {logger_file.relative_to(self.project_root)} exists")
            return True
        else:
            print(f"  ❌ {logger_file.relative_to(self.project_root)} not found")
            print(f"\n  To create it, run:")
            print(f"    cp src/backend/logger_config.py src/backend/logger_config_enhanced.py")
            return False
    
    def show_modules_to_migrate(self) -> None:
        """Show which modules should be migrated."""
        self.print_section("📋 Modules Ready for Migration")
        
        modules = {
            "Document Processing": [
                ("src/backend/services/document_service.py", "document_ingestion"),
                ("src/backend/ingest/ingestor.py", "document_ingestion"),
            ],
            "Vector Store": [
                ("src/backend/vector_store.py", "vector_store"),
                ("src/backend/data/index_manager.py", "vector_store"),
            ],
            "LLM Operations": [
                ("src/backend/llm_engine.py", "llm_queries"),
                ("src/backend/llm_tracked.py", "llm_queries"),
            ],
            "API Endpoints": [
                ("src/backend/main.py", "api_endpoints"),
                ("src/backend/services/chat_service.py", "api_endpoints"),
            ],
            "RAG Engine": [
                ("src/backend/rag_engine.py", "rag_engine"),
            ],
            "Dataset Management": [
                ("src/backend/services/dataset_service.py", "dataset"),
            ],
            "Frontend": [
                ("src/frontend/app.py", "frontend"),
            ],
        }
        
        total_files = sum(len(files) for files in modules.values())
        
        for category, files in modules.items():
            print(f"\n  📂 {category}")
            for file_path, module_name in files:
                full_path = self.project_root / file_path
                status = "✅" if full_path.exists() else "⚠️ "
                print(f"     {status} {file_path}")
                print(f"        └─ Use module: '{module_name}'")
        
        print(f"\n  📊 Total files to migrate: {total_files}")
    
    def show_available_modules(self) -> None:
        """Show all available module categories."""
        self.print_section("🏷️  Available Module Categories")
        
        modules = {
            "document_ingestion": "Document processing, chunking, embedding → logs/components/document_ingestion.log",
            "vector_store": "FAISS indexing and retrieval → logs/components/vector_store.log",
            "llm_queries": "LLM API calls and responses → logs/components/llm_queries.log",
            "api_endpoints": "FastAPI HTTP requests/responses → logs/components/api_endpoints.log",
            "opik_tracing": "Observability and tracing events → logs/components/opik_tracing.log",
            "rag_engine": "RAG pipeline operations → logs/components/rag_engine.log",
            "dataset": "Dataset management operations → logs/components/dataset_service.log",
            "frontend": "Streamlit frontend interactions → logs/frontend/streamlit_app.log",
            "error": "All ERROR and CRITICAL logs → logs/errors.log",
            "debug": "Development debug logs → logs/debug/debug.log",
            "general": "General application logs → logs/rag_system.log",
        }
        
        for module, description in modules.items():
            print(f"  '{module}'")
            print(f"    {description}\n")
    
    def show_usage_examples(self) -> None:
        """Show usage examples."""
        self.print_section("💡 Usage Examples")
        
        print("  1. Get logger in your module:\n")
        print("     from ..logger_config_enhanced import LoggerManager")
        print("     logger = LoggerManager.get_logger(__name__, 'document_ingestion')\n")
        
        print("  2. Log with context:\n")
        print("     logger.info(f'Processing | File: {filename} | Size: {size}MB')\n")
        
        print("  3. Log with timing:\n")
        print("     import time")
        print("     start = time.time()")
        print("     # do work...")
        print("     elapsed = time.time() - start")
        print("     logger.info(f'Completed | Time: {elapsed:.2f}s')\n")
        
        print("  4. Log errors with traceback:\n")
        print("     logger.error('Operation failed', exc_info=True)\n")
    
    def show_monitoring_commands(self) -> None:
        """Show commands for monitoring logs."""
        self.print_section("👁️  Monitoring Commands")
        
        commands = {
            "Watch document ingestion": "tail -f logs/components/document_ingestion.log",
            "Watch LLM queries": "tail -f logs/components/llm_queries.log",
            "Watch API endpoints": "tail -f logs/components/api_endpoints.log",
            "Watch all errors": "tail -f logs/errors.log",
            "Follow multiple logs": "tail -f logs/components/*.log logs/errors.log",
            "Search by trace ID": "grep 'a1b2c3d4' logs/components/*.log",
            "Count errors": "wc -l logs/errors.log",
            "Recent errors": "tail -50 logs/errors.log",
            "Search for warnings": "grep 'WARNING' logs/components/*.log",
            "Filter by component": "grep -E 'document_ingestion' logs/rag_system.log",
        }
        
        for description, command in commands.items():
            print(f"  {description}:")
            print(f"    $ {command}\n")
    
    def show_config_updates(self) -> None:
        """Show required config updates."""
        self.print_section("⚙️  Configuration Updates Needed")
        
        print("  1. In src/backend/config.py, add:")
        print("     ENABLE_COMPONENT_LOGS: bool = Field(True, env='ENABLE_COMPONENT_LOGS')")
        print("     DEBUG_MODE: bool = Field(False, env='DEBUG_MODE')\n")
        
        print("  2. Update .env file:")
        print("     ENABLE_COMPONENT_LOGS=true")
        print("     DEBUG_MODE=false\n")
        
        print("  3. Update imports in modules:")
        print("     OLD: from ..logger_config import logger")
        print("     NEW: from ..logger_config_enhanced import LoggerManager")
        print("          logger = LoggerManager.get_logger(__name__, 'module_name')\n")
    
    def show_migration_plan(self) -> None:
        """Show recommended migration plan."""
        self.print_section("📈 Recommended Migration Plan")
        
        phases = {
            "Phase 1: Preparation (Day 1)": [
                "✓ Create log directory structure",
                "✓ Deploy logger_config_enhanced.py",
                "✓ Update config.py with new settings",
                "✓ Test logger manually",
            ],
            "Phase 2: High-Impact Modules (Days 2-3)": [
                "→ Migrate document_service.py",
                "→ Migrate llm_engine.py",
                "→ Migrate vector_store.py",
                "→ Test and verify logs",
            ],
            "Phase 3: API & Services (Days 4-5)": [
                "→ Migrate main.py API endpoints",
                "→ Migrate chat_service.py",
                "→ Migrate dataset_service.py",
                "→ Add trace ID support",
            ],
            "Phase 4: Frontend & Cleanup (Days 6-7)": [
                "→ Migrate frontend/app.py",
                "→ Set up log monitoring",
                "→ Test end-to-end",
                "→ Document learnings",
            ],
        }
        
        for phase, items in phases.items():
            print(f"\n  {phase}")
            for item in items:
                print(f"    {item}")
    
    def show_troubleshooting(self) -> None:
        """Show troubleshooting tips."""
        self.print_section("🔧 Troubleshooting")
        
        tips = {
            "Logs not appearing": [
                "1. Check module name is in LoggerManager._module_paths",
                "2. Verify logger was created with correct module parameter",
                "3. Check LOG_LEVEL setting is not too high (try DEBUG)",
            ],
            "Permission errors": [
                "1. Check logs/ directory is writable",
                "2. chmod 755 logs/",
                "3. Check disk space: df -h",
            ],
            "Too many log files": [
                "1. Adjust LOG_MAX_BYTES in config.py (currently 10MB)",
                "2. Reduce LOG_BACKUP_COUNT (currently 5 backups)",
                "3. Archive old logs to different location",
            ],
            "High disk usage": [
                "1. Check size of individual log files: du -h logs/",
                "2. Reduce logging verbosity: set LOG_LEVEL=WARNING",
                "3. Implement log cleanup script for rotation",
            ],
        }
        
        for issue, solutions in tips.items():
            print(f"  ❓ {issue}")
            for solution in solutions:
                print(f"     {solution}")
            print()
    
    def run_check(self) -> None:
        """Run full system check."""
        self.print_section("🏥 System Check")
        
        checks = []
        
        # Check 1: Logs directory
        logs_exist = self.logs_dir.exists()
        checks.append(("Logs directory exists", logs_exist))
        
        # Check 2: Enhanced logger config
        logger_exist = (self.backend_dir / "logger_config_enhanced.py").exists()
        checks.append(("Enhanced logger config exists", logger_exist))
        
        # Check 3: Original logger config
        orig_logger = (self.backend_dir / "logger_config.py").exists()
        checks.append(("Original logger config exists", orig_logger))
        
        # Check 4: Disk space
        stat = os.statvfs(self.logs_dir.parent)
        available_gb = stat.f_bavail * stat.f_frsize / (1024 ** 3)
        disk_ok = available_gb > 1  # At least 1GB free
        checks.append((f"Disk space available ({available_gb:.1f}GB)", disk_ok))
        
        # Check 5: Log file sizes
        if self.logs_dir.exists():
            log_file = self.logs_dir / "rag_system.log"
            if log_file.exists():
                size_mb = log_file.stat().st_size / (1024 ** 2)
                checks.append((f"Current rag_system.log size ({size_mb:.1f}MB)", True))
        
        passed = sum(1 for _, result in checks if result)
        total = len(checks)
        
        for check, result in checks:
            status = "✅" if result else "❌"
            print(f"  {status} {check}")
        
        print(f"\n  Result: {passed}/{total} checks passed")
        
        if passed == total:
            print("  ✨ System ready for logging migration!")
        else:
            print("  ⚠️  Please fix failing checks before migrating")
    
    def show_full_guide(self) -> None:
        """Show complete guide."""
        self.print_header("🚀 ENHANCED LOGGING SETUP GUIDE")
        
        self.create_directory_structure()
        self.verify_logger_config()
        self.show_available_modules()
        self.show_modules_to_migrate()
        self.show_usage_examples()
        self.show_monitoring_commands()
        self.show_config_updates()
        self.show_migration_plan()
        self.show_troubleshooting()
        
        self.print_section("✅ Next Steps")
        print("  1. Read docs/LOGGING_BEST_PRACTICES.md")
        print("  2. Review docs/LOGGING_MIGRATION_EXAMPLES.md")
        print("  3. Start with Phase 1 (preparation)")
        print("  4. Run: python setup_enhanced_logging.py --check")
        print("  5. Migrate one module at a time\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Setup enhanced logging for RAG system")
    parser.add_argument("--check", action="store_true", help="Run system check only")
    parser.add_argument("--create-dirs", action="store_true", help="Create log directories")
    parser.add_argument("--modules", action="store_true", help="Show available modules")
    parser.add_argument("--examples", action="store_true", help="Show usage examples")
    parser.add_argument("--monitoring", action="store_true", help="Show monitoring commands")
    parser.add_argument("--plan", action="store_true", help="Show migration plan")
    parser.add_argument("--troubleshoot", action="store_true", help="Show troubleshooting tips")
    
    args = parser.parse_args()
    
    setup = LoggingSetup()
    
    if args.check:
        setup.run_check()
    elif args.create_dirs:
        setup.create_directory_structure()
    elif args.modules:
        setup.show_available_modules()
    elif args.examples:
        setup.show_usage_examples()
    elif args.monitoring:
        setup.show_monitoring_commands()
    elif args.plan:
        setup.show_migration_plan()
    elif args.troubleshoot:
        setup.show_troubleshooting()
    else:
        # Default: show full guide
        setup.show_full_guide()
        setup.run_check()


if __name__ == "__main__":
    main()

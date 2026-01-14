"""
Log Manager - Handle log archiving, cleanup, and reporting.

Features:
- Archive logs older than retention period
- Cleanup old files
- Generate log statistics
- Update symlinks
"""

import os
import shutil
import tarfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from .config import settings


class LogManager:
    """Manage log files - cleanup, archiving, etc."""
    
    @staticmethod
    def archive_old_logs(days: int = None, delete_after: bool = True) -> int:
        """
        Archive logs older than specified days.
        
        Args:
            days: Number of days to keep (default from config)
            delete_after: Delete original folder after archiving
            
        Returns:
            Number of folders archived
        """
        if days is None:
            days = settings.LOG_RETENTION_DAYS
        
        base_logs_dir = Path(settings.BASE_LOG_DIR)
        cutoff_date = datetime.now() - timedelta(days=days)
        archived_count = 0
        
        for category in ["backend", "frontend"]:
            category_dir = base_logs_dir / category
            
            if not category_dir.exists():
                continue
            
            # Find old date folders
            for date_folder in sorted(category_dir.iterdir()):
                if not date_folder.is_dir() or date_folder.name in ["current", "archive"]:
                    continue
                
                try:
                    folder_date = datetime.strptime(date_folder.name, "%Y-%m-%d")
                    
                    if folder_date < cutoff_date:
                        # Archive this folder
                        if LogManager._archive_folder(date_folder, category_dir):
                            archived_count += 1
                            if delete_after:
                                shutil.rmtree(date_folder)
                
                except ValueError:
                    # Skip if folder name is not a date
                    continue
        
        return archived_count
    
    @staticmethod
    def _archive_folder(folder_path: Path, category_dir: Path) -> bool:
        """
        Archive a folder to tar.gz.
        
        Returns:
            True if successful, False otherwise
        """
        archive_dir = category_dir / "archive"
        archive_dir.mkdir(exist_ok=True)
        
        archive_name = f"{folder_path.name}_logs.tar.gz"
        archive_path = archive_dir / archive_name
        
        try:
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(folder_path, arcname=folder_path.name)
            
            return True
            
        except Exception as e:
            print(f"Error archiving {folder_path}: {e}")
            return False
    
    @staticmethod
    def cleanup_old_logs(days: int = None) -> int:
        """Delete logs older than retention period."""
        if days is None:
            days = settings.LOG_RETENTION_DAYS
        
        base_logs_dir = Path(settings.BASE_LOG_DIR)
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for category in ["backend", "frontend"]:
            category_dir = base_logs_dir / category
            
            if not category_dir.exists():
                continue
            
            for date_folder in category_dir.iterdir():
                if not date_folder.is_dir() or date_folder.name in ["current", "archive"]:
                    continue
                
                try:
                    folder_date = datetime.strptime(date_folder.name, "%Y-%m-%d")
                    
                    if folder_date < cutoff_date:
                        shutil.rmtree(date_folder)
                        deleted_count += 1
                
                except ValueError:
                    continue
        
        return deleted_count
    
    @staticmethod
    def get_log_stats() -> Dict:
        """Get statistics about log directory."""
        base_logs_dir = Path(settings.BASE_LOG_DIR)
        
        stats = {
            "backend": {
                "total_size_mb": 0,
                "total_files": 0,
                "total_days": 0,
                "error_count": 0,
                "error_size_mb": 0,
            },
            "frontend": {
                "total_size_mb": 0,
                "total_files": 0,
                "total_days": 0,
                "error_count": 0,
                "error_size_mb": 0,
            },
            "archive": {
                "total_size_mb": 0,
                "total_files": 0,
            },
        }
        
        for category in ["backend", "frontend"]:
            category_dir = base_logs_dir / category
            
            if not category_dir.exists():
                continue
            
            # Count date folders and files
            for date_folder in category_dir.iterdir():
                if not date_folder.is_dir() or date_folder.name in ["current", "archive"]:
                    continue
                
                stats[category]["total_days"] += 1
                
                for log_file in date_folder.glob("*.log"):
                    size_mb = log_file.stat().st_size / (1024 * 1024)
                    stats[category]["total_size_mb"] += size_mb
                    stats[category]["total_files"] += 1
                    
                    # Count errors
                    if log_file.name == "errors.log":
                        with open(log_file, 'r', errors='ignore') as f:
                            stats[category]["error_count"] += sum(1 for _ in f)
                        stats[category]["error_size_mb"] += size_mb
        
        # Count archive
        for category in ["backend", "frontend"]:
            archive_dir = base_logs_dir / category / "archive"
            if archive_dir.exists():
                for archive_file in archive_dir.glob("*.tar.gz"):
                    size_mb = archive_file.stat().st_size / (1024 * 1024)
                    stats["archive"]["total_size_mb"] += size_mb
                    stats["archive"]["total_files"] += 1
        
        return stats
    
    @staticmethod
    def print_log_report() -> None:
        """Print log directory report."""
        stats = LogManager.get_log_stats()
        
        print("\n" + "=" * 70)
        print("LOG DIRECTORY REPORT")
        print("=" * 70 + "\n")
        
        for category in ["backend", "frontend"]:
            cat_stats = stats[category]
            print(f"📁 {category.upper()}")
            print(f"   Total size: {cat_stats['total_size_mb']:.2f} MB")
            print(f"   Total files: {cat_stats['total_files']}")
            print(f"   Total days: {cat_stats['total_days']}")
            print(f"   Error logs: {cat_stats['error_count']} entries ({cat_stats['error_size_mb']:.2f} MB)")
            print()
        
        arch_stats = stats["archive"]
        print(f"📦 ARCHIVE")
        print(f"   Total size: {arch_stats['total_size_mb']:.2f} MB")
        print(f"   Total files: {arch_stats['total_files']}")
        
        total_size = (stats['backend']['total_size_mb'] + 
                      stats['frontend']['total_size_mb'] + 
                      stats['archive']['total_size_mb'])
        
        print(f"\n📊 TOTAL: {total_size:.2f} MB")
        print("=" * 70 + "\n")
    
    @staticmethod
    def get_today_log_path(category: str = "backend", log_type: str = "general") -> Path:
        """Get path to today's log file."""
        base_logs_dir = Path(settings.BASE_LOG_DIR)
        today = datetime.now().strftime("%Y-%m-%d")
        
        log_types = {
            "backend": {
                "document_ingestion": "document_ingestion.log",
                "vector_store": "vector_store.log",
                "llm_queries": "llm_queries.log",
                "api_endpoints": "api_endpoints.log",
                "rag_engine": "rag_engine.log",
                "dataset": "dataset_service.log",
                "opik_tracing": "opik_tracing.log",
                "general": "general.log",
                "errors": "errors.log",
            },
            "frontend": {
                "app": "app.log",
                "pages": "pages.log",
                "chat": "chat.log",
                "library": "library.log",
                "upload": "upload.log",
                "settings": "settings.log",
                "api_client": "api_client.log",
                "general": "general.log",
                "errors": "errors.log",
            },
        }
        
        log_types_dict = log_types.get(category, log_types["backend"])
        log_filename = log_types_dict.get(log_type, "general.log")
        
        return base_logs_dir / category / today / log_filename
    
    @staticmethod
    def search_logs(pattern: str, category: str = None, log_type: str = None) -> List[Tuple[Path, int, str]]:
        """
        Search for pattern in logs.
        
        Returns:
            List of (file_path, line_number, line_content)
        """
        base_logs_dir = Path(settings.BASE_LOG_DIR)
        results = []
        
        categories = [category] if category else ["backend", "frontend"]
        
        for cat in categories:
            cat_dir = base_logs_dir / cat
            if not cat_dir.exists():
                continue
            
            # Search in date folders
            for date_folder in cat_dir.glob("*/"):
                if date_folder.name in ["archive", "current"]:
                    continue
                
                # Filter by log type if specified
                if log_type:
                    log_files = [date_folder / f"{log_type}.log"]
                else:
                    log_files = list(date_folder.glob("*.log"))
                
                for log_file in log_files:
                    if log_file.exists():
                        try:
                            with open(log_file, 'r', errors='ignore') as f:
                                for line_num, line in enumerate(f, 1):
                                    if pattern.lower() in line.lower():
                                        results.append((log_file, line_num, line.strip()))
                        except Exception as e:
                            print(f"Error reading {log_file}: {e}")
        
        return results
    
    @staticmethod
    def compress_old_logs(days: int = 7) -> int:
        """Compress logs older than specified days."""
        base_logs_dir = Path(settings.BASE_LOG_DIR)
        cutoff_date = datetime.now() - timedelta(days=days)
        compressed_count = 0
        
        for category in ["backend", "frontend"]:
            category_dir = base_logs_dir / category
            
            if not category_dir.exists():
                continue
            
            for date_folder in category_dir.iterdir():
                if not date_folder.is_dir() or date_folder.name in ["current", "archive"]:
                    continue
                
                try:
                    folder_date = datetime.strptime(date_folder.name, "%Y-%m-%d")
                    
                    if folder_date < cutoff_date:
                        # Compress log files
                        for log_file in date_folder.glob("*.log"):
                            if not log_file.with_suffix(".log.gz").exists():
                                os.system(f"gzip {log_file}")
                                compressed_count += 1
                
                except ValueError:
                    continue
        
        return compressed_count

#!/usr/bin/env python3
"""
Daily Log Maintenance Script
Runs daily to maintain the day-wise logging structure.
- Updates symlinks to current day's logs
- Archives old logs
- Generates log statistics report
- Cleans up expired logs
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backend.logger_config_day_wise import DayWiseLogger
from src.backend.log_manager import LogManager
from src.backend.config import Settings


def setup_maintenance_logger():
    """Setup logger for maintenance script itself."""
    logs_dir = Path(Settings().BASE_LOG_DIR) / "backend"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("log_maintenance")
    logger.setLevel(logging.INFO)
    
    # Log file in maintenance folder
    log_file = logs_dir / "maintenance.log"
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def run_daily_maintenance():
    """Execute all daily maintenance tasks."""
    settings = Settings()
    logger = setup_maintenance_logger()
    
    logger.info("=" * 80)
    logger.info(f"Starting daily log maintenance at {datetime.now().isoformat()}")
    logger.info("=" * 80)
    
    try:
        # Task 1: Update symlinks to current day
        logger.info("Task 1: Updating symlinks to current day's logs...")
        day_wise_logger = DayWiseLogger()
        
        backend_updated = day_wise_logger.create_symlinks(
            log_type="backend",
            force_update=True
        )
        frontend_updated = day_wise_logger.create_symlinks(
            log_type="frontend",
            force_update=True
        )
        
        if backend_updated or frontend_updated:
            logger.info(f"✓ Symlinks updated (backend={backend_updated}, frontend={frontend_updated})")
        else:
            logger.info("✓ Symlinks already up to date")
        
        # Task 2: Archive old logs
        logger.info("Task 2: Archiving logs older than retention period...")
        log_manager = LogManager()
        
        archive_config = {
            "backend": {"days": settings.LOG_RETENTION_DAYS, "delete_after": False},
            "frontend": {"days": settings.LOG_RETENTION_DAYS, "delete_after": False}
        }
        
        total_archived = 0
        for category, config in archive_config.items():
            try:
                archived_count = log_manager.archive_old_logs(
                    category=category,
                    days=config["days"],
                    delete_after=config["delete_after"]
                )
                if archived_count > 0:
                    logger.info(f"✓ Archived {archived_count} {category} log folders")
                    total_archived += archived_count
            except Exception as e:
                logger.error(f"Failed to archive {category} logs: {str(e)}")
        
        if total_archived == 0:
            logger.info("✓ No logs to archive")
        
        # Task 3: Generate statistics report
        logger.info("Task 3: Generating log statistics...")
        try:
            stats = log_manager.get_log_stats()
            
            # Log summary
            logger.info("Log Statistics Summary:")
            logger.info(f"  Total Size: {stats.get('total_size_mb', 0):.2f} MB")
            logger.info(f"  Total Files: {stats.get('total_files', 0)}")
            logger.info(f"  Total Error Logs: {stats.get('error_logs', 0)}")
            logger.info(f"  Categories: {', '.join(stats.get('categories', []))}")
            
            # Save detailed report
            report_dir = Path(settings.BASE_LOG_DIR) / "reports"
            report_dir.mkdir(parents=True, exist_ok=True)
            
            report_file = report_dir / f"daily_report_{datetime.now().strftime('%Y-%m-%d')}.json"
            with open(report_file, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
            
            logger.info(f"✓ Detailed report saved to {report_file}")
            
        except Exception as e:
            logger.error(f"Failed to generate statistics: {str(e)}")
        
        # Task 4: Cleanup expired archives
        logger.info("Task 4: Cleaning up expired archives...")
        try:
            cleanup_config = {
                "backend": {"days": settings.LOG_RETENTION_DAYS + 7},  # Delete archives after 37 days
                "frontend": {"days": settings.LOG_RETENTION_DAYS + 7}
            }
            
            total_cleaned = 0
            for category, config in cleanup_config.items():
                try:
                    cleaned_count = log_manager.cleanup_old_logs(
                        category=category,
                        days=config["days"]
                    )
                    if cleaned_count > 0:
                        logger.info(f"✓ Cleaned up {cleaned_count} {category} archives")
                        total_cleaned += cleaned_count
                except Exception as e:
                    logger.error(f"Failed to cleanup {category} archives: {str(e)}")
            
            if total_cleaned == 0:
                logger.info("✓ No expired archives to cleanup")
                
        except Exception as e:
            logger.error(f"Failed to cleanup archives: {str(e)}")
        
        logger.info("=" * 80)
        logger.info(f"Daily maintenance completed successfully at {datetime.now().isoformat()}")
        logger.info("=" * 80)
        return True
        
    except Exception as e:
        logger.error(f"Critical error during maintenance: {str(e)}", exc_info=True)
        return False


def print_usage():
    """Print usage information."""
    print("""
Daily Log Maintenance Script

Usage:
    python scripts/daily_log_maintenance.py [OPTIONS]

Options:
    --help              Show this help message
    --report-only       Generate report without archiving/cleanup
    --full              Run all maintenance tasks (default)

The script performs the following tasks:
    1. Update symlinks to current day's logs
    2. Archive logs older than LOG_RETENTION_DAYS (default: 30)
    3. Generate statistics report
    4. Clean up expired archives

Configuration:
    BASE_LOG_DIR            Location of centralized logs (src/logs)
    LOG_RETENTION_DAYS      Days to retain logs before archiving (30)
    ENABLE_LOG_SYMLINKS     Create symlinks to current day (true)

Scheduling:
    Linux/Mac (crontab):
        0 1 * * * cd /path/to/RAG && python scripts/daily_log_maintenance.py

    Windows (Task Scheduler):
        Create scheduled task to run:
        cmd /c "cd C:\\path\\to\\RAG && python scripts\\daily_log_maintenance.py"

Examples:
    # Run full maintenance
    python scripts/daily_log_maintenance.py

    # Generate report only
    python scripts/daily_log_maintenance.py --report-only

    # View help
    python scripts/daily_log_maintenance.py --help
    """)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Daily Log Maintenance Script",
        add_help=False
    )
    parser.add_argument("--help", action="store_true", help="Show help message")
    parser.add_argument("--report-only", action="store_true", help="Generate report only")
    parser.add_argument("--full", action="store_true", help="Run full maintenance")
    
    args = parser.parse_args()
    
    if args.help:
        print_usage()
        sys.exit(0)
    
    # Run maintenance
    success = run_daily_maintenance()
    sys.exit(0 if success else 1)

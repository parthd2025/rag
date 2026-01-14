#!/usr/bin/env python
"""
OPIK Dataset Management CLI
============================

Command-line tool for managing datasets in the RAG system.

Usage:
    python dataset_management.py create-dataset --name "Test Dataset" --description "A test dataset"
    python dataset_management.py add-test-case --dataset-id <id> --question "Q?" --answer "A."
    python dataset_management.py list-datasets
    python dataset_management.py get-dataset --dataset-id <id>
    python dataset_management.py evaluate-dataset --dataset-id <id>
    python dataset_management.py export-dataset --dataset-id <id> --format json
    python dataset_management.py import-dataset --file data.json --name "Imported" --description "Imported from file"
    python dataset_management.py add-from-csv --dataset-id <id> --file testcases.csv
    python dataset_management.py sync-to-opik --dataset-id <id>
"""

import sys
import os
import json
import argparse
import logging
from pathlib import Path
from typing import Optional, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.backend.services.dataset_service import (
    DatasetService,
    DatasetStatus,
    TestCase,
)
from src.backend.services.dataset_evaluation import DatasetEvaluator, EvaluationMetric
from src.backend.services.dataset_utils import DatasetUtils
from src.backend.logger_config import logger

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class DatasetCLI:
    """Command-line interface for dataset management."""
    
    def __init__(self, storage_path: str = "data/datasets"):
        """Initialize CLI."""
        self.dataset_service = DatasetService(storage_path=storage_path)
        self.dataset_evaluator = DatasetEvaluator(self.dataset_service)
    
    def create_dataset(self, name: str, description: str, version: str = "1.0.0",
                      domain: Optional[str] = None, tags: Optional[List[str]] = None) -> str:
        """Create a new dataset."""
        try:
            dataset_id = self.dataset_service.create_dataset(
                name=name,
                description=description,
                version=version,
                domain=domain,
                tags=tags,
            )
            print(f"✓ Dataset created successfully: {dataset_id}")
            return dataset_id
        except Exception as e:
            print(f"✗ Failed to create dataset: {e}")
            return None
    
    def add_test_case(self, dataset_id: str, question: str, ground_truth_answer: str,
                     context: Optional[str] = None, difficulty: str = "medium",
                     category: Optional[str] = None) -> Optional[str]:
        """Add a test case to a dataset."""
        try:
            test_case_id = self.dataset_service.add_test_case(
                dataset_id=dataset_id,
                question=question,
                ground_truth_answer=ground_truth_answer,
                context=context,
                difficulty_level=difficulty,
                category=category,
            )
            print(f"✓ Test case added: {test_case_id}")
            return test_case_id
        except Exception as e:
            print(f"✗ Failed to add test case: {e}")
            return None
    
    def list_datasets(self) -> None:
        """List all datasets."""
        try:
            datasets = self.dataset_service.list_datasets()
            if not datasets:
                print("No datasets found.")
                return
            
            print(f"\n{'Dataset ID':<45} {'Name':<30} {'Version':<10} {'Status':<10} {'Test Cases':<12}")
            print("-" * 110)
            
            for ds in datasets:
                test_case_count = len(self.dataset_service.get_test_cases(ds.id))
                print(f"{ds.id:<45} {ds.name:<30} {ds.version:<10} {ds.status.value:<10} {test_case_count:<12}")
        except Exception as e:
            print(f"✗ Failed to list datasets: {e}")
    
    def get_dataset(self, dataset_id: str) -> None:
        """Get dataset details."""
        try:
            metadata = self.dataset_service.get_dataset(dataset_id)
            if not metadata:
                print(f"✗ Dataset not found: {dataset_id}")
                return
            
            test_cases = self.dataset_service.get_test_cases(dataset_id)
            stats = self.dataset_service.get_statistics(dataset_id)
            
            print(f"\n=== Dataset: {metadata.name} ===")
            print(f"ID: {metadata.id}")
            print(f"Description: {metadata.description}")
            print(f"Version: {metadata.version}")
            print(f"Status: {metadata.status.value}")
            print(f"Domain: {metadata.domain or 'N/A'}")
            print(f"Tags: {', '.join(metadata.tags) if metadata.tags else 'N/A'}")
            print(f"Test Cases: {len(test_cases)}")
            print(f"Created: {metadata.created_at}")
            print(f"Updated: {metadata.updated_at}")
            
            print(f"\n--- Statistics ---")
            print(json.dumps(stats, indent=2))
            
            if test_cases:
                print(f"\n--- First 5 Test Cases ---")
                for idx, tc in enumerate(test_cases[:5], 1):
                    print(f"\n{idx}. Q: {tc.question[:60]}...")
                    print(f"   A: {tc.ground_truth_answer[:60]}...")
                    print(f"   Difficulty: {tc.difficulty_level}, Category: {tc.category}")
        
        except Exception as e:
            print(f"✗ Failed to get dataset: {e}")
    
    def add_from_csv(self, dataset_id: str, csv_file: str) -> None:
        """Add test cases from CSV file."""
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                csv_content = f.read()
            
            test_cases = DatasetUtils.csv_to_test_cases(csv_content)
            if not test_cases:
                print("✗ No valid test cases found in CSV file")
                return
            
            added_ids = self.dataset_service.add_test_cases_batch(
                dataset_id=dataset_id,
                test_cases=test_cases,
            )
            
            print(f"✓ Added {len(added_ids)} test cases from CSV")
        except FileNotFoundError:
            print(f"✗ CSV file not found: {csv_file}")
        except Exception as e:
            print(f"✗ Failed to add test cases from CSV: {e}")
    
    def export_dataset(self, dataset_id: str, output_file: str, format: str = "json") -> None:
        """Export dataset to file."""
        try:
            data = self.dataset_service.export_dataset(dataset_id, format=format)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                if format == "json":
                    json.dump(data, f, indent=2)
                else:
                    f.write(data)
            
            print(f"✓ Dataset exported to: {output_file}")
        except Exception as e:
            print(f"✗ Failed to export dataset: {e}")
    
    def import_dataset(self, file_path: str, name: str, description: str, version: str = "1.0.0") -> None:
        """Import dataset from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # Determine format
            if file_path.endswith('.json'):
                test_cases = DatasetUtils.json_to_test_cases(file_content)
            elif file_path.endswith('.csv'):
                test_cases = DatasetUtils.csv_to_test_cases(file_content)
            else:
                print("✗ Unsupported file format. Use .json or .csv")
                return
            
            if not test_cases:
                print("✗ No valid test cases found in file")
                return
            
            dataset_id = self.dataset_service.create_dataset(
                name=name,
                description=description,
                version=version,
            )
            
            added_ids = self.dataset_service.add_test_cases_batch(
                dataset_id=dataset_id,
                test_cases=test_cases,
            )
            
            print(f"✓ Dataset imported: {dataset_id}")
            print(f"  Added {len(added_ids)} test cases")
        except FileNotFoundError:
            print(f"✗ File not found: {file_path}")
        except Exception as e:
            print(f"✗ Failed to import dataset: {e}")
    
    def update_status(self, dataset_id: str, status: str) -> None:
        """Update dataset status."""
        try:
            dataset_status = DatasetStatus(status)
            self.dataset_service.update_dataset_status(dataset_id, dataset_status)
            print(f"✓ Dataset status updated to: {status}")
        except ValueError:
            print(f"✗ Invalid status. Use: draft, active, archived, deprecated")
        except Exception as e:
            print(f"✗ Failed to update status: {e}")
    
    def sync_to_opik(self, dataset_id: str) -> None:
        """Sync dataset to OPIK cloud."""
        try:
            opik_id = self.dataset_service.sync_to_opik(dataset_id)
            if opik_id:
                print(f"✓ Dataset synced to OPIK: {opik_id}")
            else:
                print("✗ OPIK sync not available")
        except Exception as e:
            print(f"✗ Failed to sync to OPIK: {e}")
    
    def generate_sample(self, name: str, description: str, count: int = 5) -> None:
        """Generate a sample dataset."""
        try:
            dataset_id = self.dataset_service.create_dataset(
                name=name,
                description=description,
            )
            
            sample_cases = DatasetUtils.generate_sample_dataset(count)
            added_ids = self.dataset_service.add_test_cases_batch(
                dataset_id=dataset_id,
                test_cases=sample_cases,
            )
            
            print(f"✓ Sample dataset created: {dataset_id}")
            print(f"  Added {len(added_ids)} sample test cases")
        except Exception as e:
            print(f"✗ Failed to generate sample dataset: {e}")
    
    def show_template(self) -> None:
        """Show test case template."""
        template = DatasetUtils.generate_test_case_template()
        print("\n=== Test Case Template ===")
        print(json.dumps(template, indent=2))


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OPIK Dataset Management CLI"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create dataset
    create_parser = subparsers.add_parser("create-dataset", help="Create a new dataset")
    create_parser.add_argument("--name", required=True, help="Dataset name")
    create_parser.add_argument("--description", required=True, help="Dataset description")
    create_parser.add_argument("--version", default="1.0.0", help="Version (default: 1.0.0)")
    create_parser.add_argument("--domain", help="Domain/category")
    create_parser.add_argument("--tags", nargs="+", help="Tags")
    
    # Add test case
    add_tc_parser = subparsers.add_parser("add-test-case", help="Add test case to dataset")
    add_tc_parser.add_argument("--dataset-id", required=True, help="Dataset ID")
    add_tc_parser.add_argument("--question", required=True, help="Question")
    add_tc_parser.add_argument("--answer", required=True, help="Ground truth answer")
    add_tc_parser.add_argument("--context", help="Context")
    add_tc_parser.add_argument("--difficulty", default="medium", help="Difficulty (easy/medium/hard)")
    add_tc_parser.add_argument("--category", help="Category")
    
    # List datasets
    subparsers.add_parser("list-datasets", help="List all datasets")
    
    # Get dataset
    get_parser = subparsers.add_parser("get-dataset", help="Get dataset details")
    get_parser.add_argument("--dataset-id", required=True, help="Dataset ID")
    
    # Add from CSV
    csv_parser = subparsers.add_parser("add-from-csv", help="Add test cases from CSV")
    csv_parser.add_argument("--dataset-id", required=True, help="Dataset ID")
    csv_parser.add_argument("--file", required=True, help="CSV file path")
    
    # Export dataset
    export_parser = subparsers.add_parser("export-dataset", help="Export dataset")
    export_parser.add_argument("--dataset-id", required=True, help="Dataset ID")
    export_parser.add_argument("--output", required=True, help="Output file path")
    export_parser.add_argument("--format", default="json", help="Format (json, csv)")
    
    # Import dataset
    import_parser = subparsers.add_parser("import-dataset", help="Import dataset from file")
    import_parser.add_argument("--file", required=True, help="File path")
    import_parser.add_argument("--name", required=True, help="Dataset name")
    import_parser.add_argument("--description", required=True, help="Dataset description")
    import_parser.add_argument("--version", default="1.0.0", help="Version")
    
    # Update status
    status_parser = subparsers.add_parser("update-status", help="Update dataset status")
    status_parser.add_argument("--dataset-id", required=True, help="Dataset ID")
    status_parser.add_argument("--status", required=True, help="Status (draft/active/archived/deprecated)")
    
    # Sync to OPIK
    sync_parser = subparsers.add_parser("sync-to-opik", help="Sync dataset to OPIK")
    sync_parser.add_argument("--dataset-id", required=True, help="Dataset ID")
    
    # Generate sample
    sample_parser = subparsers.add_parser("generate-sample", help="Generate sample dataset")
    sample_parser.add_argument("--name", required=True, help="Dataset name")
    sample_parser.add_argument("--description", required=True, help="Dataset description")
    sample_parser.add_argument("--count", type=int, default=5, help="Number of test cases")
    
    # Show template
    subparsers.add_parser("show-template", help="Show test case template")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI
    cli = DatasetCLI()
    
    # Execute command
    if args.command == "create-dataset":
        cli.create_dataset(
            name=args.name,
            description=args.description,
            version=args.version,
            domain=args.domain,
            tags=args.tags,
        )
    
    elif args.command == "add-test-case":
        cli.add_test_case(
            dataset_id=args.dataset_id,
            question=args.question,
            ground_truth_answer=args.answer,
            context=args.context,
            difficulty=args.difficulty,
            category=args.category,
        )
    
    elif args.command == "list-datasets":
        cli.list_datasets()
    
    elif args.command == "get-dataset":
        cli.get_dataset(args.dataset_id)
    
    elif args.command == "add-from-csv":
        cli.add_from_csv(args.dataset_id, args.file)
    
    elif args.command == "export-dataset":
        cli.export_dataset(args.dataset_id, args.output, args.format)
    
    elif args.command == "import-dataset":
        cli.import_dataset(args.file, args.name, args.description, args.version)
    
    elif args.command == "update-status":
        cli.update_status(args.dataset_id, args.status)
    
    elif args.command == "sync-to-opik":
        cli.sync_to_opik(args.dataset_id)
    
    elif args.command == "generate-sample":
        cli.generate_sample(args.name, args.description, args.count)
    
    elif args.command == "show-template":
        cli.show_template()


if __name__ == "__main__":
    main()

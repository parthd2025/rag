"""
Dataset Management Service for OPIK Integration
===============================================

Provides comprehensive dataset management for RAG evaluation:
- Create and manage test datasets
- Store test cases (question-answer pairs with ground truth)
- Version control for datasets
- Integration with OPIK Datasets API
- Evaluation against datasets

Features:
- Dataset CRUD operations
- Test case management
- Metadata tracking
- OPIK API integration for cloud storage
- Local caching
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib
import logging

from ..logger_config import logger
from ..config import settings

try:
    from opik import Client
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False


class DatasetStatus(str, Enum):
    """Dataset lifecycle status."""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


@dataclass
class TestCase:
    """Individual test case in a dataset."""
    id: str
    question: str
    ground_truth_answer: str
    context: Optional[str] = None
    expected_sources: Optional[List[str]] = None
    difficulty_level: Optional[str] = None  # easy, medium, hard
    category: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestCase":
        """Create from dictionary."""
        return cls(**data)
    
    def get_hash(self) -> str:
        """Get unique hash for this test case."""
        content = f"{self.question}:{self.ground_truth_answer}"
        return hashlib.md5(content.encode()).hexdigest()


@dataclass
class DatasetMetadata:
    """Metadata for a dataset."""
    id: str
    name: str
    description: str
    version: str
    status: DatasetStatus = DatasetStatus.DRAFT
    created_by: str = "system"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    test_case_count: int = 0
    tags: List[str] = field(default_factory=list)
    domain: Optional[str] = None  # e.g., "automotive", "general"
    source: Optional[str] = None  # Where the data came from
    evaluation_metrics: Dict[str, Any] = field(default_factory=dict)
    opik_dataset_id: Optional[str] = None  # ID in OPIK cloud
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatasetMetadata":
        """Create from dictionary."""
        if isinstance(data.get('status'), str):
            data['status'] = DatasetStatus(data['status'])
        return cls(**data)


@dataclass
class DatasetEvaluationResult:
    """Result of evaluating RAG outputs against a dataset."""
    dataset_id: str
    evaluation_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    test_case_count: int = 0
    passed: int = 0
    failed: int = 0
    accuracy: float = 0.0
    metrics: Dict[str, Any] = field(default_factory=dict)
    details: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class DatasetService:
    """
    Service for managing datasets and test cases.
    
    Provides:
    - Dataset CRUD operations
    - Test case management
    - OPIK integration
    - Local persistence
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize dataset service.
        
        Args:
            storage_path: Base path for local dataset storage (default: data/datasets)
        """
        self.storage_path = Path(storage_path or "data/datasets")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.datasets: Dict[str, DatasetMetadata] = {}
        self.test_cases: Dict[str, List[TestCase]] = {}  # dataset_id -> test cases
        self.opik_client = None
        
        if OPIK_AVAILABLE:
            try:
                from ..opik_config import get_opik_manager
                opik_manager = get_opik_manager()
                if opik_manager.available and opik_manager.client:
                    self.opik_client = opik_manager.client
                    logger.info("OPIK client available for dataset operations")
            except Exception as e:
                logger.warning(f"Could not initialize OPIK client: {e}")
        
        self._load_datasets()
    
    def _get_dataset_dir(self, dataset_id: str) -> Path:
        """Get directory for a dataset."""
        return self.storage_path / dataset_id
    
    def _get_metadata_file(self, dataset_id: str) -> Path:
        """Get metadata file path for a dataset."""
        return self._get_dataset_dir(dataset_id) / "metadata.json"
    
    def _get_testcases_file(self, dataset_id: str) -> Path:
        """Get test cases file path for a dataset."""
        return self._get_dataset_dir(dataset_id) / "testcases.json"
    
    def _load_datasets(self) -> None:
        """Load all datasets from local storage."""
        try:
            for dataset_dir in self.storage_path.iterdir():
                if dataset_dir.is_dir():
                    metadata_file = dataset_dir / "metadata.json"
                    if metadata_file.exists():
                        with open(metadata_file, 'r') as f:
                            metadata_data = json.load(f)
                            metadata = DatasetMetadata.from_dict(metadata_data)
                            self.datasets[metadata.id] = metadata
                        
                        # Load test cases
                        testcases_file = dataset_dir / "testcases.json"
                        if testcases_file.exists():
                            with open(testcases_file, 'r') as f:
                                testcases_data = json.load(f)
                                self.test_cases[metadata.id] = [
                                    TestCase.from_dict(tc) for tc in testcases_data
                                ]
                        logger.info(f"Loaded dataset: {metadata.id} (v{metadata.version})")
        except Exception as e:
            logger.error(f"Error loading datasets: {e}")
    
    def _save_dataset(self, dataset_id: str) -> None:
        """Save dataset and test cases to local storage."""
        if dataset_id not in self.datasets:
            raise ValueError(f"Dataset not found: {dataset_id}")
        
        dataset_dir = self._get_dataset_dir(dataset_id)
        dataset_dir.mkdir(parents=True, exist_ok=True)
        
        # Save metadata
        metadata_file = self._get_metadata_file(dataset_id)
        with open(metadata_file, 'w') as f:
            json.dump(self.datasets[dataset_id].to_dict(), f, indent=2)
        
        # Save test cases
        testcases_file = self._get_testcases_file(dataset_id)
        test_cases = self.test_cases.get(dataset_id, [])
        with open(testcases_file, 'w') as f:
            json.dump([tc.to_dict() for tc in test_cases], f, indent=2)
    
    def create_dataset(
        self,
        name: str,
        description: str,
        version: str = "1.0.0",
        domain: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Create a new dataset.
        
        Args:
            name: Dataset name
            description: Dataset description
            version: Version number (default: 1.0.0)
            domain: Domain/category of dataset
            tags: List of tags for categorization
            
        Returns:
            Dataset ID
        """
        # Generate dataset ID
        timestamp = int(time.time() * 1000)
        dataset_id = f"dataset_{name.lower().replace(' ', '_')}_{timestamp}"
        
        metadata = DatasetMetadata(
            id=dataset_id,
            name=name,
            description=description,
            version=version,
            domain=domain,
            tags=tags or [],
        )
        
        self.datasets[dataset_id] = metadata
        self.test_cases[dataset_id] = []
        
        self._save_dataset(dataset_id)
        logger.info(f"Created dataset: {dataset_id}")
        
        return dataset_id
    
    def add_test_case(
        self,
        dataset_id: str,
        question: str,
        ground_truth_answer: str,
        context: Optional[str] = None,
        expected_sources: Optional[List[str]] = None,
        difficulty_level: Optional[str] = None,
        category: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add a test case to a dataset.
        
        Args:
            dataset_id: Dataset ID
            question: Test question
            ground_truth_answer: Expected/ground truth answer
            context: Optional context
            expected_sources: Expected source documents
            difficulty_level: easy/medium/hard
            category: Test case category
            metadata: Additional metadata
            
        Returns:
            Test case ID
        """
        if dataset_id not in self.datasets:
            raise ValueError(f"Dataset not found: {dataset_id}")
        
        # Generate test case ID
        timestamp = int(time.time() * 1000)
        test_case_id = f"tc_{dataset_id}_{timestamp}"
        
        test_case = TestCase(
            id=test_case_id,
            question=question,
            ground_truth_answer=ground_truth_answer,
            context=context,
            expected_sources=expected_sources,
            difficulty_level=difficulty_level or "medium",
            category=category,
            metadata=metadata or {},
        )
        
        self.test_cases[dataset_id].append(test_case)
        
        # Update dataset metadata
        self.datasets[dataset_id].test_case_count = len(self.test_cases[dataset_id])
        self.datasets[dataset_id].updated_at = datetime.utcnow().isoformat()
        
        self._save_dataset(dataset_id)
        logger.info(f"Added test case to dataset {dataset_id}: {test_case_id}")
        
        return test_case_id
    
    def add_test_cases_batch(
        self,
        dataset_id: str,
        test_cases: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Add multiple test cases to a dataset.
        
        Args:
            dataset_id: Dataset ID
            test_cases: List of test case dictionaries
            
        Returns:
            List of test case IDs
        """
        test_case_ids = []
        for tc in test_cases:
            tc_id = self.add_test_case(
                dataset_id=dataset_id,
                question=tc['question'],
                ground_truth_answer=tc['ground_truth_answer'],
                context=tc.get('context'),
                expected_sources=tc.get('expected_sources'),
                difficulty_level=tc.get('difficulty_level', 'medium'),
                category=tc.get('category'),
                metadata=tc.get('metadata', {}),
            )
            test_case_ids.append(tc_id)
        
        return test_case_ids
    
    def get_dataset(self, dataset_id: str) -> Optional[DatasetMetadata]:
        """Get dataset metadata."""
        return self.datasets.get(dataset_id)
    
    def get_test_cases(self, dataset_id: str) -> List[TestCase]:
        """Get all test cases for a dataset."""
        return self.test_cases.get(dataset_id, [])
    
    def list_datasets(self, status: Optional[DatasetStatus] = None) -> List[DatasetMetadata]:
        """
        List all datasets.
        
        Args:
            status: Filter by status (optional)
            
        Returns:
            List of datasets
        """
        datasets = list(self.datasets.values())
        
        if status:
            datasets = [d for d in datasets if d.status == status]
        
        return sorted(datasets, key=lambda d: d.created_at, reverse=True)
    
    def update_dataset_status(
        self,
        dataset_id: str,
        status: DatasetStatus,
    ) -> None:
        """Update dataset status."""
        if dataset_id not in self.datasets:
            raise ValueError(f"Dataset not found: {dataset_id}")
        
        self.datasets[dataset_id].status = status
        self.datasets[dataset_id].updated_at = datetime.utcnow().isoformat()
        self._save_dataset(dataset_id)
        logger.info(f"Updated dataset {dataset_id} status to {status.value}")
    
    def delete_test_case(self, dataset_id: str, test_case_id: str) -> None:
        """Delete a test case from a dataset."""
        if dataset_id not in self.test_cases:
            raise ValueError(f"Dataset not found: {dataset_id}")
        
        self.test_cases[dataset_id] = [
            tc for tc in self.test_cases[dataset_id] if tc.id != test_case_id
        ]
        
        # Update count
        self.datasets[dataset_id].test_case_count = len(self.test_cases[dataset_id])
        self.datasets[dataset_id].updated_at = datetime.utcnow().isoformat()
        self._save_dataset(dataset_id)
        logger.info(f"Deleted test case {test_case_id} from dataset {dataset_id}")
    
    def export_dataset(self, dataset_id: str, format: str = "json") -> Dict[str, Any]:
        """
        Export dataset in specified format.
        
        Args:
            dataset_id: Dataset ID
            format: Export format (json, csv, etc.)
            
        Returns:
            Exported data
        """
        if dataset_id not in self.datasets:
            raise ValueError(f"Dataset not found: {dataset_id}")
        
        metadata = self.datasets[dataset_id]
        test_cases = self.test_cases.get(dataset_id, [])
        
        if format == "json":
            return {
                "metadata": metadata.to_dict(),
                "test_cases": [tc.to_dict() for tc in test_cases],
            }
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def import_dataset(
        self,
        name: str,
        description: str,
        data: Dict[str, Any],
        version: str = "1.0.0",
    ) -> str:
        """
        Import dataset from exported data.
        
        Args:
            name: Dataset name
            description: Dataset description
            data: Exported data (with test_cases list)
            version: Version number
            
        Returns:
            New dataset ID
        """
        dataset_id = self.create_dataset(
            name=name,
            description=description,
            version=version,
        )
        
        if "test_cases" in data:
            self.add_test_cases_batch(dataset_id, data["test_cases"])
        
        logger.info(f"Imported dataset: {dataset_id}")
        return dataset_id
    
    def sync_to_opik(self, dataset_id: str) -> Optional[str]:
        """
        Sync dataset to OPIK cloud.
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            OPIK dataset ID
        """
        if not self.opik_client or not OPIK_AVAILABLE:
            logger.warning("OPIK client not available, skipping sync")
            return None
        
        if dataset_id not in self.datasets:
            raise ValueError(f"Dataset not found: {dataset_id}")
        
        try:
            metadata = self.datasets[dataset_id]
            test_cases = self.test_cases.get(dataset_id, [])
            
            # Create dataset in OPIK
            opik_dataset = self.opik_client.create_dataset(
                name=metadata.name,
                description=metadata.description,
            )
            
            # Add examples (test cases) to OPIK dataset
            for test_case in test_cases:
                self.opik_client.create_example(
                    dataset_id=opik_dataset.id,
                    input={"question": test_case.question},
                    output={"answer": test_case.ground_truth_answer},
                    metadata=test_case.metadata,
                )
            
            # Update local metadata with OPIK ID
            metadata.opik_dataset_id = opik_dataset.id
            metadata.updated_at = datetime.utcnow().isoformat()
            self._save_dataset(dataset_id)
            
            logger.info(f"Synced dataset {dataset_id} to OPIK: {opik_dataset.id}")
            return opik_dataset.id
            
        except Exception as e:
            logger.error(f"Failed to sync dataset to OPIK: {e}")
            return None
    
    def get_statistics(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get statistics for a dataset.
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            Dataset statistics
        """
        if dataset_id not in self.datasets:
            raise ValueError(f"Dataset not found: {dataset_id}")
        
        test_cases = self.test_cases.get(dataset_id, [])
        
        # Calculate statistics
        difficulty_levels = {}
        categories = {}
        
        for tc in test_cases:
            difficulty = tc.difficulty_level or "unknown"
            difficulty_levels[difficulty] = difficulty_levels.get(difficulty, 0) + 1
            
            category = tc.category or "uncategorized"
            categories[category] = categories.get(category, 0) + 1
        
        return {
            "dataset_id": dataset_id,
            "total_test_cases": len(test_cases),
            "difficulty_distribution": difficulty_levels,
            "category_distribution": categories,
            "created_at": self.datasets[dataset_id].created_at,
            "updated_at": self.datasets[dataset_id].updated_at,
        }

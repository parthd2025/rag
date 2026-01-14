"""
Dataset Utilities and Helpers
=============================

Utility functions for dataset operations:
- Data validation
- Format conversion
- Test case generation
- CSV/JSON parsing
"""

import csv
import json
from io import StringIO
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

from .dataset_service import TestCase

logger = logging.getLogger(__name__)


class DatasetUtils:
    """Utility functions for dataset operations."""
    
    @staticmethod
    def validate_test_case(test_case: Dict[str, Any]) -> bool:
        """
        Validate test case has required fields.
        
        Required fields:
        - question (str)
        - ground_truth_answer (str)
        
        Args:
            test_case: Test case dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["question", "ground_truth_answer"]
        
        for field in required_fields:
            if field not in test_case:
                logger.warning(f"Missing required field: {field}")
                return False
            
            value = test_case[field]
            if not isinstance(value, str) or not value.strip():
                logger.warning(f"Field '{field}' must be non-empty string")
                return False
        
        return True
    
    @staticmethod
    def csv_to_test_cases(csv_content: str) -> List[Dict[str, Any]]:
        """
        Convert CSV content to test case list.
        
        Expected CSV columns:
        - question (required)
        - ground_truth_answer (required)
        - context (optional)
        - expected_sources (optional, comma-separated)
        - difficulty_level (optional)
        - category (optional)
        
        Args:
            csv_content: CSV content as string
            
        Returns:
            List of test case dictionaries
        """
        test_cases = []
        
        try:
            reader = csv.DictReader(StringIO(csv_content))
            
            if not reader.fieldnames:
                logger.error("CSV file has no headers")
                return []
            
            required_fields = {"question", "ground_truth_answer"}
            available_fields = set(reader.fieldnames or [])
            
            if not required_fields.issubset(available_fields):
                logger.error(f"CSV missing required columns: {required_fields - available_fields}")
                return []
            
            for idx, row in enumerate(reader, start=2):  # Start from line 2 (after header)
                # Parse expected_sources if present
                expected_sources = None
                if "expected_sources" in row and row["expected_sources"]:
                    expected_sources = [s.strip() for s in row["expected_sources"].split(",")]
                
                test_case = {
                    "question": row["question"],
                    "ground_truth_answer": row["ground_truth_answer"],
                    "context": row.get("context"),
                    "expected_sources": expected_sources,
                    "difficulty_level": row.get("difficulty_level", "medium"),
                    "category": row.get("category"),
                }
                
                if DatasetUtils.validate_test_case(test_case):
                    test_cases.append(test_case)
                else:
                    logger.warning(f"Skipping invalid test case at line {idx}")
        
        except Exception as e:
            logger.error(f"Error parsing CSV: {e}")
            return []
        
        return test_cases
    
    @staticmethod
    def json_to_test_cases(json_content: str) -> List[Dict[str, Any]]:
        """
        Convert JSON content to test case list.
        
        Expected JSON format:
        - Array of test case objects
        - OR object with 'test_cases' key containing array
        
        Args:
            json_content: JSON content as string
            
        Returns:
            List of test case dictionaries
        """
        test_cases = []
        
        try:
            data = json.loads(json_content)
            
            # Handle both array and object with test_cases key
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict) and "test_cases" in data:
                items = data["test_cases"]
            else:
                logger.error("JSON must be array or object with 'test_cases' key")
                return []
            
            if not isinstance(items, list):
                logger.error("test_cases must be an array")
                return []
            
            for idx, item in enumerate(items, start=1):
                if DatasetUtils.validate_test_case(item):
                    test_cases.append(item)
                else:
                    logger.warning(f"Skipping invalid test case at index {idx-1}")
        
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"Error processing JSON: {e}")
            return []
        
        return test_cases
    
    @staticmethod
    def test_cases_to_csv(test_cases: List[TestCase]) -> str:
        """
        Convert test cases to CSV format.
        
        Args:
            test_cases: List of TestCase objects
            
        Returns:
            CSV content as string
        """
        if not test_cases:
            return ""
        
        output = StringIO()
        
        # Define headers
        headers = [
            "id",
            "question",
            "ground_truth_answer",
            "context",
            "expected_sources",
            "difficulty_level",
            "category",
            "created_at",
        ]
        
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        
        for tc in test_cases:
            row = {
                "id": tc.id,
                "question": tc.question,
                "ground_truth_answer": tc.ground_truth_answer,
                "context": tc.context or "",
                "expected_sources": ",".join(tc.expected_sources) if tc.expected_sources else "",
                "difficulty_level": tc.difficulty_level or "",
                "category": tc.category or "",
                "created_at": tc.created_at,
            }
            writer.writerow(row)
        
        return output.getvalue()
    
    @staticmethod
    def test_cases_to_json(test_cases: List[TestCase]) -> str:
        """
        Convert test cases to JSON format.
        
        Args:
            test_cases: List of TestCase objects
            
        Returns:
            JSON content as string
        """
        data = {
            "test_cases": [tc.to_dict() for tc in test_cases],
            "count": len(test_cases),
        }
        return json.dumps(data, indent=2)
    
    @staticmethod
    def generate_test_case_template() -> Dict[str, Any]:
        """
        Generate a template for a test case.
        
        Returns:
            Template dictionary
        """
        return {
            "question": "What is the main topic?",
            "ground_truth_answer": "The main topic is...",
            "context": "Optional context if available",
            "expected_sources": ["doc1.pdf", "doc2.pdf"],
            "difficulty_level": "medium",  # easy, medium, hard
            "category": "general",
            "metadata": {
                "source": "user",
                "verified": False,
            }
        }
    
    @staticmethod
    def generate_sample_dataset(count: int = 5) -> List[Dict[str, Any]]:
        """
        Generate sample test cases for demonstration.
        
        Args:
            count: Number of sample test cases to generate
            
        Returns:
            List of sample test case dictionaries
        """
        samples = [
            {
                "question": "What is the document about?",
                "ground_truth_answer": "This document discusses various topics.",
                "difficulty_level": "easy",
                "category": "general",
            },
            {
                "question": "What are the key points mentioned?",
                "ground_truth_answer": "The key points include important information.",
                "difficulty_level": "medium",
                "category": "summary",
            },
            {
                "question": "How does this relate to other concepts?",
                "ground_truth_answer": "This relates to other concepts through...",
                "difficulty_level": "hard",
                "category": "analysis",
            },
            {
                "question": "What examples are provided?",
                "ground_truth_answer": "Several examples are provided including...",
                "difficulty_level": "medium",
                "category": "examples",
            },
            {
                "question": "What are the main conclusions?",
                "ground_truth_answer": "The main conclusions are...",
                "difficulty_level": "hard",
                "category": "conclusions",
            },
        ]
        
        return samples[:count]
    
    @staticmethod
    def calculate_statistics(test_cases: List[TestCase]) -> Dict[str, Any]:
        """
        Calculate statistics for test cases.
        
        Args:
            test_cases: List of TestCase objects
            
        Returns:
            Statistics dictionary
        """
        if not test_cases:
            return {
                "total_count": 0,
                "difficulty_distribution": {},
                "category_distribution": {},
                "avg_question_length": 0,
                "avg_answer_length": 0,
            }
        
        # Count by difficulty and category
        difficulty_count = {}
        category_count = {}
        total_q_len = 0
        total_a_len = 0
        
        for tc in test_cases:
            # Difficulty
            difficulty = tc.difficulty_level or "unknown"
            difficulty_count[difficulty] = difficulty_count.get(difficulty, 0) + 1
            
            # Category
            category = tc.category or "uncategorized"
            category_count[category] = category_count.get(category, 0) + 1
            
            # Lengths
            total_q_len += len(tc.question)
            total_a_len += len(tc.ground_truth_answer)
        
        return {
            "total_count": len(test_cases),
            "difficulty_distribution": difficulty_count,
            "category_distribution": category_count,
            "avg_question_length": round(total_q_len / len(test_cases), 2),
            "avg_answer_length": round(total_a_len / len(test_cases), 2),
        }
    
    @staticmethod
    def validate_dataset_structure(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate dataset structure.
        
        Args:
            data: Dataset data to validate
            
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check for test_cases
        if "test_cases" not in data:
            errors.append("Missing 'test_cases' key")
        elif not isinstance(data["test_cases"], list):
            errors.append("'test_cases' must be a list")
        else:
            # Validate each test case
            for idx, tc in enumerate(data["test_cases"]):
                if not isinstance(tc, dict):
                    errors.append(f"Test case {idx} must be a dictionary")
                    continue
                
                if "question" not in tc:
                    errors.append(f"Test case {idx} missing 'question'")
                if "ground_truth_answer" not in tc:
                    errors.append(f"Test case {idx} missing 'ground_truth_answer'")
        
        is_valid = len(errors) == 0
        return is_valid, errors

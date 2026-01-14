"""
Dataset Evaluation Framework
=============================

Evaluates RAG system outputs against ground truth datasets.
Tracks metrics like accuracy, precision, recall, and F1 scores.
Integrates with OPIK for tracing and analysis.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging

from .dataset_service import DatasetService, TestCase, DatasetEvaluationResult
from ..logger_config import logger

try:
    from opik import track
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    def track(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class EvaluationMetric(str, Enum):
    """Evaluation metrics."""
    EXACT_MATCH = "exact_match"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    ROUGE = "rouge"
    BLEU = "bleu"


@dataclass
class TestCaseEvaluation:
    """Evaluation result for a single test case."""
    test_case_id: str
    passed: bool
    score: float  # 0.0 to 1.0
    predicted_answer: str
    ground_truth_answer: str
    reasoning: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class DatasetEvaluator:
    """
    Evaluates RAG system outputs against datasets.
    
    Provides:
    - Test case evaluation
    - Batch evaluation
    - Metric calculation
    - Result reporting
    - OPIK integration
    """
    
    def __init__(self, dataset_service: DatasetService):
        """
        Initialize evaluator.
        
        Args:
            dataset_service: Reference to dataset service
        """
        self.dataset_service = dataset_service
        self.evaluation_results: Dict[str, DatasetEvaluationResult] = {}
    
    def evaluate_answer(
        self,
        predicted_answer: str,
        ground_truth_answer: str,
        metrics: Optional[List[EvaluationMetric]] = None,
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate a single answer against ground truth.
        
        Args:
            predicted_answer: Answer from RAG system
            ground_truth_answer: Expected/ground truth answer
            metrics: Metrics to calculate
            
        Returns:
            (overall_score, detailed_metrics)
        """
        if metrics is None:
            metrics = [EvaluationMetric.EXACT_MATCH, EvaluationMetric.SEMANTIC_SIMILARITY]
        
        detailed_metrics = {}
        scores = []
        
        # Exact match
        if EvaluationMetric.EXACT_MATCH in metrics:
            exact_match = self._calculate_exact_match(predicted_answer, ground_truth_answer)
            detailed_metrics["exact_match"] = exact_match
            scores.append(exact_match)
        
        # Semantic similarity (simple token overlap)
        if EvaluationMetric.SEMANTIC_SIMILARITY in metrics:
            semantic_sim = self._calculate_semantic_similarity(predicted_answer, ground_truth_answer)
            detailed_metrics["semantic_similarity"] = semantic_sim
            scores.append(semantic_sim)
        
        # Calculate overall score
        overall_score = sum(scores) / len(scores) if scores else 0.0
        detailed_metrics["overall_score"] = overall_score
        
        return overall_score, detailed_metrics
    
    def _calculate_exact_match(
        self,
        predicted: str,
        ground_truth: str,
        case_sensitive: bool = False,
    ) -> float:
        """Calculate exact match score."""
        p = predicted if case_sensitive else predicted.lower()
        g = ground_truth if case_sensitive else ground_truth.lower()
        return 1.0 if p.strip() == g.strip() else 0.0
    
    def _calculate_semantic_similarity(
        self,
        predicted: str,
        ground_truth: str,
        threshold: float = 0.7,
    ) -> float:
        """
        Calculate semantic similarity using token overlap (Jaccard similarity).
        
        For more advanced similarity, integrate with embedding models.
        """
        def tokenize(text):
            return set(text.lower().split())
        
        pred_tokens = tokenize(predicted)
        truth_tokens = tokenize(ground_truth)
        
        if not pred_tokens and not truth_tokens:
            return 1.0
        
        if not pred_tokens or not truth_tokens:
            return 0.0
        
        intersection = len(pred_tokens & truth_tokens)
        union = len(pred_tokens | truth_tokens)
        
        return intersection / union if union > 0 else 0.0
    
    @track(name="evaluate_test_case")
    def evaluate_test_case(
        self,
        test_case: TestCase,
        predicted_answer: str,
        metrics: Optional[List[EvaluationMetric]] = None,
    ) -> TestCaseEvaluation:
        """
        Evaluate a single test case.
        
        Args:
            test_case: Test case to evaluate
            predicted_answer: Predicted answer from RAG
            metrics: Metrics to calculate
            
        Returns:
            Evaluation result
        """
        score, detailed_metrics = self.evaluate_answer(
            predicted_answer=predicted_answer,
            ground_truth_answer=test_case.ground_truth_answer,
            metrics=metrics,
        )
        
        passed = score >= 0.5  # Pass if score >= 0.5
        
        return TestCaseEvaluation(
            test_case_id=test_case.id,
            passed=passed,
            score=score,
            predicted_answer=predicted_answer,
            ground_truth_answer=test_case.ground_truth_answer,
            metrics=detailed_metrics,
            reasoning=f"Score: {score:.2f} - {'PASS' if passed else 'FAIL'}",
        )
    
    @track(name="evaluate_dataset")
    def evaluate_dataset(
        self,
        dataset_id: str,
        rag_engine: Any,  # RAGEngine instance
        metrics: Optional[List[EvaluationMetric]] = None,
    ) -> DatasetEvaluationResult:
        """
        Evaluate entire dataset against RAG system.
        
        Args:
            dataset_id: Dataset ID to evaluate
            rag_engine: RAGEngine instance to use for evaluation
            metrics: Metrics to calculate
            
        Returns:
            Dataset evaluation result
        """
        dataset = self.dataset_service.get_dataset(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset not found: {dataset_id}")
        
        test_cases = self.dataset_service.get_test_cases(dataset_id)
        
        evaluation_details = []
        passed_count = 0
        failed_count = 0
        
        logger.info(f"Starting evaluation of dataset {dataset_id} with {len(test_cases)} test cases")
        
        for idx, test_case in enumerate(test_cases, 1):
            try:
                # Get prediction from RAG engine
                result = rag_engine.rag_query_complete(
                    query=test_case.question,
                    top_k=5,
                )
                predicted_answer = result.get("answer", "")
                
                # Evaluate test case
                tc_eval = self.evaluate_test_case(
                    test_case=test_case,
                    predicted_answer=predicted_answer,
                    metrics=metrics,
                )
                
                evaluation_details.append(asdict(tc_eval))
                
                if tc_eval.passed:
                    passed_count += 1
                else:
                    failed_count += 1
                
                logger.debug(f"Evaluated test case {idx}/{len(test_cases)}: {tc_eval.passed}")
                
            except Exception as e:
                logger.error(f"Error evaluating test case {test_case.id}: {e}")
                failed_count += 1
                evaluation_details.append({
                    "test_case_id": test_case.id,
                    "passed": False,
                    "score": 0.0,
                    "predicted_answer": "",
                    "ground_truth_answer": test_case.ground_truth_answer,
                    "reasoning": f"Error during evaluation: {str(e)}",
                })
        
        # Calculate overall metrics
        total = len(test_cases)
        accuracy = (passed_count / total * 100) if total > 0 else 0.0
        
        result = DatasetEvaluationResult(
            dataset_id=dataset_id,
            test_case_count=total,
            passed=passed_count,
            failed=failed_count,
            accuracy=accuracy,
            metrics={
                "accuracy_percent": accuracy,
                "pass_rate": (passed_count / total) if total > 0 else 0.0,
                "fail_rate": (failed_count / total) if total > 0 else 0.0,
            },
            details=evaluation_details,
        )
        
        # Store result
        self.evaluation_results[dataset_id] = result
        
        logger.info(
            f"Dataset evaluation complete: {passed_count}/{total} passed "
            f"({accuracy:.1f}% accuracy)"
        )
        
        return result
    
    def get_evaluation_summary(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of latest evaluation for a dataset."""
        result = self.evaluation_results.get(dataset_id)
        if not result:
            return None
        
        return {
            "dataset_id": dataset_id,
            "total_test_cases": result.test_case_count,
            "passed": result.passed,
            "failed": result.failed,
            "accuracy_percent": result.accuracy,
            "timestamp": result.evaluation_timestamp,
            "metrics": result.metrics,
        }
    
    def compare_evaluations(
        self,
        dataset_id_1: str,
        dataset_id_2: str,
    ) -> Dict[str, Any]:
        """
        Compare evaluation results between two datasets.
        
        Args:
            dataset_id_1: First dataset ID
            dataset_id_2: Second dataset ID
            
        Returns:
            Comparison results
        """
        result1 = self.evaluation_results.get(dataset_id_1)
        result2 = self.evaluation_results.get(dataset_id_2)
        
        if not result1 or not result2:
            raise ValueError("One or both evaluation results not found")
        
        return {
            "dataset_1": {
                "id": dataset_id_1,
                "accuracy": result1.accuracy,
                "passed": result1.passed,
                "total": result1.test_case_count,
            },
            "dataset_2": {
                "id": dataset_id_2,
                "accuracy": result2.accuracy,
                "passed": result2.passed,
                "total": result2.test_case_count,
            },
            "difference": {
                "accuracy_delta": result2.accuracy - result1.accuracy,
                "passed_delta": result2.passed - result1.passed,
            },
        }
    
    def export_results(
        self,
        dataset_id: str,
        format: str = "json",
    ) -> Dict[str, Any]:
        """
        Export evaluation results.
        
        Args:
            dataset_id: Dataset ID
            format: Export format
            
        Returns:
            Exported results
        """
        result = self.evaluation_results.get(dataset_id)
        if not result:
            raise ValueError(f"No evaluation results found for dataset {dataset_id}")
        
        if format == "json":
            return result.to_dict()
        else:
            raise ValueError(f"Unsupported export format: {format}")

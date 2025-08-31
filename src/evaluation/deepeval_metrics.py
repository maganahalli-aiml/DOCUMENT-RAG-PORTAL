"""
DeepEval Metrics Implementation
Comprehensive evaluation framework for RAG systems
"""

import asyncio
import json
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import pandas as pd

# DeepEval imports
from deepeval import evaluate
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    HallucinationMetric,
    ToxicityMetric,
    BiasMetric
)
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset

# LangChain imports for our RAG system
from langchain.schema import Document


class RAGEvaluationMetrics:
    """Comprehensive evaluation metrics for RAG systems using DeepEval"""
    
    def __init__(self, model_name: str = "gpt-4"):
        """Initialize evaluation metrics"""
        self.model_name = model_name
        
        # Initialize metrics
        self.answer_relevancy = AnswerRelevancyMetric(
            threshold=0.7,
            model=model_name,
            include_reason=True
        )
        
        self.faithfulness = FaithfulnessMetric(
            threshold=0.7,
            model=model_name,
            include_reason=True
        )
        
        self.contextual_precision = ContextualPrecisionMetric(
            threshold=0.7,
            model=model_name,
            include_reason=True
        )
        
        self.contextual_recall = ContextualRecallMetric(
            threshold=0.7,
            model=model_name,
            include_reason=True
        )
        
        self.hallucination = HallucinationMetric(
            threshold=0.3,  # Lower threshold means less tolerance for hallucination
            model=model_name,
            include_reason=True
        )
        
        self.toxicity = ToxicityMetric(
            threshold=0.5,
            model=model_name,
            include_reason=True
        )
        
        self.bias = BiasMetric(
            threshold=0.5,
            model=model_name,
            include_reason=True
        )
    
    def create_test_case(
        self,
        input_query: str,
        actual_output: str,
        expected_output: str = None,
        retrieval_context: List[str] = None
    ) -> LLMTestCase:
        """Create a test case for evaluation"""
        return LLMTestCase(
            input=input_query,
            actual_output=actual_output,
            expected_output=expected_output,
            retrieval_context=retrieval_context
        )
    
    async def evaluate_single_response(
        self,
        query: str,
        response: str,
        expected_response: str = None,
        context_documents: List[Document] = None
    ) -> Dict[str, Any]:
        """Evaluate a single RAG response"""
        
        # Convert context documents to strings
        retrieval_context = []
        if context_documents:
            retrieval_context = [doc.page_content for doc in context_documents]
        
        # Create test case
        test_case = self.create_test_case(
            input_query=query,
            actual_output=response,
            expected_output=expected_response,
            retrieval_context=retrieval_context
        )
        
        # Evaluate with all metrics
        results = {}
        
        try:
            # Answer Relevancy
            await self.answer_relevancy.a_measure(test_case)
            results['answer_relevancy'] = {
                'score': self.answer_relevancy.score,
                'reason': self.answer_relevancy.reason,
                'success': self.answer_relevancy.success
            }
        except Exception as e:
            results['answer_relevancy'] = {'error': str(e)}
        
        try:
            # Faithfulness (requires context)
            if retrieval_context:
                await self.faithfulness.a_measure(test_case)
                results['faithfulness'] = {
                    'score': self.faithfulness.score,
                    'reason': self.faithfulness.reason,
                    'success': self.faithfulness.success
                }
        except Exception as e:
            results['faithfulness'] = {'error': str(e)}
        
        try:
            # Contextual Precision (requires expected output and context)
            if expected_response and retrieval_context:
                await self.contextual_precision.a_measure(test_case)
                results['contextual_precision'] = {
                    'score': self.contextual_precision.score,
                    'reason': self.contextual_precision.reason,
                    'success': self.contextual_precision.success
                }
        except Exception as e:
            results['contextual_precision'] = {'error': str(e)}
        
        try:
            # Contextual Recall (requires expected output and context)
            if expected_response and retrieval_context:
                await self.contextual_recall.a_measure(test_case)
                results['contextual_recall'] = {
                    'score': self.contextual_recall.score,
                    'reason': self.contextual_recall.reason,
                    'success': self.contextual_recall.success
                }
        except Exception as e:
            results['contextual_recall'] = {'error': str(e)}
        
        try:
            # Hallucination
            await self.hallucination.a_measure(test_case)
            results['hallucination'] = {
                'score': self.hallucination.score,
                'reason': self.hallucination.reason,
                'success': self.hallucination.success
            }
        except Exception as e:
            results['hallucination'] = {'error': str(e)}
        
        try:
            # Toxicity
            await self.toxicity.a_measure(test_case)
            results['toxicity'] = {
                'score': self.toxicity.score,
                'reason': self.toxicity.reason,
                'success': self.toxicity.success
            }
        except Exception as e:
            results['toxicity'] = {'error': str(e)}
        
        try:
            # Bias
            await self.bias.a_measure(test_case)
            results['bias'] = {
                'score': self.bias.score,
                'reason': self.bias.reason,
                'success': self.bias.success
            }
        except Exception as e:
            results['bias'] = {'error': str(e)}
        
        return results
    
    async def evaluate_dataset(
        self,
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate a dataset of test cases"""
        
        # Convert test cases to LLMTestCase objects
        llm_test_cases = []
        for case in test_cases:
            test_case = self.create_test_case(
                input_query=case['query'],
                actual_output=case['response'],
                expected_output=case.get('expected_response'),
                retrieval_context=case.get('context', [])
            )
            llm_test_cases.append(test_case)
        
        # Create evaluation dataset
        dataset = EvaluationDataset(test_cases=llm_test_cases)
        
        # Run evaluation
        evaluation_results = evaluate(
            dataset=dataset,
            metrics=[
                self.answer_relevancy,
                self.faithfulness,
                self.contextual_precision,
                self.contextual_recall,
                self.hallucination,
                self.toxicity,
                self.bias
            ]
        )
        
        return self._process_dataset_results(evaluation_results)
    
    def _process_dataset_results(self, results) -> Dict[str, Any]:
        """Process and aggregate dataset evaluation results"""
        processed_results = {
            'overall_scores': {},
            'individual_results': [],
            'summary_statistics': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Extract individual test case results
        for test_case in results.test_cases:
            case_results = {
                'input': test_case.input,
                'actual_output': test_case.actual_output,
                'metrics': {}
            }
            
            # Extract metric scores
            for metric_name, metric_result in test_case.metrics_metadata.items():
                case_results['metrics'][metric_name] = {
                    'score': metric_result.get('score'),
                    'success': metric_result.get('success'),
                    'reason': metric_result.get('reason')
                }
            
            processed_results['individual_results'].append(case_results)
        
        # Calculate overall scores
        metrics_names = ['answer_relevancy', 'faithfulness', 'contextual_precision', 
                        'contextual_recall', 'hallucination', 'toxicity', 'bias']
        
        for metric_name in metrics_names:
            scores = []
            successes = []
            
            for case in processed_results['individual_results']:
                if metric_name in case['metrics'] and case['metrics'][metric_name]['score'] is not None:
                    scores.append(case['metrics'][metric_name]['score'])
                    successes.append(case['metrics'][metric_name]['success'])
            
            if scores:
                processed_results['overall_scores'][metric_name] = {
                    'average_score': sum(scores) / len(scores),
                    'min_score': min(scores),
                    'max_score': max(scores),
                    'success_rate': sum(successes) / len(successes) if successes else 0,
                    'total_evaluations': len(scores)
                }
        
        # Calculate summary statistics
        processed_results['summary_statistics'] = {
            'total_test_cases': len(processed_results['individual_results']),
            'average_overall_score': self._calculate_overall_average(processed_results['overall_scores']),
            'metrics_evaluated': len(processed_results['overall_scores']),
            'evaluation_timestamp': datetime.now().isoformat()
        }
        
        return processed_results
    
    def _calculate_overall_average(self, overall_scores: Dict[str, Dict]) -> float:
        """Calculate overall average score across all metrics"""
        scores = []
        for metric_scores in overall_scores.values():
            if 'average_score' in metric_scores:
                scores.append(metric_scores['average_score'])
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def export_results_to_csv(self, results: Dict[str, Any], output_path: str):
        """Export evaluation results to CSV"""
        # Create DataFrame for individual results
        individual_data = []
        
        for case in results['individual_results']:
            row = {
                'input': case['input'],
                'actual_output': case['actual_output']
            }
            
            # Add metric scores
            for metric_name, metric_data in case['metrics'].items():
                row[f"{metric_name}_score"] = metric_data['score']
                row[f"{metric_name}_success"] = metric_data['success']
            
            individual_data.append(row)
        
        df = pd.DataFrame(individual_data)
        df.to_csv(output_path, index=False)
        
        # Also save summary
        summary_path = output_path.replace('.csv', '_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(results['overall_scores'], f, indent=2)
    
    def create_evaluation_report(self, results: Dict[str, Any]) -> str:
        """Create a comprehensive evaluation report"""
        report = []
        report.append("# RAG System Evaluation Report")
        report.append(f"Generated on: {results['summary_statistics']['evaluation_timestamp']}")
        report.append("")
        
        # Overall Summary
        report.append("## Overall Summary")
        report.append(f"- Total test cases: {results['summary_statistics']['total_test_cases']}")
        report.append(f"- Average overall score: {results['summary_statistics']['average_overall_score']:.3f}")
        report.append(f"- Metrics evaluated: {results['summary_statistics']['metrics_evaluated']}")
        report.append("")
        
        # Metric-wise Results
        report.append("## Metric-wise Results")
        for metric_name, scores in results['overall_scores'].items():
            report.append(f"### {metric_name.replace('_', ' ').title()}")
            report.append(f"- Average Score: {scores['average_score']:.3f}")
            report.append(f"- Success Rate: {scores['success_rate']:.1%}")
            report.append(f"- Score Range: {scores['min_score']:.3f} - {scores['max_score']:.3f}")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        for metric_name, scores in results['overall_scores'].items():
            if scores['average_score'] < 0.7:
                report.append(f"- **{metric_name.replace('_', ' ').title()}**: Score below threshold ({scores['average_score']:.3f}). Consider reviewing and improving this aspect.")
            elif scores['average_score'] > 0.9:
                report.append(f"- **{metric_name.replace('_', ' ').title()}**: Excellent performance ({scores['average_score']:.3f}).")
        
        return "\n".join(report)


class BenchmarkDatasets:
    """Predefined benchmark datasets for evaluation"""
    
    @staticmethod
    def get_general_qa_dataset() -> List[Dict[str, Any]]:
        """General Q&A benchmark dataset"""
        return [
            {
                "query": "What is artificial intelligence?",
                "response": "Artificial intelligence is the simulation of human intelligence in machines.",
                "expected_response": "AI is a field of computer science focused on creating intelligent machines.",
                "context": ["AI involves machine learning, neural networks, and cognitive computing."]
            },
            {
                "query": "How does machine learning work?",
                "response": "Machine learning uses algorithms to learn from data patterns.",
                "expected_response": "ML algorithms improve their performance on a task through experience.",
                "context": ["Machine learning is a subset of AI that uses statistical techniques."]
            }
            # Add more test cases as needed
        ]
    
    @staticmethod
    def get_document_qa_dataset() -> List[Dict[str, Any]]:
        """Document-specific Q&A benchmark dataset"""
        return [
            {
                "query": "What are the key findings in the research paper?",
                "response": "The paper concludes that the proposed method improves accuracy by 15%.",
                "expected_response": "The main findings show significant improvement in model performance.",
                "context": ["The study evaluated performance on multiple datasets showing consistent improvements."]
            },
            {
                "query": "What is the methodology used in the study?",
                "response": "The researchers used a controlled experimental design with cross-validation.",
                "expected_response": "The methodology involves statistical analysis and comparative evaluation.",
                "context": ["The experimental setup included multiple baseline comparisons and ablation studies."]
            }
            # Add more test cases as needed
        ]


# Example usage
if __name__ == "__main__":
    # Initialize evaluator
    evaluator = RAGEvaluationMetrics()
    
    # Example single evaluation
    async def test_single_evaluation():
        results = await evaluator.evaluate_single_response(
            query="What is machine learning?",
            response="Machine learning is a subset of AI that enables computers to learn from data.",
            expected_response="ML is an AI technique for pattern recognition in data.",
            context_documents=None
        )
        print("Single evaluation results:", results)
    
    # Example dataset evaluation
    async def test_dataset_evaluation():
        test_dataset = BenchmarkDatasets.get_general_qa_dataset()
        results = await evaluator.evaluate_dataset(test_dataset)
        
        # Generate report
        report = evaluator.create_evaluation_report(results)
        print("Evaluation Report:")
        print(report)
    
    # Run examples
    asyncio.run(test_single_evaluation())
    # asyncio.run(test_dataset_evaluation())

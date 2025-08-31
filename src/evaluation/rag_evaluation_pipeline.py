"""
RAG System Integration for Evaluation
Connects the RAG pipeline with DeepEval metrics
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from src.evaluation.deepeval_metrics import RAGEvaluationMetrics
except ImportError:
    from src.evaluation.mock_deepeval_metrics import RAGEvaluationMetrics
from langchain.schema import Document

# Import our RAG components (assuming they exist)
try:
    from src.conversational_rag import ConversationalRAG
    from src.document_ingestion.document_processors import DocumentProcessorFactory
except ImportError as e:
    logging.warning(f"Could not import RAG components: {e}")


class RAGEvaluationPipeline:
    """Complete evaluation pipeline for RAG system"""
    
    def __init__(self, rag_system=None, model_name: str = "gpt-4"):
        """Initialize evaluation pipeline"""
        self.rag_system = rag_system
        self.evaluator = RAGEvaluationMetrics(model_name=model_name)
        self.logger = logging.getLogger(__name__)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def evaluate_document_processing(
        self, 
        document_path: str,
        test_queries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate document processing and retrieval"""
        
        results = {
            'document_path': document_path,
            'processing_results': {},
            'query_evaluations': [],
            'overall_performance': {}
        }
        
        try:
            # Process document if RAG system available
            if self.rag_system:
                # Process the document
                processing_start = datetime.now()
                success = await self._process_document(document_path)
                processing_time = (datetime.now() - processing_start).total_seconds()
                
                results['processing_results'] = {
                    'success': success,
                    'processing_time_seconds': processing_time,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Evaluate queries
                for query_data in test_queries:
                    query_result = await self._evaluate_single_query(query_data)
                    results['query_evaluations'].append(query_result)
                
                # Calculate overall performance
                results['overall_performance'] = self._calculate_overall_performance(
                    results['query_evaluations']
                )
            
            else:
                self.logger.warning("No RAG system provided, skipping document processing evaluation")
                
        except Exception as e:
            self.logger.error(f"Error in document processing evaluation: {e}")
            results['error'] = str(e)
        
        return results
    
    async def _process_document(self, document_path: str) -> bool:
        """Process document through RAG system"""
        try:
            # This would integrate with your actual RAG system
            # For now, we'll simulate the process
            await asyncio.sleep(1)  # Simulate processing time
            return True
        except Exception as e:
            self.logger.error(f"Document processing failed: {e}")
            return False
    
    async def _evaluate_single_query(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single query against the RAG system"""
        
        query = query_data['query']
        expected_response = query_data.get('expected_response')
        
        try:
            # Get response from RAG system
            if self.rag_system:
                response_data = await self._get_rag_response(query)
                response = response_data.get('response', '')
                context_docs = response_data.get('context_documents', [])
            else:
                # Mock response for testing
                response = f"Mock response for: {query}"
                context_docs = [Document(page_content="Mock context document")]
            
            # Evaluate with DeepEval
            evaluation_results = await self.evaluator.evaluate_single_response(
                query=query,
                response=response,
                expected_response=expected_response,
                context_documents=context_docs
            )
            
            return {
                'query': query,
                'response': response,
                'expected_response': expected_response,
                'context_count': len(context_docs),
                'evaluation_metrics': evaluation_results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Query evaluation failed for '{query}': {e}")
            return {
                'query': query,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _get_rag_response(self, query: str) -> Dict[str, Any]:
        """Get response from RAG system"""
        try:
            # This would integrate with your actual RAG system
            # For now, we'll simulate the response
            return {
                'response': f"Simulated RAG response for: {query}",
                'context_documents': [
                    Document(page_content="Simulated context document 1"),
                    Document(page_content="Simulated context document 2")
                ]
            }
        except Exception as e:
            self.logger.error(f"RAG response generation failed: {e}")
            return {'response': '', 'context_documents': []}
    
    def _calculate_overall_performance(self, query_evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall performance metrics"""
        
        if not query_evaluations:
            return {'error': 'No query evaluations available'}
        
        # Aggregate metric scores
        metric_aggregates = {}
        successful_evaluations = 0
        
        for evaluation in query_evaluations:
            if 'evaluation_metrics' in evaluation:
                successful_evaluations += 1
                metrics = evaluation['evaluation_metrics']
                
                for metric_name, metric_data in metrics.items():
                    if isinstance(metric_data, dict) and 'score' in metric_data:
                        if metric_name not in metric_aggregates:
                            metric_aggregates[metric_name] = []
                        metric_aggregates[metric_name].append(metric_data['score'])
        
        # Calculate averages
        average_scores = {}
        for metric_name, scores in metric_aggregates.items():
            valid_scores = [s for s in scores if s is not None]
            if valid_scores:
                average_scores[metric_name] = {
                    'average': sum(valid_scores) / len(valid_scores),
                    'min': min(valid_scores),
                    'max': max(valid_scores),
                    'count': len(valid_scores)
                }
        
        return {
            'total_queries': len(query_evaluations),
            'successful_evaluations': successful_evaluations,
            'success_rate': successful_evaluations / len(query_evaluations),
            'average_metric_scores': average_scores,
            'overall_score': self._calculate_composite_score(average_scores)
        }
    
    def _calculate_composite_score(self, average_scores: Dict[str, Dict]) -> float:
        """Calculate composite performance score"""
        if not average_scores:
            return 0.0
        
        # Weight different metrics
        metric_weights = {
            'answer_relevancy': 0.25,
            'faithfulness': 0.25,
            'contextual_precision': 0.20,
            'contextual_recall': 0.20,
            'hallucination': 0.10  # Inverted - lower is better
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for metric_name, weight in metric_weights.items():
            if metric_name in average_scores:
                score = average_scores[metric_name]['average']
                
                # Invert hallucination score (lower is better)
                if metric_name == 'hallucination':
                    score = 1.0 - score
                
                weighted_sum += score * weight
                total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    async def run_comprehensive_evaluation(
        self,
        test_cases: List[Dict[str, Any]],
        output_dir: str = "evaluation_results"
    ) -> Dict[str, Any]:
        """Run comprehensive evaluation with multiple test cases"""
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        evaluation_results = {
            'evaluation_id': f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'start_time': datetime.now().isoformat(),
            'test_cases': [],
            'summary': {}
        }
        
        self.logger.info(f"Starting comprehensive evaluation with {len(test_cases)} test cases")
        
        # Process each test case
        for i, test_case in enumerate(test_cases):
            self.logger.info(f"Processing test case {i+1}/{len(test_cases)}")
            
            try:
                case_result = await self.evaluator.evaluate_single_response(
                    query=test_case['query'],
                    response=test_case.get('response', ''),
                    expected_response=test_case.get('expected_response'),
                    context_documents=test_case.get('context_documents', [])
                )
                
                evaluation_results['test_cases'].append({
                    'test_case_id': i + 1,
                    'query': test_case['query'],
                    'results': case_result
                })
                
            except Exception as e:
                self.logger.error(f"Test case {i+1} failed: {e}")
                evaluation_results['test_cases'].append({
                    'test_case_id': i + 1,
                    'query': test_case.get('query', 'Unknown'),
                    'error': str(e)
                })
        
        # Calculate summary
        evaluation_results['summary'] = self._generate_evaluation_summary(
            evaluation_results['test_cases']
        )
        evaluation_results['end_time'] = datetime.now().isoformat()
        
        # Save results
        output_file = os.path.join(output_dir, f"{evaluation_results['evaluation_id']}.json")
        import json
        with open(output_file, 'w') as f:
            json.dump(evaluation_results, f, indent=2)
        
        # Generate report
        report = self._generate_evaluation_report(evaluation_results)
        report_file = os.path.join(output_dir, f"{evaluation_results['evaluation_id']}_report.md")
        with open(report_file, 'w') as f:
            f.write(report)
        
        self.logger.info(f"Evaluation completed. Results saved to {output_dir}")
        
        return evaluation_results
    
    def _generate_evaluation_summary(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of evaluation results"""
        
        total_cases = len(test_cases)
        successful_cases = len([case for case in test_cases if 'results' in case])
        failed_cases = total_cases - successful_cases
        
        # Aggregate metric scores
        metric_scores = {}
        for case in test_cases:
            if 'results' in case:
                for metric_name, metric_data in case['results'].items():
                    if isinstance(metric_data, dict) and 'score' in metric_data:
                        if metric_name not in metric_scores:
                            metric_scores[metric_name] = []
                        score = metric_data['score']
                        if score is not None:
                            metric_scores[metric_name].append(score)
        
        # Calculate averages
        average_scores = {}
        for metric_name, scores in metric_scores.items():
            if scores:
                average_scores[metric_name] = {
                    'average': sum(scores) / len(scores),
                    'min': min(scores),
                    'max': max(scores),
                    'std_dev': self._calculate_std_dev(scores)
                }
        
        return {
            'total_test_cases': total_cases,
            'successful_evaluations': successful_cases,
            'failed_evaluations': failed_cases,
            'success_rate': successful_cases / total_cases if total_cases > 0 else 0,
            'metric_averages': average_scores,
            'overall_performance_score': self._calculate_composite_score(average_scores)
        }
    
    def _calculate_std_dev(self, scores: List[float]) -> float:
        """Calculate standard deviation"""
        if len(scores) < 2:
            return 0.0
        
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / (len(scores) - 1)
        return variance ** 0.5
    
    def _generate_evaluation_report(self, evaluation_results: Dict[str, Any]) -> str:
        """Generate markdown evaluation report"""
        
        report = []
        report.append(f"# RAG System Evaluation Report")
        report.append(f"**Evaluation ID:** {evaluation_results['evaluation_id']}")
        report.append(f"**Start Time:** {evaluation_results['start_time']}")
        report.append(f"**End Time:** {evaluation_results['end_time']}")
        report.append("")
        
        summary = evaluation_results['summary']
        
        # Summary section
        report.append("## Summary")
        report.append(f"- **Total Test Cases:** {summary['total_test_cases']}")
        report.append(f"- **Successful Evaluations:** {summary['successful_evaluations']}")
        report.append(f"- **Failed Evaluations:** {summary['failed_evaluations']}")
        report.append(f"- **Success Rate:** {summary['success_rate']:.1%}")
        report.append(f"- **Overall Performance Score:** {summary['overall_performance_score']:.3f}")
        report.append("")
        
        # Metric details
        report.append("## Metric Performance")
        for metric_name, scores in summary['metric_averages'].items():
            report.append(f"### {metric_name.replace('_', ' ').title()}")
            report.append(f"- **Average Score:** {scores['average']:.3f}")
            report.append(f"- **Range:** {scores['min']:.3f} - {scores['max']:.3f}")
            report.append(f"- **Standard Deviation:** {scores['std_dev']:.3f}")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        for metric_name, scores in summary['metric_averages'].items():
            avg_score = scores['average']
            if avg_score < 0.6:
                report.append(f"- **{metric_name.replace('_', ' ').title()}:** Low performance ({avg_score:.3f}). Requires immediate attention.")
            elif avg_score < 0.7:
                report.append(f"- **{metric_name.replace('_', ' ').title()}:** Below threshold ({avg_score:.3f}). Consider improvements.")
            elif avg_score > 0.9:
                report.append(f"- **{metric_name.replace('_', ' ').title()}:** Excellent performance ({avg_score:.3f}).")
        
        report.append("")
        report.append("---")
        report.append("*Report generated by RAG Evaluation Pipeline*")
        
        return "\n".join(report)


# Example usage and test cases
def get_sample_test_cases() -> List[Dict[str, Any]]:
    """Get sample test cases for evaluation"""
    return [
        {
            "query": "What is machine learning?",
            "response": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.",
            "expected_response": "Machine learning is an AI technique that allows systems to automatically learn and improve from data.",
            "context_documents": [
                Document(page_content="Machine learning algorithms build mathematical models based on training data to make predictions or decisions.")
            ]
        },
        {
            "query": "How does deep learning work?",
            "response": "Deep learning uses neural networks with multiple layers to model and understand complex patterns in data.",
            "expected_response": "Deep learning employs multi-layered neural networks to learn hierarchical representations of data.",
            "context_documents": [
                Document(page_content="Deep learning architectures consist of multiple layers of artificial neurons that process information hierarchically.")
            ]
        },
        {
            "query": "What are the applications of AI?",
            "response": "AI has applications in healthcare, finance, autonomous vehicles, natural language processing, and computer vision.",
            "expected_response": "AI is applied across various domains including medical diagnosis, financial analysis, and autonomous systems.",
            "context_documents": [
                Document(page_content="Artificial intelligence finds applications in numerous fields including healthcare diagnostics, financial modeling, and transportation systems.")
            ]
        }
    ]


if __name__ == "__main__":
    # Example usage
    async def run_sample_evaluation():
        pipeline = RAGEvaluationPipeline()
        
        test_cases = get_sample_test_cases()
        results = await pipeline.run_comprehensive_evaluation(test_cases)
        
        print("Evaluation completed!")
        print(f"Overall performance score: {results['summary']['overall_performance_score']:.3f}")
        print(f"Success rate: {results['summary']['success_rate']:.1%}")
    
    # Run sample evaluation
    asyncio.run(run_sample_evaluation())

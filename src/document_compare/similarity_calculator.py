"""
Similarity Calculator for Document Comparison
Provides statistical similarity metrics for document comparison.
"""

import re
from typing import Tuple, Set
from difflib import SequenceMatcher
from collections import Counter
import math


class SimilarityCalculator:
    """
    Calculate similarity metrics between two documents.
    """
    
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
            'his', 'its', 'our', 'their', 'from', 'as', 'not', 'all', 'some', 'any', 'each', 'every'
        }
    
    def preprocess_text(self, text: str) -> str:
        """
        Clean and normalize text for comparison.
        Optimized for large texts.
        """
        # Limit text length for performance - increased to 200k characters
        if len(text) > 200000:  # 200k character limit
            text = text[:200000]
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep word boundaries
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra spaces
        text = text.strip()
        
        return text
    
    def extract_words(self, text: str) -> Set[str]:
        """
        Extract meaningful words from text, excluding stop words.
        Optimized for performance.
        """
        processed_text = self.preprocess_text(text)
        words = processed_text.split()
        
        # Filter out stop words and very short words
        # Use set comprehension for better performance
        meaningful_words = {
            word for word in words 
            if len(word) > 2 and word not in self.stop_words
        }
        
        # Limit word set size to prevent memory issues - increased to 25k words
        if len(meaningful_words) > 25000:
            meaningful_words = set(list(meaningful_words)[:25000])
        
        return meaningful_words
    
    def calculate_jaccard_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate Jaccard similarity coefficient between two texts.
        """
        words1 = self.extract_words(text1)
        words2 = self.extract_words(text2)
        
        if not words1 and not words2:
            return 1.0  # Both empty
        
        if not words1 or not words2:
            return 0.0  # One empty
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def calculate_cosine_similarity(self, words1: Set[str], words2: Set[str]) -> float:
        """
        Calculate cosine similarity between two sets of words.
        Optimized for performance with large word sets.
        """
        if not words1 or not words2:
            return 0.0
        
        # Limit vocabulary size for performance - increased to 15k words
        all_words = words1.union(words2)
        if len(all_words) > 15000:
            # Use most common words from both sets
            all_words = list(all_words)[:15000]
        else:
            all_words = list(all_words)
        
        # Create word vectors more efficiently
        vec1 = [1 if word in words1 else 0 for word in all_words]
        vec2 = [1 if word in words2 else 0 for word in all_words]
        
        # Calculate dot product and norms
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def calculate_sequence_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate sequence similarity using difflib.
        Optimized for large texts by sampling.
        """
        # For large texts, use sampling to improve performance - increased to 50k chars
        max_length = 50000
        if len(text1) > max_length:
            text1 = text1[:max_length]
        if len(text2) > max_length:
            text2 = text2[:max_length]
        
        # Use SequenceMatcher for character-level similarity
        matcher = SequenceMatcher(None, text1, text2)
        return matcher.ratio()
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate overall similarity score using multiple metrics.
        Returns a value between 0.0 and 1.0.
        """
        # Calculate different similarity metrics
        jaccard = self.calculate_jaccard_similarity(text1, text2)
        
        # Extract words for cosine similarity
        words1 = self.extract_words(text1)
        words2 = self.extract_words(text2)
        cosine = self.calculate_cosine_similarity(words1, words2)
        
        sequence = self.calculate_sequence_similarity(text1, text2)
        
        # Weighted average of the metrics
        # Jaccard is good for word overlap
        # Cosine is good for content similarity
        # Sequence is good for structural similarity
        overall_similarity = (jaccard * 0.4 + cosine * 0.4 + sequence * 0.2)
        
        return round(overall_similarity, 4)
    
    def calculate_word_metrics(self, text1: str, text2: str) -> Tuple[int, int]:
        """
        Calculate common and unique word counts.
        Returns (common_words, unique_words)
        """
        words1 = self.extract_words(text1)
        words2 = self.extract_words(text2)
        
        common_words = len(words1.intersection(words2))
        unique_words = len(words1.symmetric_difference(words2))
        
        return common_words, unique_words
    
    def get_word_frequency_analysis(self, text1: str, text2: str) -> dict:
        """
        Get detailed word frequency analysis for both documents.
        """
        words1 = self.extract_words(text1)
        words2 = self.extract_words(text2)
        
        # Count word frequencies
        freq1 = Counter(self.preprocess_text(text1).split())
        freq2 = Counter(self.preprocess_text(text2).split())
        
        # Filter meaningful words
        freq1_filtered = {word: count for word, count in freq1.items() 
                         if len(word) > 2 and word not in self.stop_words}
        freq2_filtered = {word: count for word, count in freq2.items() 
                         if len(word) > 2 and word not in self.stop_words}
        
        return {
            "document1": {
                "total_words": len(words1),
                "top_words": dict(sorted(freq1_filtered.items(), 
                                       key=lambda x: x[1], reverse=True)[:10])
            },
            "document2": {
                "total_words": len(words2),
                "top_words": dict(sorted(freq2_filtered.items(), 
                                       key=lambda x: x[1], reverse=True)[:10])
            },
            "common_words": list(words1.intersection(words2)),
            "unique_to_doc1": list(words1 - words2),
            "unique_to_doc2": list(words2 - words1)
        }

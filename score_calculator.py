"""
Score Calculator Module
Calculates final scores with negative marking
"""
from typing import Dict


class ScoreCalculator:
    """
    Calculates final scores by combining weighted scores and negative marking
    """
    
    @staticmethod
    def calculate_final_score(
        weighted_score: float,
        negative_marks: float,
        max_score: float = 10.0
    ) -> Dict[str, float]:
        """
        Calculate final score after applying negative marking
        
        Args:
            weighted_score: Weighted score from evaluation (0-10 scale)
            negative_marks: Negative marks to deduct
            max_score: Maximum possible score for the question
        
        Returns:
            Dictionary with final_score, percentage, and scaled_score
        """
        # Scale weighted score to max_score
        scaled_score = (weighted_score / 10.0) * max_score
        
        # Apply negative marking
        final_score = max(0.0, scaled_score - negative_marks)
        
        # Calculate percentage
        percentage = (final_score / max_score) * 100.0 if max_score > 0 else 0.0
        
        return {
            "final_score": round(final_score, 2),
            "percentage": round(percentage, 2),
            "scaled_score": round(scaled_score, 2)
        }
    
    @staticmethod
    def calculate_assessment_total(
        scores: list,
        max_scores: list
    ) -> Dict[str, float]:
        """
        Calculate total assessment score from multiple questions
        
        Args:
            scores: List of final scores for each question
            max_scores: List of max possible scores for each question
        
        Returns:
            Dictionary with total_score, max_possible_score, and percentage
        """
        total_score = sum(scores)
        max_possible_score = sum(max_scores)
        
        percentage = (total_score / max_possible_score) * 100.0 if max_possible_score > 0 else 0.0
        
        return {
            "total_score": round(total_score, 2),
            "max_possible_score": round(max_possible_score, 2),
            "percentage": round(percentage, 2)
        }

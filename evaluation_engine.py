"""
AI-Based Answer Evaluation Engine
Evaluates answers based on Correctness, Depth, and Clarity
"""
import re
import time
from typing import Dict, Tuple
from config import get_settings

settings = get_settings()


class AIEvaluationEngine:
    """
    AI-based evaluation engine for scoring candidate answers
    Uses rule-based AI logic (can be replaced with OpenAI/GPT integration)
    """
    
    def __init__(self):
        self.settings = settings
    
    def evaluate_answer(
        self,
        question: str,
        answer: str,
        expected_keywords: str = None,
        max_score: float = 10.0
    ) -> Dict[str, any]:
        """
        Main evaluation method
        Returns metric scores, feedback, and processing time
        """
        start_time = time.time()
        
        # Evaluate individual metrics
        correctness = self._evaluate_correctness(question, answer, expected_keywords)
        depth = self._evaluate_depth(answer)
        clarity = self._evaluate_clarity(answer)
        
        # Calculate weighted score
        weighted_score = (
            correctness * self.settings.CORRECTNESS_WEIGHT +
            depth * self.settings.DEPTH_WEIGHT +
            clarity * self.settings.CLARITY_WEIGHT
        )
        
        # Scale to max_score
        scaled_score = (weighted_score / 10.0) * max_score
        
        # Generate feedback
        feedback = self._generate_feedback(correctness, depth, clarity)
        
        processing_time = int((time.time() - start_time) * 1000)  # milliseconds
        
        return {
            "correctness_score": round(correctness, 2),
            "depth_score": round(depth, 2),
            "clarity_score": round(clarity, 2),
            "weighted_score": round(weighted_score, 2),
            "scaled_score": round(scaled_score, 2),
            "evaluation_feedback": feedback,
            "processing_time_ms": processing_time
        }
    
    def _evaluate_correctness(
        self,
        question: str,
        answer: str,
        expected_keywords: str = None
    ) -> float:
        """
        Evaluate correctness based on keyword matching and relevance
        Score: 0-10
        """
        score = 5.0  # Base score
        
        answer_lower = answer.lower()
        question_lower = question.lower()
        
        # Extract key terms from question
        question_terms = set(re.findall(r'\b\w{4,}\b', question_lower))
        answer_terms = set(re.findall(r'\b\w{4,}\b', answer_lower))
        
        # Check keyword overlap
        if question_terms:
            overlap = len(question_terms & answer_terms) / len(question_terms)
            score += overlap * 3.0
        
        # Check for expected keywords if provided
        if expected_keywords:
            keywords = [k.strip().lower() for k in expected_keywords.split(',')]
            keyword_matches = sum(1 for kw in keywords if kw in answer_lower)
            if keywords:
                score += (keyword_matches / len(keywords)) * 2.0
        
        # Penalize very short answers
        if len(answer) < 50:
            score -= 2.0
        
        return max(0.0, min(10.0, score))
    
    def _evaluate_depth(self, answer: str) -> float:
        """
        Evaluate depth based on answer length, structure, and detail
        Score: 0-10
        """
        score = 0.0
        
        # Length-based scoring
        word_count = len(answer.split())
        if word_count < 20:
            score += 2.0
        elif word_count < 50:
            score += 4.0
        elif word_count < 100:
            score += 6.0
        elif word_count < 200:
            score += 8.0
        else:
            score += 10.0
        
        # Check for structured content (bullet points, numbers, paragraphs)
        if re.search(r'(\n\s*[-*•]\s+|\n\s*\d+\.)', answer):
            score += 1.0
        
        # Check for examples or explanations
        if re.search(r'\b(example|for instance|such as|like|e\.g\.)\b', answer.lower()):
            score += 1.0
        
        # Check for technical terms (words with 8+ characters)
        technical_terms = len(re.findall(r'\b\w{8,}\b', answer))
        if technical_terms >= 3:
            score += 1.0
        
        return max(0.0, min(10.0, score))
    
    def _evaluate_clarity(self, answer: str) -> float:
        """
        Evaluate clarity based on grammar, structure, and readability
        Score: 0-10
        """
        score = 5.0  # Base score
        
        # Check sentence structure
        sentences = re.split(r'[.!?]+', answer)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) >= 2:
            score += 2.0
        
        # Check for proper capitalization
        if answer and answer[0].isupper():
            score += 1.0
        
        # Check for punctuation
        if re.search(r'[.!?]', answer):
            score += 1.0
        
        # Penalize excessive repetition
        words = answer.lower().split()
        if len(words) > 0:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.5:
                score -= 2.0
        
        # Check for coherent paragraphs
        paragraphs = [p.strip() for p in answer.split('\n\n') if p.strip()]
        if len(paragraphs) >= 2:
            score += 1.0
        
        return max(0.0, min(10.0, score))
    
    def _generate_feedback(
        self,
        correctness: float,
        depth: float,
        clarity: float
    ) -> str:
        """Generate human-readable feedback based on scores"""
        feedback_parts = []
        
        # Correctness feedback
        if correctness >= 8:
            feedback_parts.append("Excellent correctness - answer is highly relevant and accurate.")
        elif correctness >= 6:
            feedback_parts.append("Good correctness - answer addresses the question well.")
        elif correctness >= 4:
            feedback_parts.append("Moderate correctness - answer is partially relevant.")
        else:
            feedback_parts.append("Low correctness - answer needs more relevance to the question.")
        
        # Depth feedback
        if depth >= 8:
            feedback_parts.append("Excellent depth - comprehensive and detailed explanation.")
        elif depth >= 6:
            feedback_parts.append("Good depth - adequate detail provided.")
        elif depth >= 4:
            feedback_parts.append("Moderate depth - could use more elaboration.")
        else:
            feedback_parts.append("Low depth - answer is too brief or lacks detail.")
        
        # Clarity feedback
        if clarity >= 8:
            feedback_parts.append("Excellent clarity - well-structured and easy to understand.")
        elif clarity >= 6:
            feedback_parts.append("Good clarity - answer is reasonably clear.")
        elif clarity >= 4:
            feedback_parts.append("Moderate clarity - structure could be improved.")
        else:
            feedback_parts.append("Low clarity - answer needs better organization.")
        
        return " ".join(feedback_parts)


class NegativeMarkingEngine:
    """
    Negative marking system for penalizing poor answers
    """
    
    def __init__(self):
        self.settings = settings
    
    def apply_negative_marking(
        self,
        answer: str,
        correctness_score: float,
        depth_score: float,
        clarity_score: float
    ) -> Tuple[float, str]:
        """
        Apply negative marking based on answer quality
        Returns: (negative_marks, reason)
        """
        negative_marks = 0.0
        reasons = []
        
        # Check for too short answer
        if len(answer) < self.settings.MIN_ANSWER_LENGTH:
            negative_marks += abs(self.settings.TOO_SHORT_PENALTY)
            reasons.append("Answer too short")
        
        # Check for irrelevant answer (very low correctness)
        if correctness_score < 3.0:
            negative_marks += abs(self.settings.IRRELEVANT_PENALTY)
            reasons.append("Answer appears irrelevant")
        
        # Check for mostly incorrect (low correctness but not irrelevant)
        elif correctness_score < 5.0:
            negative_marks += abs(self.settings.INCORRECT_PENALTY)
            reasons.append("Answer mostly incorrect")
        
        # Check for potential hallucination (high confidence but low correctness)
        if depth_score > 7.0 and correctness_score < 4.0:
            negative_marks += abs(self.settings.HALLUCINATION_PENALTY)
            reasons.append("Potential hallucinated or misleading content")
        
        # Check for gibberish (very low clarity)
        if clarity_score < 2.0:
            negative_marks += abs(self.settings.INCORRECT_PENALTY)
            reasons.append("Answer unclear or incoherent")
        
        reason_text = "; ".join(reasons) if reasons else None
        
        return negative_marks, reason_text

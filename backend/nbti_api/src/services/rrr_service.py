"""
RRR (Recommendation, Recognition, and Reward) Service
Handles calculation of combined scores for promotion decisions.

Formula: Combined Score = (Exam × 70%) + (PMS × 20%) + (Seniority × 10%)
"""

from typing import List, Dict, Optional
from src.models import User, PMSEvaluation, EMMExamSubmission


def calculate_combined_score(exam_score: float, pms_score: float, seniority_score: float) -> float:
    """
    Calculate combined RRR score using the weighted formula.
    
    Args:
        exam_score: Exam score (0-100)
        pms_score: PMS score (0-100)
        seniority_score: Seniority score (0-100)
    
    Returns:
        Combined score (0-100)
    """
    if exam_score is None or pms_score is None or seniority_score is None:
        return 0.0
    
    combined = (exam_score * 0.70) + (pms_score * 0.20) + (seniority_score * 0.10)
    return round(combined, 2)


def calculate_pms_score(evaluation: PMSEvaluation) -> float:
    """
    Calculate PMS score as percentage (0-100).
    
    Args:
        evaluation: PMSEvaluation object
    
    Returns:
        PMS score as percentage (0-100)
    """
    if not evaluation:
        return 0.0
    
    # Calculate final score if not already calculated
    if evaluation.final_score is None:
        evaluation.calculate_final_score()
    
    # Convert to percentage (final_score is on 1-5 scale)
    return evaluation.get_pms_percentage()


def get_exam_score(user: User, exam_submission: EMMExamSubmission) -> float:
    """
    Get exam score as percentage (0-100).
    
    Args:
        user: User object
        exam_submission: EMMExamSubmission object
    
    Returns:
        Exam score as percentage (0-100)
    """
    if not exam_submission or exam_submission.percentage is None:
        return 0.0
    
    return float(exam_submission.percentage)


def calculate_seniority_score(user: User, candidates_in_same_grade: List[User]) -> float:
    """
    Calculate seniority score using priority-based ranking.
    
    Priority hierarchy:
    1. Step (higher step = more senior)
    2. Confirmation date (earlier date = more senior)
    3. Age (older = more senior)
    4. File number (lower number = more senior)
    
    Args:
        user: User object to calculate score for
        candidates_in_same_grade: List of all candidates in the same grade
    
    Returns:
        Seniority score (0-100), where 100 is most senior
    """
    return user.calculate_seniority_score(candidates_in_same_grade)


def get_latest_pms_evaluation(user: User, year: int = None) -> Optional[PMSEvaluation]:
    """
    Get the latest PMS evaluation for a user.
    
    Args:
        user: User object
        year: Optional year to filter by
    
    Returns:
        Latest PMSEvaluation or None
    """
    query = PMSEvaluation.query.filter_by(staff_id=user.id)
    
    if year:
        query = query.filter_by(year=year)
    
    return query.order_by(PMSEvaluation.created_at.desc()).first()


def get_latest_exam_submission(user: User, exam_id: int = None, is_promotional: bool = True) -> Optional[EMMExamSubmission]:
    """
    Get the latest exam submission for a user.
    
    Args:
        user: User object
        exam_id: Optional specific exam ID
        is_promotional: Filter for promotional exams only
    
    Returns:
        Latest EMMExamSubmission or None
    """
    from src.models import EMMExam
    
    query = EMMExamSubmission.query.filter_by(
        candidate_id=user.id,
        status='Completed'
    )
    
    if exam_id:
        query = query.filter_by(exam_id=exam_id)
    elif is_promotional:
        # Join with exam table to filter promotional exams
        query = query.join(EMMExam).filter(EMMExam.is_promotional_exam == True)
    
    return query.order_by(EMMExamSubmission.submitted_at.desc()).first()


def calculate_user_rrr_scores(user: User, candidates_in_same_grade: List[User], 
                               pms_year: int = None, exam_id: int = None) -> Dict[str, float]:
    """
    Calculate all RRR scores for a user.
    
    Args:
        user: User object
        candidates_in_same_grade: List of candidates in same grade for seniority ranking
        pms_year: Optional year for PMS evaluation
        exam_id: Optional specific exam ID
    
    Returns:
        Dictionary with exam_score, pms_score, seniority_score, and combined_score
    """
    # Get PMS score
    pms_evaluation = get_latest_pms_evaluation(user, pms_year)
    pms_score = calculate_pms_score(pms_evaluation) if pms_evaluation else 0.0
    
    # Get Exam score
    exam_submission = get_latest_exam_submission(user, exam_id)
    exam_score = get_exam_score(user, exam_submission) if exam_submission else 0.0
    
    # Get Seniority score
    seniority_score = calculate_seniority_score(user, candidates_in_same_grade)
    
    # Calculate combined score
    combined_score = calculate_combined_score(exam_score, pms_score, seniority_score)
    
    return {
        'exam_score': exam_score,
        'pms_score': pms_score,
        'seniority_score': seniority_score,
        'combined_score': combined_score
    }


def rank_candidates_by_combined_score(candidates: List[Dict]) -> List[Dict]:
    """
    Rank candidates by combined score (highest first).
    
    Args:
        candidates: List of candidate dictionaries with 'combined_score' key
    
    Returns:
        Sorted list of candidates with 'rank' added
    """
    # Sort by combined score (descending)
    sorted_candidates = sorted(candidates, key=lambda x: x['combined_score'], reverse=True)
    
    # Add rank
    for rank, candidate in enumerate(sorted_candidates, start=1):
        candidate['rank'] = rank
    
    return sorted_candidates


"""
RRR Allocation Service
Handles rank-based allocation of promotions, recognition, and rewards based on vacancy slots.
"""

from typing import List, Dict, Tuple
from datetime import datetime, date
from src.models import User, RRRVacancy, RRRRecommendation, db
from src.services.rrr_service import calculate_user_rrr_scores


def get_eligible_candidates_for_grade(grade: int, promotion_cycle: str) -> List[User]:
    """
    Get all eligible candidates for a specific CONRAISS grade.
    
    Args:
        grade: CONRAISS grade (2-15)
        promotion_cycle: Promotion cycle (e.g., "2024", "2025")
    
    Returns:
        List of eligible User objects
    """
    # Get all active users in the specified grade
    candidates = User.query.filter_by(
        conraiss_grade=grade,
        is_active=True
    ).all()
    
    # TODO: Add eligibility checks (time in grade, disciplinary status, etc.)
    # For now, return all users in the grade
    
    return candidates


def rank_candidates(candidates: List[User], promotion_cycle: str, 
                    pms_year: int = None, exam_id: int = None) -> List[Dict]:
    """
    Rank candidates by combined score with tie-breaking.
    
    Args:
        candidates: List of User objects
        promotion_cycle: Promotion cycle identifier
        pms_year: Optional year for PMS evaluation
        exam_id: Optional specific exam ID
    
    Returns:
        List of candidate dictionaries sorted by rank
    """
    if not candidates:
        return []
    
    candidate_scores = []
    
    for user in candidates:
        # Calculate scores
        scores = calculate_user_rrr_scores(user, candidates, pms_year, exam_id)
        
        candidate_scores.append({
            'user_id': user.id,
            'user': user,
            'exam_score': scores['exam_score'],
            'pms_score': scores['pms_score'],
            'seniority_score': scores['seniority_score'],
            'combined_score': scores['combined_score']
        })
    
    # Sort by combined score (descending), then by seniority score as tie-breaker
    sorted_candidates = sorted(
        candidate_scores, 
        key=lambda x: (x['combined_score'], x['seniority_score']), 
        reverse=True
    )
    
    # Add rank
    for rank, candidate in enumerate(sorted_candidates, start=1):
        candidate['rank'] = rank
    
    return sorted_candidates


def allocate_rrr_for_grade(grade: int, promotion_cycle: str, 
                           promotion_vacancies: int = 0,
                           recognition_slots: int = 0,
                           reward_slots: int = 0,
                           pms_year: int = None,
                           exam_id: int = None) -> Dict:
    """
    Allocate RRR (Promotion, Recognition, Reward) for a specific grade.
    
    Args:
        grade: CONRAISS grade
        promotion_cycle: Promotion cycle identifier
        promotion_vacancies: Number of promotion slots
        recognition_slots: Number of recognition slots
        reward_slots: Number of reward slots
        pms_year: Optional year for PMS evaluation
        exam_id: Optional specific exam ID
    
    Returns:
        Dictionary with allocation results
    """
    # Get eligible candidates
    candidates = get_eligible_candidates_for_grade(grade, promotion_cycle)
    
    if not candidates:
        return {
            'grade': grade,
            'total_candidates': 0,
            'promoted': [],
            'recognized': [],
            'rewarded': [],
            'message': 'No eligible candidates found'
        }
    
    # Rank candidates
    ranked_candidates = rank_candidates(candidates, promotion_cycle, pms_year, exam_id)
    
    # Allocate promotions (top N candidates)
    promoted = ranked_candidates[:promotion_vacancies] if promotion_vacancies > 0 else []
    
    # Allocate recognition (next M candidates after promotions)
    recognition_start = len(promoted)
    recognition_end = recognition_start + recognition_slots
    recognized = ranked_candidates[recognition_start:recognition_end] if recognition_slots > 0 else []
    
    # Allocate rewards (next K candidates after recognition)
    reward_start = recognition_end
    reward_end = reward_start + reward_slots
    rewarded = ranked_candidates[reward_start:reward_end] if reward_slots > 0 else []
    
    return {
        'grade': grade,
        'total_candidates': len(ranked_candidates),
        'all_candidates': ranked_candidates,
        'promoted': promoted,
        'recognized': recognized,
        'rewarded': rewarded,
        'promotion_vacancies': promotion_vacancies,
        'recognition_slots': recognition_slots,
        'reward_slots': reward_slots
    }


def allocate_rrr_for_all_grades(promotion_cycle: str, pms_year: int = None, 
                                exam_id: int = None) -> Dict[int, Dict]:
    """
    Allocate RRR for all CONRAISS grades based on configured vacancies.
    
    Args:
        promotion_cycle: Promotion cycle identifier
        pms_year: Optional year for PMS evaluation
        exam_id: Optional specific exam ID
    
    Returns:
        Dictionary mapping grade to allocation results
    """
    # Get all vacancy configurations for this cycle
    vacancies = RRRVacancy.query.filter_by(
        promotion_cycle=promotion_cycle,
        is_active=True
    ).all()
    
    if not vacancies:
        return {}
    
    results = {}
    
    for vacancy in vacancies:
        allocation = allocate_rrr_for_grade(
            grade=vacancy.conraiss_grade,
            promotion_cycle=promotion_cycle,
            promotion_vacancies=vacancy.promotion_vacancies,
            recognition_slots=vacancy.recognition_slots,
            reward_slots=vacancy.reward_slots,
            pms_year=pms_year,
            exam_id=exam_id
        )
        results[vacancy.conraiss_grade] = allocation
    
    return results


def generate_rrr_recommendations(allocation_results: Dict[int, Dict], 
                                 promotion_cycle: str,
                                 recommended_by: int = None) -> List[RRRRecommendation]:
    """
    Generate RRRRecommendation records from allocation results.
    
    Args:
        allocation_results: Results from allocate_rrr_for_all_grades()
        promotion_cycle: Promotion cycle identifier
        recommended_by: User ID of recommender
    
    Returns:
        List of created RRRRecommendation objects
    """
    recommendations = []
    
    for grade, allocation in allocation_results.items():
        all_candidates = allocation['all_candidates']
        
        for candidate in all_candidates:
            # Check if recommendation already exists
            existing = RRRRecommendation.query.filter_by(
                user_id=candidate['user_id'],
                promotion_cycle=promotion_cycle
            ).first()
            
            if existing:
                # Update existing recommendation
                recommendation = existing
            else:
                # Create new recommendation
                recommendation = RRRRecommendation(
                    user_id=candidate['user_id'],
                    promotion_cycle=promotion_cycle,
                    conraiss_grade=grade
                )
            
            # Set scores
            recommendation.exam_score = candidate['exam_score']
            recommendation.pms_score = candidate['pms_score']
            recommendation.seniority_score = candidate['seniority_score']
            recommendation.combined_score = candidate['combined_score']
            recommendation.rank_in_grade = candidate['rank']
            recommendation.total_candidates_in_grade = allocation['total_candidates']
            
            # Determine RRR allocation
            recommendation.is_promoted = candidate in allocation['promoted']
            recommendation.is_recognized = candidate in allocation['recognized']
            recommendation.is_rewarded = candidate in allocation['rewarded']
            
            # Set promotion details if promoted
            if recommendation.is_promoted:
                recommendation.promoted_to_grade = grade + 1  # Next grade
                # Step allocation will be calculated separately
                recommendation.status = 'Pending'
            
            # Set recommender
            if recommended_by:
                recommendation.recommended_by = recommended_by
            
            if not existing:
                db.session.add(recommendation)
            
            recommendations.append(recommendation)
    
    db.session.commit()
    
    return recommendations


def get_rrr_rankings_for_grade(grade: int, promotion_cycle: str) -> List[Dict]:
    """
    Get RRR rankings for a specific grade and cycle.
    
    Args:
        grade: CONRAISS grade
        promotion_cycle: Promotion cycle identifier
    
    Returns:
        List of candidate rankings with RRR allocations
    """
    recommendations = RRRRecommendation.query.filter_by(
        conraiss_grade=grade,
        promotion_cycle=promotion_cycle
    ).order_by(RRRRecommendation.rank_in_grade).all()
    
    return [rec.to_dict() for rec in recommendations]


def approve_rrr_recommendation(recommendation_id: int, approved_by: int) -> RRRRecommendation:
    """
    Approve an RRR recommendation.
    
    Args:
        recommendation_id: RRRRecommendation ID
        approved_by: User ID of approver
    
    Returns:
        Updated RRRRecommendation object
    """
    recommendation = RRRRecommendation.query.get(recommendation_id)
    
    if not recommendation:
        raise ValueError(f"Recommendation {recommendation_id} not found")
    
    recommendation.status = 'Approved'
    recommendation.approved_by = approved_by
    recommendation.approval_date = datetime.utcnow()
    
    # If promoted, update user record
    if recommendation.is_promoted and recommendation.promoted_to_grade and recommendation.promoted_to_step:
        user = User.query.get(recommendation.user_id)
        if user:
            user.conraiss_grade = recommendation.promoted_to_grade
            user.conraiss_step = recommendation.promoted_to_step
            user.date_of_last_promotion = recommendation.promotion_effective_date or date.today()
            user.last_rrr_date = date.today()
            user.last_rrr_type = 'Promotion'
            user.failed_promotion_attempts = 0  # Reset failed attempts
    
    db.session.commit()
    
    return recommendation


def reject_rrr_recommendation(recommendation_id: int, rejection_reason: str) -> RRRRecommendation:
    """
    Reject an RRR recommendation.
    
    Args:
        recommendation_id: RRRRecommendation ID
        rejection_reason: Reason for rejection
    
    Returns:
        Updated RRRRecommendation object
    """
    recommendation = RRRRecommendation.query.get(recommendation_id)
    
    if not recommendation:
        raise ValueError(f"Recommendation {recommendation_id} not found")
    
    recommendation.status = 'Rejected'
    recommendation.rejection_reason = rejection_reason
    
    # If promotion was rejected, increment failed attempts
    if recommendation.is_promoted:
        user = User.query.get(recommendation.user_id)
        if user:
            user.failed_promotion_attempts += 1
    
    db.session.commit()
    
    return recommendation


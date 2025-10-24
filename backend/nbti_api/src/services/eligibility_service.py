"""
Eligibility Service
Handles promotion eligibility checking based on CONRAISS rules.
"""

from typing import Dict, List
from datetime import date
from src.models import User, RRRVacancy


def get_standard_eligibility_cycle(conraiss_grade: int) -> int:
    """
    Get standard eligibility cycle (years) for a CONRAISS grade.
    
    Args:
        conraiss_grade: CONRAISS grade (2-15)
    
    Returns:
        Number of years required before eligible for promotion
    """
    if 2 <= conraiss_grade <= 5:
        return 2  # Every 2 years
    elif 6 <= conraiss_grade <= 12:
        return 3  # Every 3 years
    elif 13 <= conraiss_grade <= 14:
        return 4  # Every 4 years
    elif conraiss_grade == 15:
        return 0  # Grade 15 is the highest, no promotion
    else:
        return 3  # Default


def has_active_disciplinary_action(user: User) -> bool:
    """
    Check if user has active disciplinary action.
    
    Args:
        user: User object
    
    Returns:
        True if user has active disciplinary action
    """
    # TODO: Implement disciplinary action checking
    # For now, return False (no disciplinary actions)
    return False


def is_eligible_for_promotion(user: User, target_grade: int = None, 
                              check_vacancy: bool = False,
                              promotion_cycle: str = None) -> Dict:
    """
    Check if user is eligible for promotion.
    
    Eligibility criteria:
    1. Time in grade requirement met (or failed previous attempt)
    2. No active disciplinary actions
    3. Has current grade and step information
    4. Not already at maximum grade
    5. (Optional) Vacancy exists for target grade
    
    Args:
        user: User object
        target_grade: Optional target grade (defaults to current + 1)
        check_vacancy: Whether to check for vacancy availability
        promotion_cycle: Promotion cycle for vacancy check
    
    Returns:
        Dictionary with eligibility status and details
    """
    if not user.conraiss_grade or not user.conraiss_step:
        return {
            'eligible': False,
            'reason': 'User does not have grade/step information',
            'details': {}
        }
    
    current_grade = user.conraiss_grade
    
    if target_grade is None:
        target_grade = current_grade + 1
    
    # Check if already at maximum grade
    if current_grade >= 15:
        return {
            'eligible': False,
            'reason': 'Already at maximum CONRAISS grade (15)',
            'details': {'current_grade': current_grade}
        }
    
    # Check disciplinary actions
    if has_active_disciplinary_action(user):
        return {
            'eligible': False,
            'reason': 'Has active disciplinary action',
            'details': {}
        }
    
    # Calculate time in grade
    if user.date_of_last_promotion:
        days_in_grade = (date.today() - user.date_of_last_promotion).days
        years_in_grade = days_in_grade / 365.25
    elif user.date_of_first_appointment:
        days_in_grade = (date.today() - user.date_of_first_appointment).days
        years_in_grade = days_in_grade / 365.25
    else:
        return {
            'eligible': False,
            'reason': 'Cannot determine time in grade (missing appointment dates)',
            'details': {}
        }
    
    # Get standard eligibility cycle
    standard_cycle = get_standard_eligibility_cycle(current_grade)
    
    # Check if failed previous promotion attempt (eligible every year after failure)
    failed_attempts = user.failed_promotion_attempts or 0
    
    if failed_attempts > 0:
        # After failed attempt, eligible every year
        required_years = 1
    else:
        # Standard eligibility cycle
        required_years = standard_cycle
    
    # Check time requirement
    if years_in_grade < required_years:
        return {
            'eligible': False,
            'reason': f'Insufficient time in grade (requires {required_years} years)',
            'details': {
                'current_grade': current_grade,
                'years_in_grade': round(years_in_grade, 2),
                'required_years': required_years,
                'years_remaining': round(required_years - years_in_grade, 2),
                'failed_attempts': failed_attempts
            }
        }
    
    # Check vacancy if requested
    if check_vacancy and promotion_cycle:
        vacancy = RRRVacancy.query.filter_by(
            conraiss_grade=current_grade,
            promotion_cycle=promotion_cycle,
            is_active=True
        ).first()
        
        if not vacancy or vacancy.promotion_vacancies <= 0:
            return {
                'eligible': False,
                'reason': f'No promotion vacancies available for Grade {current_grade} in cycle {promotion_cycle}',
                'details': {
                    'current_grade': current_grade,
                    'promotion_cycle': promotion_cycle
                }
            }
    
    # Eligible!
    return {
        'eligible': True,
        'reason': 'Meets all eligibility criteria',
        'details': {
            'current_grade': current_grade,
            'target_grade': target_grade,
            'years_in_grade': round(years_in_grade, 2),
            'required_years': required_years,
            'failed_attempts': failed_attempts,
            'standard_cycle': standard_cycle
        }
    }


def get_eligible_candidates(target_grade: int = None, promotion_cycle: str = None) -> List[User]:
    """
    Get all eligible candidates for promotion.
    
    Args:
        target_grade: Optional filter by target grade
        promotion_cycle: Optional promotion cycle for vacancy check
    
    Returns:
        List of eligible User objects
    """
    # Get all active users
    users = User.query.filter_by(is_active=True).all()
    
    eligible_users = []
    
    for user in users:
        if target_grade and user.conraiss_grade != target_grade - 1:
            # Skip if not in the grade below target
            continue
        
        eligibility = is_eligible_for_promotion(
            user, 
            target_grade=target_grade,
            check_vacancy=False,  # Don't check vacancy for bulk query
            promotion_cycle=promotion_cycle
        )
        
        if eligibility['eligible']:
            eligible_users.append(user)
    
    return eligible_users


def update_eligibility_status_for_all_staff() -> Dict:
    """
    Batch update eligibility status for all staff.
    This can be run periodically to update eligibility flags.
    
    Returns:
        Dictionary with statistics
    """
    users = User.query.filter_by(is_active=True).all()
    
    eligible_count = 0
    ineligible_count = 0
    
    for user in users:
        eligibility = is_eligible_for_promotion(user)
        
        if eligibility['eligible']:
            eligible_count += 1
        else:
            ineligible_count += 1
    
    return {
        'total_users': len(users),
        'eligible': eligible_count,
        'ineligible': ineligible_count
    }


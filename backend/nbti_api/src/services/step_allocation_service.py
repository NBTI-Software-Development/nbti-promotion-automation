"""
Step Allocation Service
Handles promotion step allocation to ensure salary increment.
"""

from typing import Optional, Tuple, Dict
from datetime import date
from src.models import User, SalaryScale, StepIncrementLog, db


def get_max_step_for_grade(grade: int) -> int:
    """
    Get maximum step for a CONRAISS grade.
    
    Args:
        grade: CONRAISS grade (2-15)
    
    Returns:
        Maximum step number
    """
    if 2 <= grade <= 9:
        return 15
    elif 10 <= grade <= 12:
        return 11
    elif 13 <= grade <= 15:
        return 9
    else:
        return 15  # Default


def get_salary_for_grade_step(grade: int, step: int) -> Optional[float]:
    """
    Get annual salary for a specific grade and step.
    
    Args:
        grade: CONRAISS grade
        step: Step number
    
    Returns:
        Annual salary or None if not found
    """
    salary_record = SalaryScale.query.filter_by(
        conraiss_grade=grade,
        step=step,
        is_active=True
    ).first()
    
    if salary_record:
        return float(salary_record.annual_salary)
    
    return None


def calculate_promotion_step(current_grade: int, current_step: int, new_grade: int) -> Tuple[int, float, float]:
    """
    Calculate the appropriate step in the new grade that ensures salary increment.
    
    Args:
        current_grade: Current CONRAISS grade
        current_step: Current step
        new_grade: New CONRAISS grade after promotion
    
    Returns:
        Tuple of (recommended_step, current_salary, new_salary)
    """
    # Get current salary
    current_salary = get_salary_for_grade_step(current_grade, current_step)
    
    if current_salary is None:
        raise ValueError(f"Could not find salary for Grade {current_grade} Step {current_step}")
    
    # Find minimum step in new grade where salary > current salary
    max_step = get_max_step_for_grade(new_grade)
    
    for step in range(1, max_step + 1):
        new_salary = get_salary_for_grade_step(new_grade, step)
        
        if new_salary and new_salary > current_salary:
            return step, current_salary, new_salary
    
    # If no step provides increment, return max step
    # (This is an edge case that shouldn't happen with proper CONRAISS structure)
    new_salary = get_salary_for_grade_step(new_grade, max_step)
    return max_step, current_salary, new_salary or current_salary


def apply_promotion(user: User, new_grade: int, new_step: int, 
                   effective_date: date = None, processed_by: int = None,
                   notes: str = None) -> Tuple[User, StepIncrementLog]:
    """
    Apply promotion to a user (update grade and step).
    
    Args:
        user: User object
        new_grade: New CONRAISS grade
        new_step: New step
        effective_date: Effective date of promotion
        processed_by: User ID of processor
        notes: Optional notes
    
    Returns:
        Tuple of (updated User, StepIncrementLog)
    """
    if effective_date is None:
        effective_date = date.today()
    
    # Store old values
    old_grade = user.conraiss_grade
    old_step = user.conraiss_step
    
    # Update user
    user.conraiss_grade = new_grade
    user.conraiss_step = new_step
    user.date_of_last_promotion = effective_date
    user.last_rrr_date = effective_date
    user.last_rrr_type = 'Promotion'
    user.failed_promotion_attempts = 0  # Reset failed attempts
    
    # Log the promotion
    log = StepIncrementLog(
        user_id=user.id,
        previous_step=old_step,
        new_step=new_step,
        increment_date=effective_date,
        increment_type='Promotion',
        processed_by=processed_by,
        notes=notes or f"Promoted from Grade {old_grade} Step {old_step} to Grade {new_grade} Step {new_step}"
    )
    
    db.session.add(log)
    db.session.commit()
    
    return user, log


def increment_user_step(user: User, processed_by: int = None, 
                       notes: str = None) -> Optional[StepIncrementLog]:
    """
    Increment user's step by 1 (for annual increment).
    
    Args:
        user: User object
        processed_by: User ID of processor (None for automated)
        notes: Optional notes
    
    Returns:
        StepIncrementLog if incremented, None if already at max step
    """
    if not user.conraiss_grade or not user.conraiss_step:
        return None
    
    max_step = get_max_step_for_grade(user.conraiss_grade)
    
    # Check if already at max step
    if user.conraiss_step >= max_step:
        return None
    
    # Store old step
    old_step = user.conraiss_step
    
    # Increment step
    user.conraiss_step += 1
    
    # Log the increment
    log = StepIncrementLog(
        user_id=user.id,
        previous_step=old_step,
        new_step=user.conraiss_step,
        increment_date=date.today(),
        increment_type='Annual',
        processed_by=processed_by,
        notes=notes or f"Annual step increment from {old_step} to {user.conraiss_step}"
    )
    
    db.session.add(log)
    db.session.commit()
    
    return log


def get_promotion_step_recommendation(user: User, target_grade: int) -> Dict:
    """
    Get promotion step recommendation for a user.
    
    Args:
        user: User object
        target_grade: Target CONRAISS grade
    
    Returns:
        Dictionary with recommendation details
    """
    if not user.conraiss_grade or not user.conraiss_step:
        return {
            'error': 'User does not have current grade/step information',
            'can_calculate': False
        }
    
    try:
        recommended_step, current_salary, new_salary = calculate_promotion_step(
            user.conraiss_grade,
            user.conraiss_step,
            target_grade
        )
        
        salary_increment = new_salary - current_salary
        increment_percentage = (salary_increment / current_salary) * 100
        
        return {
            'can_calculate': True,
            'current_grade': user.conraiss_grade,
            'current_step': user.conraiss_step,
            'current_salary': current_salary,
            'target_grade': target_grade,
            'recommended_step': recommended_step,
            'new_salary': new_salary,
            'salary_increment': salary_increment,
            'increment_percentage': round(increment_percentage, 2)
        }
    except ValueError as e:
        return {
            'error': str(e),
            'can_calculate': False
        }


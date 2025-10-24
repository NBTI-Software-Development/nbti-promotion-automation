"""
Audit Logging Service
Provides forensic-level audit logging for all system actions.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from flask import request
from src.models import db, AuditLog


def log_action(
    user_id: Optional[int],
    action_type: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    old_value: Optional[Dict] = None,
    new_value: Optional[Dict] = None,
    is_sensitive: bool = False
) -> AuditLog:
    """
    Log an action to the audit trail.
    
    Args:
        user_id: ID of user performing the action (None for system actions)
        action_type: Type of action (CREATE, UPDATE, DELETE, VIEW, LOGIN, LOGOUT, etc.)
        entity_type: Type of entity affected (User, PMSEvaluation, EMMExam, etc.)
        entity_id: ID of the affected entity
        old_value: Previous state (for UPDATE/DELETE)
        new_value: New state (for CREATE/UPDATE)
        is_sensitive: Whether this action involves sensitive data
    
    Returns:
        Created AuditLog object
    """
    # Get request context
    ip_address = None
    user_agent = None
    session_id = None
    
    if request:
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        # Try to get session ID from JWT or session
        # This would need to be implemented based on your auth setup
    
    # Create audit log entry
    log = AuditLog(
        id=str(uuid.uuid4()),
        user_id=user_id,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=session_id,
        is_sensitive=is_sensitive,
        timestamp=datetime.utcnow()
    )
    
    db.session.add(log)
    db.session.commit()
    
    return log


def log_user_action(user_id: int, action: str, details: Dict = None):
    """
    Log a user action (login, logout, password change, etc.).
    
    Args:
        user_id: User ID
        action: Action performed
        details: Additional details
    """
    return log_action(
        user_id=user_id,
        action_type=action,
        entity_type='User',
        entity_id=user_id,
        new_value=details,
        is_sensitive=True
    )


def log_pms_action(user_id: int, action: str, evaluation_id: int, 
                   old_data: Dict = None, new_data: Dict = None):
    """
    Log a PMS-related action.
    
    Args:
        user_id: User performing the action
        action: Action type (CREATE, UPDATE, SUBMIT, APPROVE, etc.)
        evaluation_id: PMS evaluation ID
        old_data: Previous state
        new_data: New state
    """
    return log_action(
        user_id=user_id,
        action_type=action,
        entity_type='PMSEvaluation',
        entity_id=evaluation_id,
        old_value=old_data,
        new_value=new_data,
        is_sensitive=False
    )


def log_exam_action(user_id: int, action: str, exam_id: int = None, 
                    submission_id: int = None, details: Dict = None):
    """
    Log an exam-related action.
    
    Args:
        user_id: User performing the action
        action: Action type (START, SUBMIT, GRADE, etc.)
        exam_id: Exam ID
        submission_id: Submission ID
        details: Additional details
    """
    entity_id = submission_id if submission_id else exam_id
    entity_type = 'EMMExamSubmission' if submission_id else 'EMMExam'
    
    return log_action(
        user_id=user_id,
        action_type=action,
        entity_type=entity_type,
        entity_id=entity_id,
        new_value=details,
        is_sensitive=False
    )


def log_rrr_action(user_id: int, action: str, recommendation_id: int = None,
                   old_data: Dict = None, new_data: Dict = None):
    """
    Log an RRR-related action.
    
    Args:
        user_id: User performing the action
        action: Action type (ALLOCATE, APPROVE, REJECT, etc.)
        recommendation_id: RRR recommendation ID
        old_data: Previous state
        new_data: New state
    """
    return log_action(
        user_id=user_id,
        action_type=action,
        entity_type='RRRRecommendation',
        entity_id=recommendation_id,
        old_value=old_data,
        new_value=new_data,
        is_sensitive=True  # RRR decisions are sensitive
    )


def log_promotion_action(user_id: int, action: str, target_user_id: int,
                        old_data: Dict = None, new_data: Dict = None):
    """
    Log a promotion-related action.
    
    Args:
        user_id: User performing the action
        action: Action type (PROMOTE, INCREMENT_STEP, etc.)
        target_user_id: User being promoted
        old_data: Previous state
        new_data: New state
    """
    return log_action(
        user_id=user_id,
        action_type=action,
        entity_type='Promotion',
        entity_id=target_user_id,
        old_value=old_data,
        new_value=new_data,
        is_sensitive=True
    )


def get_audit_logs(
    user_id: Optional[int] = None,
    action_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    is_sensitive: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100
) -> list:
    """
    Query audit logs with filters.
    
    Args:
        user_id: Filter by user
        action_type: Filter by action type
        entity_type: Filter by entity type
        entity_id: Filter by entity ID
        is_sensitive: Filter by sensitivity
        start_date: Filter by start date
        end_date: Filter by end date
        limit: Maximum number of results
    
    Returns:
        List of AuditLog objects
    """
    query = AuditLog.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if action_type:
        query = query.filter_by(action_type=action_type)
    
    if entity_type:
        query = query.filter_by(entity_type=entity_type)
    
    if entity_id:
        query = query.filter_by(entity_id=entity_id)
    
    if is_sensitive is not None:
        query = query.filter_by(is_sensitive=is_sensitive)
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    query = query.order_by(AuditLog.timestamp.desc()).limit(limit)
    
    return query.all()


def get_entity_history(entity_type: str, entity_id: int) -> list:
    """
    Get complete audit history for a specific entity.
    
    Args:
        entity_type: Type of entity
        entity_id: Entity ID
    
    Returns:
        List of AuditLog objects ordered by timestamp
    """
    return AuditLog.query.filter_by(
        entity_type=entity_type,
        entity_id=entity_id
    ).order_by(AuditLog.timestamp.asc()).all()


def get_user_activity(user_id: int, days: int = 30) -> list:
    """
    Get recent activity for a user.
    
    Args:
        user_id: User ID
        days: Number of days to look back
    
    Returns:
        List of AuditLog objects
    """
    from datetime import timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    return AuditLog.query.filter(
        AuditLog.user_id == user_id,
        AuditLog.timestamp >= start_date
    ).order_by(AuditLog.timestamp.desc()).all()


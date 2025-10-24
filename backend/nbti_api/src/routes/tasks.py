"""
Task Management Routes
API endpoints for managing background tasks and scheduled jobs.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import User
from src.tasks import (
    process_annual_step_increment,
    generate_rrr_report,
    backup_database,
    cleanup_old_audit_logs
)

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/trigger-step-increment', methods=['POST'])
@jwt_required()
def trigger_step_increment():
    """Manually trigger annual step increment (for testing or manual execution)."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is HR Admin
    if not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Trigger the task asynchronously
    task = process_annual_step_increment.delay()
    
    return jsonify({
        'message': 'Annual step increment task triggered',
        'task_id': task.id,
        'status': 'Processing'
    }), 202


@tasks_bp.route('/generate-rrr-report/<promotion_cycle>', methods=['POST'])
@jwt_required()
def trigger_rrr_report(promotion_cycle):
    """Generate RRR report for a promotion cycle."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is HR Admin or Director
    if not (current_user.has_role('HR Admin') or current_user.has_role('Director')):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Trigger the task asynchronously
    task = generate_rrr_report.delay(promotion_cycle)
    
    return jsonify({
        'message': f'RRR report generation triggered for cycle {promotion_cycle}',
        'task_id': task.id,
        'status': 'Processing'
    }), 202


@tasks_bp.route('/backup-database', methods=['POST'])
@jwt_required()
def trigger_backup():
    """Manually trigger database backup."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is HR Admin
    if not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Trigger the task asynchronously
    task = backup_database.delay()
    
    return jsonify({
        'message': 'Database backup task triggered',
        'task_id': task.id,
        'status': 'Processing'
    }), 202


@tasks_bp.route('/cleanup-audit-logs', methods=['POST'])
@jwt_required()
def trigger_cleanup():
    """Manually trigger audit log cleanup."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is HR Admin
    if not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json() or {}
    days_to_keep = data.get('days_to_keep', 3650)  # Default 10 years
    
    # Trigger the task asynchronously
    task = cleanup_old_audit_logs.delay(days_to_keep)
    
    return jsonify({
        'message': f'Audit log cleanup task triggered (keeping last {days_to_keep} days)',
        'task_id': task.id,
        'status': 'Processing'
    }), 202


@tasks_bp.route('/task-status/<task_id>', methods=['GET'])
@jwt_required()
def get_task_status(task_id):
    """Get status of a background task."""
    from celery.result import AsyncResult
    from src.celery_app import celery_app
    
    task = AsyncResult(task_id, app=celery_app)
    
    if task.state == 'PENDING':
        response = {
            'task_id': task_id,
            'state': task.state,
            'status': 'Task is waiting to be executed'
        }
    elif task.state == 'STARTED':
        response = {
            'task_id': task_id,
            'state': task.state,
            'status': 'Task is currently running'
        }
    elif task.state == 'SUCCESS':
        response = {
            'task_id': task_id,
            'state': task.state,
            'status': 'Task completed successfully',
            'result': task.result
        }
    elif task.state == 'FAILURE':
        response = {
            'task_id': task_id,
            'state': task.state,
            'status': 'Task failed',
            'error': str(task.info)
        }
    else:
        response = {
            'task_id': task_id,
            'state': task.state,
            'status': str(task.info)
        }
    
    return jsonify(response), 200


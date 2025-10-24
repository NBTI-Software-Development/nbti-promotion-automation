"""
Promotion Routes
API endpoints for managing promotions, step allocation, and eligibility.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date
from src.models import db, User, StepIncrementLog
from src.services.step_allocation_service import (
    get_promotion_step_recommendation,
    apply_promotion,
    increment_user_step,
    get_max_step_for_grade
)
from src.services.eligibility_service import (
    is_eligible_for_promotion,
    get_eligible_candidates,
    update_eligibility_status_for_all_staff
)

promotion_bp = Blueprint('promotion', __name__)


@promotion_bp.route('/eligibility/<int:user_id>', methods=['GET'])
@jwt_required()
def check_eligibility(user_id):
    """Check promotion eligibility for a user."""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    target_grade = request.args.get('target_grade', type=int)
    check_vacancy = request.args.get('check_vacancy', 'false').lower() == 'true'
    promotion_cycle = request.args.get('promotion_cycle')
    
    eligibility = is_eligible_for_promotion(
        user,
        target_grade=target_grade,
        check_vacancy=check_vacancy,
        promotion_cycle=promotion_cycle
    )
    
    return jsonify(eligibility), 200


@promotion_bp.route('/eligible-candidates', methods=['GET'])
@jwt_required()
def get_eligible():
    """Get all eligible candidates for promotion."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is HR Admin or Director
    if not (current_user.has_role('HR Admin') or current_user.has_role('Director')):
        return jsonify({'error': 'Unauthorized'}), 403
    
    target_grade = request.args.get('target_grade', type=int)
    promotion_cycle = request.args.get('promotion_cycle')
    
    eligible_users = get_eligible_candidates(target_grade, promotion_cycle)
    
    return jsonify({
        'count': len(eligible_users),
        'candidates': [u.to_dict() for u in eligible_users]
    }), 200


@promotion_bp.route('/step-recommendation/<int:user_id>', methods=['GET'])
@jwt_required()
def get_step_recommendation(user_id):
    """Get promotion step recommendation for a user."""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    target_grade = request.args.get('target_grade', type=int)
    
    if not target_grade:
        target_grade = user.conraiss_grade + 1 if user.conraiss_grade else None
    
    if not target_grade:
        return jsonify({'error': 'Cannot determine target grade'}), 400
    
    recommendation = get_promotion_step_recommendation(user, target_grade)
    
    return jsonify(recommendation), 200


@promotion_bp.route('/apply/<int:user_id>', methods=['POST'])
@jwt_required()
def apply_user_promotion(user_id):
    """Apply promotion to a user."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is HR Admin
    if not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Validate required fields
    if 'new_grade' not in data or 'new_step' not in data:
        return jsonify({'error': 'Missing required fields: new_grade, new_step'}), 400
    
    new_grade = data['new_grade']
    new_step = data['new_step']
    effective_date_str = data.get('effective_date')
    notes = data.get('notes')
    
    # Parse effective date
    if effective_date_str:
        try:
            effective_date = date.fromisoformat(effective_date_str)
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    else:
        effective_date = date.today()
    
    # Validate new grade and step
    max_step = get_max_step_for_grade(new_grade)
    if new_step < 1 or new_step > max_step:
        return jsonify({'error': f'Invalid step. Grade {new_grade} has steps 1-{max_step}'}), 400
    
    try:
        updated_user, log = apply_promotion(
            user,
            new_grade,
            new_step,
            effective_date,
            processed_by=current_user_id,
            notes=notes
        )
        
        return jsonify({
            'message': 'Promotion applied successfully',
            'user': updated_user.to_dict(),
            'log': {
                'id': log.id,
                'previous_step': log.previous_step,
                'new_step': log.new_step,
                'increment_date': log.increment_date.isoformat(),
                'increment_type': log.increment_type,
                'notes': log.notes
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@promotion_bp.route('/increment-step/<int:user_id>', methods=['POST'])
@jwt_required()
def increment_step(user_id):
    """Increment user's step (annual increment)."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is HR Admin
    if not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json() or {}
    notes = data.get('notes')
    
    log = increment_user_step(user, processed_by=current_user_id, notes=notes)
    
    if log:
        return jsonify({
            'message': 'Step incremented successfully',
            'user': user.to_dict(),
            'log': {
                'id': log.id,
                'previous_step': log.previous_step,
                'new_step': log.new_step,
                'increment_date': log.increment_date.isoformat(),
                'increment_type': log.increment_type
            }
        }), 200
    else:
        return jsonify({
            'message': 'User is already at maximum step for their grade',
            'user': user.to_dict()
        }), 200


@promotion_bp.route('/step-history/<int:user_id>', methods=['GET'])
@jwt_required()
def get_step_history(user_id):
    """Get step increment history for a user."""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    logs = StepIncrementLog.query.filter_by(user_id=user_id).order_by(
        StepIncrementLog.increment_date.desc()
    ).all()
    
    return jsonify({
        'user_id': user_id,
        'count': len(logs),
        'history': [{
            'id': log.id,
            'previous_step': log.previous_step,
            'new_step': log.new_step,
            'increment_date': log.increment_date.isoformat(),
            'increment_type': log.increment_type,
            'notes': log.notes,
            'processed_by': log.processed_by,
            'created_at': log.created_at.isoformat() if log.created_at else None
        } for log in logs]
    }), 200


@promotion_bp.route('/batch-eligibility-update', methods=['POST'])
@jwt_required()
def batch_eligibility_update():
    """Update eligibility status for all staff."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is HR Admin
    if not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    stats = update_eligibility_status_for_all_staff()
    
    return jsonify({
        'message': 'Eligibility status updated for all staff',
        'statistics': stats
    }), 200


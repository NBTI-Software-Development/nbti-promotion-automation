"""
RRR (Recommendation, Recognition, Reward) Routes
API endpoints for managing RRR allocations and recommendations.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db, User, RRRVacancy, RRRRecommendation
from src.services.rrr_allocation_service import (
    allocate_rrr_for_grade,
    allocate_rrr_for_all_grades,
    generate_rrr_recommendations,
    get_rrr_rankings_for_grade,
    approve_rrr_recommendation,
    reject_rrr_recommendation
)

rrr_bp = Blueprint('rrr', __name__)


@rrr_bp.route('/vacancies', methods=['POST'])
@jwt_required()
def create_or_update_vacancy():
    """Create or update RRR vacancy configuration for a grade."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is HR Admin
    if not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['conraiss_grade', 'promotion_cycle']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    grade = data['conraiss_grade']
    cycle = data['promotion_cycle']
    
    # Check if vacancy already exists
    vacancy = RRRVacancy.query.filter_by(
        conraiss_grade=grade,
        promotion_cycle=cycle
    ).first()
    
    if vacancy:
        # Update existing
        vacancy.promotion_vacancies = data.get('promotion_vacancies', vacancy.promotion_vacancies)
        vacancy.recognition_slots = data.get('recognition_slots', vacancy.recognition_slots)
        vacancy.reward_slots = data.get('reward_slots', vacancy.reward_slots)
        vacancy.is_active = data.get('is_active', vacancy.is_active)
        message = 'Vacancy configuration updated'
    else:
        # Create new
        vacancy = RRRVacancy(
            conraiss_grade=grade,
            promotion_cycle=cycle,
            promotion_vacancies=data.get('promotion_vacancies', 0),
            recognition_slots=data.get('recognition_slots', 0),
            reward_slots=data.get('reward_slots', 0),
            is_active=data.get('is_active', True),
            created_by=current_user_id
        )
        db.session.add(vacancy)
        message = 'Vacancy configuration created'
    
    db.session.commit()
    
    return jsonify({
        'message': message,
        'vacancy': vacancy.to_dict()
    }), 201


@rrr_bp.route('/vacancies/<promotion_cycle>', methods=['GET'])
@jwt_required()
def get_vacancies(promotion_cycle):
    """Get all vacancy configurations for a promotion cycle."""
    vacancies = RRRVacancy.query.filter_by(
        promotion_cycle=promotion_cycle,
        is_active=True
    ).all()
    
    return jsonify({
        'promotion_cycle': promotion_cycle,
        'vacancies': [v.to_dict() for v in vacancies]
    }), 200


@rrr_bp.route('/allocate/<promotion_cycle>', methods=['POST'])
@jwt_required()
def allocate_rrr(promotion_cycle):
    """Trigger RRR allocation for a promotion cycle."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is HR Admin
    if not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json() or {}
    pms_year = data.get('pms_year')
    exam_id = data.get('exam_id')
    
    # Perform allocation for all grades
    allocation_results = allocate_rrr_for_all_grades(promotion_cycle, pms_year, exam_id)
    
    if not allocation_results:
        return jsonify({'error': 'No vacancy configurations found for this cycle'}), 404
    
    # Generate recommendations
    recommendations = generate_rrr_recommendations(
        allocation_results, 
        promotion_cycle,
        recommended_by=current_user_id
    )
    
    # Prepare summary
    summary = {
        'promotion_cycle': promotion_cycle,
        'total_grades_processed': len(allocation_results),
        'total_recommendations': len(recommendations),
        'by_grade': {}
    }
    
    for grade, allocation in allocation_results.items():
        summary['by_grade'][grade] = {
            'total_candidates': allocation['total_candidates'],
            'promoted_count': len(allocation['promoted']),
            'recognized_count': len(allocation['recognized']),
            'rewarded_count': len(allocation['rewarded'])
        }
    
    return jsonify({
        'message': 'RRR allocation completed successfully',
        'summary': summary
    }), 200


@rrr_bp.route('/recommendations/<promotion_cycle>', methods=['GET'])
@jwt_required()
def get_recommendations(promotion_cycle):
    """Get all RRR recommendations for a promotion cycle."""
    grade = request.args.get('grade', type=int)
    status = request.args.get('status')
    
    query = RRRRecommendation.query.filter_by(promotion_cycle=promotion_cycle)
    
    if grade:
        query = query.filter_by(conraiss_grade=grade)
    
    if status:
        query = query.filter_by(status=status)
    
    recommendations = query.order_by(
        RRRRecommendation.conraiss_grade,
        RRRRecommendation.rank_in_grade
    ).all()
    
    return jsonify({
        'promotion_cycle': promotion_cycle,
        'count': len(recommendations),
        'recommendations': [r.to_dict() for r in recommendations]
    }), 200


@rrr_bp.route('/rankings/<int:grade>/<promotion_cycle>', methods=['GET'])
@jwt_required()
def get_rankings(grade, promotion_cycle):
    """Get candidate rankings for a specific grade and cycle."""
    rankings = get_rrr_rankings_for_grade(grade, promotion_cycle)
    
    return jsonify({
        'grade': grade,
        'promotion_cycle': promotion_cycle,
        'count': len(rankings),
        'rankings': rankings
    }), 200


@rrr_bp.route('/recommendations/<int:recommendation_id>/approve', methods=['PUT'])
@jwt_required()
def approve_recommendation(recommendation_id):
    """Approve an RRR recommendation."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is HR Admin or Director
    if not (current_user.has_role('HR Admin') or current_user.has_role('Director')):
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        recommendation = approve_rrr_recommendation(recommendation_id, current_user_id)
        return jsonify({
            'message': 'Recommendation approved successfully',
            'recommendation': recommendation.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@rrr_bp.route('/recommendations/<int:recommendation_id>/reject', methods=['PUT'])
@jwt_required()
def reject_recommendation(recommendation_id):
    """Reject an RRR recommendation."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is HR Admin or Director
    if not (current_user.has_role('HR Admin') or current_user.has_role('Director')):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    rejection_reason = data.get('rejection_reason', 'No reason provided')
    
    try:
        recommendation = reject_rrr_recommendation(recommendation_id, rejection_reason)
        return jsonify({
            'message': 'Recommendation rejected',
            'recommendation': recommendation.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@rrr_bp.route('/dashboard/<promotion_cycle>', methods=['GET'])
@jwt_required()
def get_rrr_dashboard(promotion_cycle):
    """Get RRR dashboard data for a promotion cycle."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Get all recommendations
    recommendations = RRRRecommendation.query.filter_by(
        promotion_cycle=promotion_cycle
    ).all()
    
    # Calculate statistics
    total_candidates = len(recommendations)
    promoted_count = sum(1 for r in recommendations if r.is_promoted)
    recognized_count = sum(1 for r in recommendations if r.is_recognized)
    rewarded_count = sum(1 for r in recommendations if r.is_rewarded)
    
    pending_count = sum(1 for r in recommendations if r.status == 'Pending')
    approved_count = sum(1 for r in recommendations if r.status == 'Approved')
    rejected_count = sum(1 for r in recommendations if r.status == 'Rejected')
    
    # By grade statistics
    by_grade = {}
    for rec in recommendations:
        grade = rec.conraiss_grade
        if grade not in by_grade:
            by_grade[grade] = {
                'total': 0,
                'promoted': 0,
                'recognized': 0,
                'rewarded': 0
            }
        by_grade[grade]['total'] += 1
        if rec.is_promoted:
            by_grade[grade]['promoted'] += 1
        if rec.is_recognized:
            by_grade[grade]['recognized'] += 1
        if rec.is_rewarded:
            by_grade[grade]['rewarded'] += 1
    
    return jsonify({
        'promotion_cycle': promotion_cycle,
        'summary': {
            'total_candidates': total_candidates,
            'promoted': promoted_count,
            'recognized': recognized_count,
            'rewarded': rewarded_count,
            'pending': pending_count,
            'approved': approved_count,
            'rejected': rejected_count
        },
        'by_grade': by_grade
    }), 200


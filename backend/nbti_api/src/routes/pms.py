from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from datetime import datetime
from src.models.user import User, db
from src.models.pms import PMSEvaluation, PMSGoal

pms_bp = Blueprint('pms', __name__)

# Schemas for request validation
class EvaluationSchema(Schema):
    staff_id = fields.Int(required=True)
    quarter = fields.Str(required=True)
    year = fields.Int(required=True)

class GoalSchema(Schema):
    description = fields.Str(required=True)
    target = fields.Str(required=False)
    weight = fields.Float(required=False, missing=1.0)

class RatingSchema(Schema):
    goal_id = fields.Int(required=True)
    rating = fields.Int(required=True, validate=lambda x: 1 <= x <= 5)
    supervisor_comments = fields.Str(required=False)

def require_pms_access(f):
    """Decorator to ensure user has PMS access."""
    def decorated_function(*args, **kwargs):
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user has any PMS-related role
        pms_roles = ['Staff Member', 'Supervisor', 'Head of Department', 'Head of Unit', 
                     'Centre Manager', 'Director', 'HR Admin']
        
        if not any(user.has_role(role) for role in pms_roles):
            return jsonify({'error': 'Insufficient permissions for PMS access'}), 403
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Evaluation Management
@pms_bp.route('/evaluations', methods=['GET'])
@jwt_required()
@require_pms_access
def get_evaluations():
    """Get evaluations based on user role."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    quarter = request.args.get('quarter')
    year = request.args.get('year', type=int)
    status = request.args.get('status')
    
    # Build query based on user role
    if current_user.has_role('HR Admin') or current_user.has_role('Director'):
        # HR Admin and Directors can see all evaluations
        query = PMSEvaluation.query
    elif current_user.has_role('Supervisor') or current_user.has_role('Head of Department') or \
         current_user.has_role('Head of Unit') or current_user.has_role('Centre Manager'):
        # Supervisors can see evaluations they supervise and their own
        query = PMSEvaluation.query.filter(
            (PMSEvaluation.supervisor_id == current_user_id) | 
            (PMSEvaluation.staff_id == current_user_id)
        )
    else:
        # Staff members can only see their own evaluations
        query = PMSEvaluation.query.filter(PMSEvaluation.staff_id == current_user_id)
    
    # Apply filters
    if quarter:
        query = query.filter(PMSEvaluation.quarter == quarter)
    if year:
        query = query.filter(PMSEvaluation.year == year)
    if status:
        query = query.filter(PMSEvaluation.status == status)
    
    evaluations = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'evaluations': [evaluation.to_dict() for evaluation in evaluations.items],
        'total': evaluations.total,
        'pages': evaluations.pages,
        'current_page': page
    }), 200

@pms_bp.route('/evaluations', methods=['POST'])
@jwt_required()
@require_pms_access
def create_evaluation():
    """Create a new evaluation (staff can initiate their own)."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    schema = EvaluationSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    # Check if user can create evaluation for the specified staff
    if data['staff_id'] != current_user_id:
        if not (current_user.has_role('HR Admin') or current_user.has_role('Supervisor')):
            return jsonify({'error': 'Can only create evaluation for yourself'}), 403
    
    # Check if evaluation already exists for this quarter/year
    existing = PMSEvaluation.query.filter_by(
        staff_id=data['staff_id'],
        quarter=data['quarter'],
        year=data['year']
    ).first()
    
    if existing:
        return jsonify({'error': 'Evaluation already exists for this quarter/year'}), 400
    
    # Find supervisor (for now, assume it's provided or use current user if they're creating for someone else)
    staff_member = User.query.get(data['staff_id'])
    if not staff_member:
        return jsonify({'error': 'Staff member not found'}), 404
    
    # For MVP, supervisor_id can be set to current user if they're creating for someone else
    supervisor_id = current_user_id if data['staff_id'] != current_user_id else None
    
    evaluation = PMSEvaluation(
        staff_id=data['staff_id'],
        supervisor_id=supervisor_id,
        quarter=data['quarter'],
        year=data['year'],
        status='Pending'
    )
    
    db.session.add(evaluation)
    db.session.commit()
    
    return jsonify({
        'message': 'Evaluation created successfully',
        'evaluation': evaluation.to_dict()
    }), 201

@pms_bp.route('/evaluations/<int:evaluation_id>', methods=['GET'])
@jwt_required()
@require_pms_access
def get_evaluation(evaluation_id):
    """Get specific evaluation."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    evaluation = PMSEvaluation.query.get_or_404(evaluation_id)
    
    # Check access permissions
    if not (current_user.has_role('HR Admin') or 
            evaluation.staff_id == current_user_id or 
            evaluation.supervisor_id == current_user_id):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    return jsonify({'evaluation': evaluation.to_dict()}), 200

@pms_bp.route('/evaluations/<int:evaluation_id>/assign-supervisor', methods=['POST'])
@jwt_required()
@require_pms_access
def assign_supervisor(evaluation_id):
    """Assign supervisor to evaluation (HR Admin only)."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Only HR Admin can assign supervisors'}), 403
    
    evaluation = PMSEvaluation.query.get_or_404(evaluation_id)
    data = request.json
    supervisor_id = data.get('supervisor_id')
    
    if not supervisor_id:
        return jsonify({'error': 'Supervisor ID is required'}), 400
    
    supervisor = User.query.get(supervisor_id)
    if not supervisor:
        return jsonify({'error': 'Supervisor not found'}), 404
    
    if not supervisor.has_role('Supervisor'):
        return jsonify({'error': 'User is not a supervisor'}), 400
    
    evaluation.supervisor_id = supervisor_id
    db.session.commit()
    
    return jsonify({
        'message': 'Supervisor assigned successfully',
        'evaluation': evaluation.to_dict()
    }), 200

# Goal Management
@pms_bp.route('/evaluations/<int:evaluation_id>/goals', methods=['GET'])
@jwt_required()
@require_pms_access
def get_goals(evaluation_id):
    """Get goals for an evaluation."""
    current_user_id = get_jwt_identity()
    evaluation = PMSEvaluation.query.get_or_404(evaluation_id)
    
    # Check access permissions
    if not (evaluation.staff_id == current_user_id or 
            evaluation.supervisor_id == current_user_id or
            User.query.get(current_user_id).has_role('HR Admin')):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    goals = evaluation.goals.all()
    return jsonify({'goals': [goal.to_dict() for goal in goals]}), 200

@pms_bp.route('/evaluations/<int:evaluation_id>/goals', methods=['POST'])
@jwt_required()
@require_pms_access
def create_goal(evaluation_id):
    """Create a new goal for an evaluation."""
    current_user_id = get_jwt_identity()
    evaluation = PMSEvaluation.query.get_or_404(evaluation_id)
    
    # Check if user can add goals (staff member or supervisor)
    if not (evaluation.staff_id == current_user_id or 
            evaluation.supervisor_id == current_user_id or
            User.query.get(current_user_id).has_role('HR Admin')):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    schema = GoalSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    goal = PMSGoal(
        evaluation_id=evaluation_id,
        description=data['description'],
        target=data.get('target'),
        weight=data.get('weight', 1.0)
    )
    
    db.session.add(goal)
    
    # Update evaluation status
    if evaluation.status == 'Pending':
        evaluation.status = 'In Progress'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Goal created successfully',
        'goal': goal.to_dict()
    }), 201

@pms_bp.route('/goals/<int:goal_id>/agree', methods=['POST'])
@jwt_required()
@require_pms_access
def agree_goal(goal_id):
    """Mark goal as agreed upon."""
    current_user_id = get_jwt_identity()
    goal = PMSGoal.query.get_or_404(goal_id)
    evaluation = goal.evaluation
    
    # Both staff and supervisor can agree on goals
    if not (evaluation.staff_id == current_user_id or 
            evaluation.supervisor_id == current_user_id):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    goal.agreed = True
    db.session.commit()
    
    return jsonify({
        'message': 'Goal agreed upon successfully',
        'goal': goal.to_dict()
    }), 200

# Rating and Evaluation
@pms_bp.route('/goals/<int:goal_id>/rate', methods=['POST'])
@jwt_required()
@require_pms_access
def rate_goal(goal_id):
    """Rate a goal (supervisor only)."""
    current_user_id = get_jwt_identity()
    goal = PMSGoal.query.get_or_404(goal_id)
    evaluation = goal.evaluation
    
    # Only supervisor can rate goals
    if evaluation.supervisor_id != current_user_id:
        return jsonify({'error': 'Only the assigned supervisor can rate goals'}), 403
    
    schema = RatingSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    goal.rating = data['rating']
    goal.supervisor_comments = data.get('supervisor_comments')
    
    db.session.commit()
    
    return jsonify({
        'message': 'Goal rated successfully',
        'goal': goal.to_dict()
    }), 200

@pms_bp.route('/evaluations/<int:evaluation_id>/finalize', methods=['POST'])
@jwt_required()
@require_pms_access
def finalize_evaluation(evaluation_id):
    """Finalize evaluation and calculate final score."""
    current_user_id = get_jwt_identity()
    evaluation = PMSEvaluation.query.get_or_404(evaluation_id)
    
    # Only supervisor can finalize evaluation
    if evaluation.supervisor_id != current_user_id:
        return jsonify({'error': 'Only the assigned supervisor can finalize evaluation'}), 403
    
    # Check if all goals have been rated
    unrated_goals = [goal for goal in evaluation.goals if goal.rating is None]
    if unrated_goals:
        return jsonify({
            'error': 'Cannot finalize evaluation. Some goals are not rated yet.',
            'unrated_goals': len(unrated_goals)
        }), 400
    
    # Calculate final score
    final_score = evaluation.calculate_final_score()
    evaluation.status = 'Completed'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Evaluation finalized successfully',
        'evaluation': evaluation.to_dict(),
        'final_score': final_score
    }), 200

# Dashboard and Statistics
@pms_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@require_pms_access
def get_dashboard():
    """Get PMS dashboard data for current user."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    dashboard_data = {
        'user_info': current_user.to_dict(),
        'stats': {}
    }
    
    if current_user.has_role('Staff Member'):
        # Staff member dashboard
        my_evaluations = PMSEvaluation.query.filter_by(staff_id=current_user_id).all()
        dashboard_data['stats'] = {
            'total_evaluations': len(my_evaluations),
            'pending_evaluations': len([e for e in my_evaluations if e.status == 'Pending']),
            'in_progress_evaluations': len([e for e in my_evaluations if e.status == 'In Progress']),
            'completed_evaluations': len([e for e in my_evaluations if e.status == 'Completed']),
            'recent_evaluations': [e.to_dict() for e in my_evaluations[-3:]]
        }
    
    if current_user.has_role('Supervisor'):
        # Supervisor dashboard
        supervised_evaluations = PMSEvaluation.query.filter_by(supervisor_id=current_user_id).all()
        dashboard_data['stats'].update({
            'supervised_evaluations': len(supervised_evaluations),
            'pending_reviews': len([e for e in supervised_evaluations if e.status == 'In Progress']),
            'completed_reviews': len([e for e in supervised_evaluations if e.status == 'Completed']),
            'recent_supervised': [e.to_dict() for e in supervised_evaluations[-3:]]
        })
    
    if current_user.has_role('HR Admin'):
        # HR Admin dashboard
        all_evaluations = PMSEvaluation.query.all()
        dashboard_data['stats'].update({
            'total_system_evaluations': len(all_evaluations),
            'system_pending': len([e for e in all_evaluations if e.status == 'Pending']),
            'system_in_progress': len([e for e in all_evaluations if e.status == 'In Progress']),
            'system_completed': len([e for e in all_evaluations if e.status == 'Completed'])
        })
    
    return jsonify(dashboard_data), 200

# Staff Comments
@pms_bp.route('/goals/<int:goal_id>/comment', methods=['POST'])
@jwt_required()
@require_pms_access
def add_staff_comment(goal_id):
    """Add staff comment to a goal."""
    current_user_id = get_jwt_identity()
    goal = PMSGoal.query.get_or_404(goal_id)
    evaluation = goal.evaluation
    
    # Only staff member can add their own comments
    if evaluation.staff_id != current_user_id:
        return jsonify({'error': 'Can only comment on your own goals'}), 403
    
    data = request.json
    comment = data.get('comment')
    
    if not comment:
        return jsonify({'error': 'Comment is required'}), 400
    
    goal.staff_comments = comment
    db.session.commit()
    
    return jsonify({
        'message': 'Comment added successfully',
        'goal': goal.to_dict()
    }), 200


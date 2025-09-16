from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from src.models.user import User, Role, db

user_bp = Blueprint('user', __name__)

# Schemas for request validation
class UserUpdateSchema(Schema):
    username = fields.Str(required=False)
    email = fields.Email(required=False)
    first_name = fields.Str(required=False)
    last_name = fields.Str(required=False)
    employee_id = fields.Str(required=False)
    department = fields.Str(required=False)
    position = fields.Str(required=False)
    is_active = fields.Bool(required=False)

class RoleSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(required=False)

def require_role(role_name):
    """Decorator to require specific role."""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            current_user_id = int(get_jwt_identity())
            user = User.query.get(current_user_id)
            
            if not user or not user.has_role(role_name):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

# User management endpoints
@user_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (admin only)."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    if not current_user.has_role('HR Admin') and not current_user.has_role('Director'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    users = User.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'users': [user.to_dict() for user in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': page
    }), 200

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get specific user."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    # Users can view their own profile, admins can view any profile
    if current_user_id != user_id and not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify({'user': user.to_dict()}), 200

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user information."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    # Users can update their own profile, admins can update any profile
    if current_user_id != user_id and not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    user = User.query.get_or_404(user_id)
    
    schema = UserUpdateSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    # Check for unique constraints
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
    
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
    
    # Update user fields
    for field, value in data.items():
        setattr(user, field, value)
    
    db.session.commit()
    return jsonify({'user': user.to_dict()}), 200

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete user (admin only)."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    if not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    if current_user_id == user_id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200

# Role management endpoints
@user_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_roles():
    """Get all roles."""
    roles = Role.query.all()
    return jsonify({'roles': [role.to_dict() for role in roles]}), 200

@user_bp.route('/roles', methods=['POST'])
@jwt_required()
def create_role():
    """Create new role (admin only)."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    if not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    schema = RoleSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    if Role.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Role already exists'}), 400
    
    role = Role(
        name=data['name'],
        description=data.get('description')
    )
    
    db.session.add(role)
    db.session.commit()
    
    return jsonify({'role': role.to_dict()}), 201

@user_bp.route('/users/<int:user_id>/roles', methods=['POST'])
@jwt_required()
def assign_role_to_user(user_id):
    """Assign role to user (admin only)."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    if not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.json
    role_id = data.get('role_id')
    
    if not role_id:
        return jsonify({'error': 'Role ID is required'}), 400
    
    role = Role.query.get_or_404(role_id)
    user.add_role(role)
    db.session.commit()
    
    return jsonify({'message': f'Role {role.name} assigned to user {user.username}'}), 200

@user_bp.route('/users/<int:user_id>/roles/<int:role_id>', methods=['DELETE'])
@jwt_required()
def remove_role_from_user(user_id, role_id):
    """Remove role from user (admin only)."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    if not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    user = User.query.get_or_404(user_id)
    role = Role.query.get_or_404(role_id)
    
    user.remove_role(role)
    db.session.commit()
    
    return jsonify({'message': f'Role {role.name} removed from user {user.username}'}), 200

# Initialize default roles
@user_bp.route('/init-roles', methods=['POST'])
@jwt_required()
def initialize_default_roles():
    """Initialize default roles (admin only)."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    if not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    default_roles = [
        {'name': 'Staff Member', 'description': 'Regular staff member'},
        {'name': 'Supervisor', 'description': 'Direct line manager/rater'},
        {'name': 'Head of Department', 'description': 'Department head'},
        {'name': 'Head of Unit', 'description': 'Unit head'},
        {'name': 'Centre Manager', 'description': 'Technology Incubation Centre manager'},
        {'name': 'Director', 'description': 'Directorate director'},
        {'name': 'HR Admin', 'description': 'Human Resource administrator'},
        {'name': 'Exam Administrator', 'description': 'Exam management administrator'},
        {'name': 'Question Author', 'description': 'Subject matter expert for questions'},
        {'name': 'Grader', 'description': 'Manual/AI reviewer for exams'}
    ]
    
    created_roles = []
    for role_data in default_roles:
        if not Role.query.filter_by(name=role_data['name']).first():
            role = Role(name=role_data['name'], description=role_data['description'])
            db.session.add(role)
            created_roles.append(role_data['name'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Default roles initialized',
        'created_roles': created_roles
    }), 200


"""
Import/Export Routes
API endpoints for bulk import and export operations.
"""

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import User
from src.services.user_import_service import import_users_from_csv, get_csv_template

import_export_bp = Blueprint('import_export', __name__)


@import_export_bp.route('/users/template', methods=['GET'])
@jwt_required()
def download_csv_template():
    """Download CSV template for user import."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is HR Admin
    if not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    template = get_csv_template()
    
    return Response(
        template,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=user_import_template.csv'}
    )


@import_export_bp.route('/users/import', methods=['POST'])
@jwt_required()
def import_users():
    """Import users from CSV file."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is HR Admin
    if not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if file is provided
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV file'}), 400
    
    # Import users
    result = import_users_from_csv(file, current_user_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@import_export_bp.route('/users/export', methods=['GET'])
@jwt_required()
def export_users():
    """Export all users to CSV."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is HR Admin
    if not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get all users
    users = User.query.filter_by(is_active=True).all()
    
    # Generate CSV
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'employee_id', 'first_name', 'last_name', 'email', 'department',
        'position', 'rank', 'cadre', 'ippis_number', 'date_of_birth',
        'state_of_origin', 'local_government_area', 'file_no',
        'confirmation_date', 'qualifications', 'conraiss_grade',
        'conraiss_step', 'date_of_hire', 'phone_number', 'office_location',
        'supervisor_employee_id'
    ])
    
    # Write data
    for user in users:
        supervisor_employee_id = ''
        if user.supervisor_id:
            supervisor = User.query.get(user.supervisor_id)
            if supervisor:
                supervisor_employee_id = supervisor.employee_id
        
        writer.writerow([
            user.employee_id or '',
            user.first_name or '',
            user.last_name or '',
            user.email or '',
            user.department or '',
            user.position or '',
            user.rank or '',
            user.cadre or '',
            user.ippis_number or '',
            user.date_of_birth.isoformat() if user.date_of_birth else '',
            user.state_of_origin or '',
            user.local_government_area or '',
            user.file_no or '',
            user.confirmation_date.isoformat() if user.confirmation_date else '',
            user.qualifications or '',
            user.conraiss_grade or '',
            user.conraiss_step or '',
            user.date_of_first_appointment.isoformat() if user.date_of_first_appointment else '',
            user.phone_number or '',
            user.office_location or '',
            supervisor_employee_id
        ])
    
    # Get CSV content
    csv_content = output.getvalue()
    output.close()
    
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=users_export.csv'}
    )


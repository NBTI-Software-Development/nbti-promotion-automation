"""
Audit and File Management Routes
API endpoints for audit logs and file uploads.
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from src.models import User
from src.services.audit_service import (
    get_audit_logs,
    get_entity_history,
    get_user_activity
)
from src.services.s3_service import (
    s3_service,
    upload_pms_evidence,
    upload_appeal_document,
    upload_user_document
)

audit_bp = Blueprint('audit', __name__)


@audit_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_logs():
    """Get audit logs with filters."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is HR Admin or Director
    if not (current_user.has_role('HR Admin') or current_user.has_role('Director')):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Parse query parameters
    user_id = request.args.get('user_id', type=int)
    action_type = request.args.get('action_type')
    entity_type = request.args.get('entity_type')
    entity_id = request.args.get('entity_id', type=int)
    is_sensitive = request.args.get('is_sensitive', type=lambda x: x.lower() == 'true')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    limit = request.args.get('limit', 100, type=int)
    
    # Parse dates
    start_date = None
    end_date = None
    
    if start_date_str:
        try:
            start_date = datetime.fromisoformat(start_date_str)
        except ValueError:
            return jsonify({'error': 'Invalid start_date format. Use ISO format.'}), 400
    
    if end_date_str:
        try:
            end_date = datetime.fromisoformat(end_date_str)
        except ValueError:
            return jsonify({'error': 'Invalid end_date format. Use ISO format.'}), 400
    
    # Get logs
    logs = get_audit_logs(
        user_id=user_id,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        is_sensitive=is_sensitive,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    
    return jsonify({
        'count': len(logs),
        'logs': [log.to_dict() for log in logs]
    }), 200


@audit_bp.route('/entity-history/<entity_type>/<int:entity_id>', methods=['GET'])
@jwt_required()
def get_entity_audit_history(entity_type, entity_id):
    """Get complete audit history for an entity."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is HR Admin or Director
    if not (current_user.has_role('HR Admin') or current_user.has_role('Director')):
        return jsonify({'error': 'Unauthorized'}), 403
    
    logs = get_entity_history(entity_type, entity_id)
    
    return jsonify({
        'entity_type': entity_type,
        'entity_id': entity_id,
        'count': len(logs),
        'history': [log.to_dict() for log in logs]
    }), 200


@audit_bp.route('/user-activity/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_audit_activity(user_id):
    """Get recent activity for a user."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Users can view their own activity, or HR Admin/Director can view anyone's
    if current_user_id != user_id and not (current_user.has_role('HR Admin') or current_user.has_role('Director')):
        return jsonify({'error': 'Unauthorized'}), 403
    
    days = request.args.get('days', 30, type=int)
    
    logs = get_user_activity(user_id, days)
    
    return jsonify({
        'user_id': user_id,
        'days': days,
        'count': len(logs),
        'activity': [log.to_dict() for log in logs]
    }), 200


@audit_bp.route('/upload/pms-evidence/<int:evaluation_id>', methods=['POST'])
@jwt_required()
def upload_pms_evidence_file(evaluation_id):
    """Upload PMS evidence file."""
    current_user_id = get_jwt_identity()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Upload to S3
    s3_key = upload_pms_evidence(file, evaluation_id, file.filename)
    
    if s3_key:
        # Get presigned URL
        url = s3_service.get_file_url(s3_key)
        
        return jsonify({
            'message': 'File uploaded successfully',
            's3_key': s3_key,
            'url': url
        }), 200
    else:
        return jsonify({'error': 'File upload failed'}), 500


@audit_bp.route('/upload/appeal-document/<int:appeal_id>', methods=['POST'])
@jwt_required()
def upload_appeal_document_file(appeal_id):
    """Upload appeal supporting document."""
    current_user_id = get_jwt_identity()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Upload to S3
    s3_key = upload_appeal_document(file, appeal_id, file.filename)
    
    if s3_key:
        url = s3_service.get_file_url(s3_key)
        
        return jsonify({
            'message': 'File uploaded successfully',
            's3_key': s3_key,
            'url': url
        }), 200
    else:
        return jsonify({'error': 'File upload failed'}), 500


@audit_bp.route('/upload/user-document/<int:user_id>/<doc_type>', methods=['POST'])
@jwt_required()
def upload_user_document_file(user_id, doc_type):
    """Upload user document (qualification, certificate, etc.)."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Users can upload their own documents, or HR Admin can upload for anyone
    if current_user_id != user_id and not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Upload to S3
    s3_key = upload_user_document(file, user_id, doc_type, file.filename)
    
    if s3_key:
        url = s3_service.get_file_url(s3_key)
        
        return jsonify({
            'message': 'File uploaded successfully',
            's3_key': s3_key,
            'url': url
        }), 200
    else:
        return jsonify({'error': 'File upload failed'}), 500


@audit_bp.route('/download/<path:s3_key>', methods=['GET'])
@jwt_required()
def download_file(s3_key):
    """Get presigned URL for downloading a file."""
    current_user_id = get_jwt_identity()
    
    # Check if file exists
    if not s3_service.file_exists(s3_key):
        return jsonify({'error': 'File not found'}), 404
    
    # Generate presigned URL
    url = s3_service.get_file_url(s3_key)
    
    if url:
        return jsonify({
            's3_key': s3_key,
            'download_url': url,
            'expires_in': 3600  # 1 hour
        }), 200
    else:
        return jsonify({'error': 'Failed to generate download URL'}), 500


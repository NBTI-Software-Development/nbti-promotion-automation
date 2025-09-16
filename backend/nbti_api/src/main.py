import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

# Import security module
from src.security import init_security, SecurityMiddleware

# Import all models to ensure they are registered
from src.models.user import db, User, Role
from src.models.pms import PMSEvaluation, PMSGoal
from src.models.emm import EMMQuestion, EMMOption, EMMExam, EMMExamSubmission, EMMSubmissionAnswer

# Import blueprints
from src.routes.auth import auth_bp
from src.routes.user import user_bp
from src.routes.pms import pms_bp
from src.routes.emm import emm_bp

def create_app():
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
        seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    )
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(
        seconds=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000))
    )
    
    # Security configuration
    app.config['SECURITY_HEADERS_ENABLED'] = os.getenv('SECURITY_HEADERS_ENABLED', 'True').lower() == 'true'
    app.config['CONTENT_SECURITY_POLICY'] = os.getenv('CONTENT_SECURITY_POLICY')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))
    app.config['LOG_LEVEL'] = os.getenv('LOG_LEVEL', 'INFO')
    app.config['LOG_FILE'] = os.getenv('LOG_FILE')
    
    # Database configuration
    database_url = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    
    # CORS configuration with environment-specific origins
    cors_origins = os.getenv('CORS_ORIGINS', '*').split(',')
    CORS(app, origins=cors_origins)
    
    # Initialize security
    init_security(app)
    SecurityMiddleware(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(pms_bp, url_prefix='/api/pms')
    app.register_blueprint(emm_bp, url_prefix='/api/emm')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'NBTI Promotion Automation API is running',
            'version': '1.0.0'
        }), 200
    
    # API documentation endpoint
    @app.route('/api/docs', methods=['GET'])
    def api_docs():
        return jsonify({
            'title': 'NBTI Promotion Automation API',
            'version': '1.0.0',
            'description': 'API for Performance Management System and Exam Management Module',
            'endpoints': {
                'authentication': {
                    'POST /api/auth/register': 'Register a new user',
                    'POST /api/auth/login': 'Login user',
                    'POST /api/auth/refresh': 'Refresh access token',
                    'POST /api/auth/logout': 'Logout user',
                    'GET /api/auth/me': 'Get current user info',
                    'POST /api/auth/change-password': 'Change password'
                },
                'user_management': {
                    'GET /api/users': 'Get all users (admin)',
                    'GET /api/users/{id}': 'Get specific user',
                    'PUT /api/users/{id}': 'Update user',
                    'DELETE /api/users/{id}': 'Delete user (admin)',
                    'GET /api/roles': 'Get all roles',
                    'POST /api/roles': 'Create role (admin)',
                    'POST /api/users/{id}/roles': 'Assign role to user (admin)',
                    'DELETE /api/users/{id}/roles/{role_id}': 'Remove role from user (admin)',
                    'POST /api/init-roles': 'Initialize default roles (admin)'
                },
                'pms': {
                    'GET /api/pms/evaluations': 'Get evaluations based on user role',
                    'POST /api/pms/evaluations': 'Create new evaluation',
                    'GET /api/pms/evaluations/{id}': 'Get specific evaluation',
                    'POST /api/pms/evaluations/{id}/assign-supervisor': 'Assign supervisor (admin)',
                    'GET /api/pms/evaluations/{id}/goals': 'Get goals for evaluation',
                    'POST /api/pms/evaluations/{id}/goals': 'Create goal for evaluation',
                    'POST /api/pms/goals/{id}/agree': 'Mark goal as agreed',
                    'POST /api/pms/goals/{id}/rate': 'Rate goal (supervisor)',
                    'POST /api/pms/goals/{id}/comment': 'Add staff comment to goal',
                    'POST /api/pms/evaluations/{id}/finalize': 'Finalize evaluation',
                    'GET /api/pms/dashboard': 'Get PMS dashboard data'
                },
                'emm': {
                    'GET /api/emm/questions': 'Get questions from question bank',
                    'POST /api/emm/questions': 'Create new question (authors/admins)',
                    'GET /api/emm/questions/{id}': 'Get specific question',
                    'PUT /api/emm/questions/{id}': 'Update question',
                    'GET /api/emm/exams': 'Get exams based on user role',
                    'POST /api/emm/exams': 'Create new exam (admins)',
                    'GET /api/emm/exams/{id}': 'Get specific exam',
                    'POST /api/emm/exams/{id}/start': 'Start taking an exam',
                    'POST /api/emm/submissions/{id}/answer': 'Submit answer for question',
                    'POST /api/emm/submissions/{id}/submit': 'Submit entire exam',
                    'GET /api/emm/submissions': 'Get exam submissions',
                    'GET /api/emm/submissions/{id}': 'Get specific submission',
                    'GET /api/emm/dashboard': 'Get EMM dashboard data',
                    'GET /api/emm/integration/promotion-scores': 'Get promotion scores (admin)'
                },
                'health': {
                    'GET /api/health': 'Health check',
                    'GET /api/docs': 'API documentation'
                }
            }
        }), 200
    
    # Create tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if it doesn't exist
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@nbti.gov.ng',
                first_name='System',
                last_name='Administrator'
            )
            admin_user.set_password('admin123')
            
            # Create HR Admin role if it doesn't exist
            hr_admin_role = Role.query.filter_by(name='HR Admin').first()
            if not hr_admin_role:
                hr_admin_role = Role(name='HR Admin', description='Human Resource administrator')
                db.session.add(hr_admin_role)
                db.session.flush()  # Flush to get the ID
            
            admin_user.add_role(hr_admin_role)
            db.session.add(admin_user)
            db.session.commit()
            
            print("Default admin user created: username='admin', password='admin123'")
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return "index.html not found", 404
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


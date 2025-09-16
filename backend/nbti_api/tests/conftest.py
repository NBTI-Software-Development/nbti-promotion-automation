import pytest
import tempfile
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta

from models.user import db, User, Role
from models.pms import PMSEvaluation, PMSGoal
from models.emm import EMMExam, EMMQuestion, EMMExamSubmission
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta


def create_test_app(config=None):
    """Create and configure a test app instance."""
    app = Flask(__name__)
    
    # Test configuration
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-secret-key',
        'SECRET_KEY': 'test-secret-key',
        'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=1),
        'JWT_REFRESH_TOKEN_EXPIRES': timedelta(days=30)
    })
    
    if config:
        app.config.update(config)
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app)
    
    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.pms import pms_bp
    from routes.emm import emm_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(pms_bp, url_prefix='/api/pms')
    app.register_blueprint(emm_bp, url_prefix='/api/emm')
    
    return app


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_test_app()
    
    with app.app_context():
        db.create_all()
        
        # Create default roles
        roles = [
            Role(name='Staff Member', description='Regular staff member'),
            Role(name='Supervisor', description='Team supervisor'),
            Role(name='HR Admin', description='HR administrator'),
            Role(name='Director', description='Department director'),
            Role(name='Exam Administrator', description='Exam administrator'),
            Role(name='Question Author', description='Question author'),
        ]
        
        for role in roles:
            db.session.add(role)
        
        db.session.commit()
    
    yield app
    
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client, app):
    """Create authentication headers for testing."""
    with app.app_context():
        # Create a test user
        staff_role = Role.query.filter_by(name='Staff Member').first()
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password_hash=generate_password_hash('testpass123')
        )
        user.roles.append(staff_role)
        db.session.add(user)
        db.session.commit()
        
        # Login to get token
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        token = response.json['access_token']
        return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def admin_headers(client, app):
    """Create admin authentication headers for testing."""
    with app.app_context():
        # Create an admin user
        admin_role = Role.query.filter_by(name='HR Admin').first()
        admin = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password_hash=generate_password_hash('adminpass123')
        )
        admin.roles.append(admin_role)
        db.session.add(admin)
        db.session.commit()
        
        # Login to get token
        response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'adminpass123'
        })
        
        token = response.json['access_token']
        return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def sample_user(app):
    """Create a sample user for testing."""
    with app.app_context():
        staff_role = Role.query.filter_by(name='Staff Member').first()
        user = User(
            username='sampleuser',
            email='sample@example.com',
            first_name='Sample',
            last_name='User',
            password_hash=generate_password_hash('samplepass123')
        )
        user.roles.append(staff_role)
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def sample_evaluation(app, sample_user):
    """Create a sample evaluation for testing."""
    with app.app_context():
        evaluation = PMSEvaluation(
            staff_id=sample_user.id,
            supervisor_id=sample_user.id,  # Using same user for simplicity
            quarter='Q1',
            year=2024,
            status='In Progress'
        )
        db.session.add(evaluation)
        db.session.commit()
        return evaluation


@pytest.fixture
def sample_goal(app, sample_evaluation):
    """Create a sample goal for testing."""
    with app.app_context():
        goal = PMSGoal(
            evaluation_id=sample_evaluation.id,
            description='Complete project documentation',
            target='Finish all documentation by end of quarter',
            weight=1.0,
            agreed=True
        )
        db.session.add(goal)
        db.session.commit()
        return goal


@pytest.fixture
def sample_exam(app):
    """Create a sample exam for testing."""
    with app.app_context():
        exam = EMMExam(
            title='Python Programming Test',
            description='Test your Python programming skills',
            duration=60,
            passing_score=70.0,
            status='Active',
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(exam)
        db.session.commit()
        return exam


@pytest.fixture
def sample_question(app, sample_exam):
    """Create a sample question for testing."""
    with app.app_context():
        # Get a user to be the creator
        user = User.query.first()
        if not user:
            staff_role = Role.query.filter_by(name='Staff Member').first()
            user = User(
                username='questioncreator',
                email='creator@example.com',
                first_name='Question',
                last_name='Creator',
                password_hash=generate_password_hash('password123')
            )
            user.roles.append(staff_role)
            db.session.add(user)
            db.session.commit()
            
        question = EMMQuestion(
            question_text='What is the output of print("Hello World")?',
            question_type='MCQ',
            subject='Python',
            difficulty='Easy',
            points=10,
            created_by=user.id
        )
        db.session.add(question)
        db.session.commit()
        
        # Add the question to the exam
        sample_exam.questions.append(question)
        db.session.commit()
        
        return question


@pytest.fixture
def sample_submission(app, sample_exam, sample_user):
    """Create a sample submission for testing."""
    with app.app_context():
        submission = EMMExamSubmission(
            exam_id=sample_exam.id,
            user_id=sample_user.id,
            started_at=datetime.utcnow(),
            status='In Progress'
        )
        db.session.add(submission)
        db.session.commit()
        return submission


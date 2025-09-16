from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from datetime import datetime, timedelta
from src.models.user import User, db
from src.models.emm import EMMQuestion, EMMOption, EMMExam, EMMExamSubmission, EMMSubmissionAnswer

emm_bp = Blueprint('emm', __name__)

# Schemas for request validation
class QuestionSchema(Schema):
    question_text = fields.Str(required=True)
    question_type = fields.Str(required=True, validate=lambda x: x in ['MCQ', 'Essay'])
    subject = fields.Str(required=False)
    difficulty = fields.Str(required=False, validate=lambda x: x in ['Easy', 'Medium', 'Hard'])
    points = fields.Int(required=False, missing=1)

class OptionSchema(Schema):
    option_text = fields.Str(required=True)
    is_correct = fields.Bool(required=True)

class ExamSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=False)
    time_limit = fields.Int(required=True)
    passing_score = fields.Float(required=False, missing=60.0)
    start_time = fields.DateTime(required=False)
    end_time = fields.DateTime(required=False)
    question_ids = fields.List(fields.Int(), required=True)

class SubmissionAnswerSchema(Schema):
    question_id = fields.Int(required=True)
    selected_option_id = fields.Int(required=False)
    text_answer = fields.Str(required=False)

def require_emm_access(f):
    """Decorator to ensure user has EMM access."""
    def decorated_function(*args, **kwargs):
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user has any EMM-related role
        emm_roles = ['Exam Administrator', 'Question Author', 'Grader', 'HR Admin', 'Staff Member']
        
        if not any(user.has_role(role) for role in emm_roles):
            return jsonify({'error': 'Insufficient permissions for EMM access'}), 403
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Question Bank Management
@emm_bp.route('/questions', methods=['GET'])
@jwt_required()
@require_emm_access
def get_questions():
    """Get questions from the question bank."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    subject = request.args.get('subject')
    difficulty = request.args.get('difficulty')
    question_type = request.args.get('question_type')
    
    # Build query
    query = EMMQuestion.query.filter_by(is_active=True)
    
    if subject:
        query = query.filter(EMMQuestion.subject == subject)
    if difficulty:
        query = query.filter(EMMQuestion.difficulty == difficulty)
    if question_type:
        query = query.filter(EMMQuestion.question_type == question_type)
    
    questions = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Include correct answers only for authorized users
    include_answers = current_user.has_role('Question Author') or current_user.has_role('Exam Administrator')
    
    return jsonify({
        'questions': [question.to_dict(include_options=True) for question in questions.items],
        'total': questions.total,
        'pages': questions.pages,
        'current_page': page
    }), 200

@emm_bp.route('/questions', methods=['POST'])
@jwt_required()
@require_emm_access
def create_question():
    """Create a new question (Question Authors and Exam Administrators only)."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    if not (current_user.has_role('Question Author') or current_user.has_role('Exam Administrator')):
        return jsonify({'error': 'Only Question Authors and Exam Administrators can create questions'}), 403
    
    schema = QuestionSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    question = EMMQuestion(
        question_text=data['question_text'],
        question_type=data['question_type'],
        subject=data.get('subject'),
        difficulty=data.get('difficulty'),
        points=data.get('points', 1),
        created_by=current_user_id
    )
    
    db.session.add(question)
    db.session.flush()  # Get the question ID
    
    # Add options for MCQ questions
    if data['question_type'] == 'MCQ':
        options_data = request.json.get('options', [])
        if not options_data:
            return jsonify({'error': 'MCQ questions must have options'}), 400
        
        correct_count = 0
        for option_data in options_data:
            option_schema = OptionSchema()
            try:
                option_validated = option_schema.load(option_data)
            except ValidationError as err:
                return jsonify({'error': 'Option validation error', 'messages': err.messages}), 400
            
            option = EMMOption(
                question_id=question.id,
                option_text=option_validated['option_text'],
                is_correct=option_validated['is_correct']
            )
            db.session.add(option)
            
            if option_validated['is_correct']:
                correct_count += 1
        
        if correct_count == 0:
            return jsonify({'error': 'MCQ questions must have at least one correct answer'}), 400
    
    db.session.commit()
    
    return jsonify({
        'message': 'Question created successfully',
        'question': question.to_dict()
    }), 201

@emm_bp.route('/questions/<int:question_id>', methods=['GET'])
@jwt_required()
@require_emm_access
def get_question(question_id):
    """Get specific question."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    question = EMMQuestion.query.get_or_404(question_id)
    
    # Include correct answers only for authorized users
    include_answers = current_user.has_role('Question Author') or current_user.has_role('Exam Administrator')
    
    return jsonify({'question': question.to_dict(include_options=True)}), 200

@emm_bp.route('/questions/<int:question_id>', methods=['PUT'])
@jwt_required()
@require_emm_access
def update_question(question_id):
    """Update question (creators and admins only)."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    question = EMMQuestion.query.get_or_404(question_id)
    
    # Check permissions
    if not (current_user.has_role('Exam Administrator') or question.created_by == current_user_id):
        return jsonify({'error': 'Can only edit your own questions or admin access required'}), 403
    
    schema = QuestionSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    # Update question fields
    question.question_text = data['question_text']
    question.question_type = data['question_type']
    question.subject = data.get('subject')
    question.difficulty = data.get('difficulty')
    question.points = data.get('points', 1)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Question updated successfully',
        'question': question.to_dict()
    }), 200

# Exam Management
@emm_bp.route('/exams', methods=['GET'])
@jwt_required()
@require_emm_access
def get_exams():
    """Get exams based on user role."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    is_active = request.args.get('is_active', type=bool)
    
    # Build query based on user role
    if current_user.has_role('Exam Administrator') or current_user.has_role('HR Admin'):
        # Admins can see all exams
        query = EMMExam.query
    else:
        # Regular users can only see active exams
        query = EMMExam.query.filter_by(is_active=True)
    
    if is_active is not None:
        query = query.filter(EMMExam.is_active == is_active)
    
    exams = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'exams': [exam.to_dict() for exam in exams.items],
        'total': exams.total,
        'pages': exams.pages,
        'current_page': page
    }), 200

@emm_bp.route('/exams', methods=['POST'])
@jwt_required()
@require_emm_access
def create_exam():
    """Create a new exam (Exam Administrators only)."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    if not current_user.has_role('Exam Administrator'):
        return jsonify({'error': 'Only Exam Administrators can create exams'}), 403
    
    schema = ExamSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    # Validate questions exist
    questions = EMMQuestion.query.filter(EMMQuestion.id.in_(data['question_ids'])).all()
    if len(questions) != len(data['question_ids']):
        return jsonify({'error': 'Some questions not found'}), 400
    
    exam = EMMExam(
        title=data['title'],
        description=data.get('description'),
        time_limit=data['time_limit'],
        passing_score=data.get('passing_score', 60.0),
        start_time=data.get('start_time'),
        end_time=data.get('end_time'),
        created_by=current_user_id
    )
    
    # Add questions to exam
    exam.questions = questions
    exam.calculate_total_points()
    
    db.session.add(exam)
    db.session.commit()
    
    return jsonify({
        'message': 'Exam created successfully',
        'exam': exam.to_dict()
    }), 201

@emm_bp.route('/exams/<int:exam_id>', methods=['GET'])
@jwt_required()
@require_emm_access
def get_exam(exam_id):
    """Get specific exam."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    exam = EMMExam.query.get_or_404(exam_id)
    
    # Check if user can access this exam
    if not exam.is_active and not current_user.has_role('Exam Administrator'):
        return jsonify({'error': 'Exam not available'}), 403
    
    # Include questions for admins or during exam taking
    include_questions = current_user.has_role('Exam Administrator') or current_user.has_role('Question Author')
    
    return jsonify({'exam': exam.to_dict(include_questions=include_questions)}), 200

# Exam Taking
@emm_bp.route('/exams/<int:exam_id>/start', methods=['POST'])
@jwt_required()
@require_emm_access
def start_exam(exam_id):
    """Start taking an exam."""
    current_user_id = int(get_jwt_identity())
    exam = EMMExam.query.get_or_404(exam_id)
    
    # Check if exam is available
    if not exam.is_active:
        return jsonify({'error': 'Exam is not active'}), 400
    
    # Check time window
    now = datetime.utcnow()
    if exam.start_time and now < exam.start_time:
        return jsonify({'error': 'Exam has not started yet'}), 400
    
    if exam.end_time and now > exam.end_time:
        return jsonify({'error': 'Exam has ended'}), 400
    
    # Check if user already has a submission
    existing_submission = EMMExamSubmission.query.filter_by(
        exam_id=exam_id,
        candidate_id=current_user_id
    ).first()
    
    if existing_submission:
        if existing_submission.status == 'Completed':
            return jsonify({'error': 'You have already completed this exam'}), 400
        else:
            # Return existing submission
            return jsonify({
                'message': 'Resuming existing exam session',
                'submission': existing_submission.to_dict(),
                'exam': exam.to_dict(include_questions=True)
            }), 200
    
    # Create new submission
    submission = EMMExamSubmission(
        exam_id=exam_id,
        candidate_id=current_user_id,
        status='In Progress'
    )
    
    db.session.add(submission)
    db.session.commit()
    
    return jsonify({
        'message': 'Exam started successfully',
        'submission': submission.to_dict(),
        'exam': exam.to_dict(include_questions=True)
    }), 201

@emm_bp.route('/submissions/<int:submission_id>/answer', methods=['POST'])
@jwt_required()
@require_emm_access
def submit_answer(submission_id):
    """Submit answer for a question."""
    current_user_id = int(get_jwt_identity())
    submission = EMMExamSubmission.query.get_or_404(submission_id)
    
    # Check ownership
    if submission.candidate_id != current_user_id:
        return jsonify({'error': 'Not your submission'}), 403
    
    # Check if submission is still active
    if submission.status != 'In Progress':
        return jsonify({'error': 'Submission is not active'}), 400
    
    schema = SubmissionAnswerSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    # Validate question belongs to exam
    question = EMMQuestion.query.get_or_404(data['question_id'])
    if question not in submission.exam.questions:
        return jsonify({'error': 'Question not in this exam'}), 400
    
    # Check if answer already exists
    existing_answer = EMMSubmissionAnswer.query.filter_by(
        submission_id=submission_id,
        question_id=data['question_id']
    ).first()
    
    if existing_answer:
        # Update existing answer
        existing_answer.selected_option_id = data.get('selected_option_id')
        existing_answer.text_answer = data.get('text_answer')
        existing_answer.answered_at = datetime.utcnow()
    else:
        # Create new answer
        answer = EMMSubmissionAnswer(
            submission_id=submission_id,
            question_id=data['question_id'],
            selected_option_id=data.get('selected_option_id'),
            text_answer=data.get('text_answer')
        )
        db.session.add(answer)
    
    db.session.commit()
    
    return jsonify({'message': 'Answer submitted successfully'}), 200

@emm_bp.route('/submissions/<int:submission_id>/submit', methods=['POST'])
@jwt_required()
@require_emm_access
def submit_exam(submission_id):
    """Submit the entire exam."""
    current_user_id = int(get_jwt_identity())
    submission = EMMExamSubmission.query.get_or_404(submission_id)
    
    # Check ownership
    if submission.candidate_id != current_user_id:
        return jsonify({'error': 'Not your submission'}), 403
    
    # Check if submission is still active
    if submission.status != 'In Progress':
        return jsonify({'error': 'Submission is not active'}), 400
    
    # Calculate score
    score, percentage = submission.calculate_score()
    
    # Update submission
    submission.end_time = datetime.utcnow()
    submission.status = 'Completed'
    submission.submitted_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Exam submitted successfully',
        'submission': submission.to_dict(),
        'score': score,
        'percentage': percentage,
        'passed': percentage >= submission.exam.passing_score
    }), 200

# Results and Grading
@emm_bp.route('/submissions', methods=['GET'])
@jwt_required()
@require_emm_access
def get_submissions():
    """Get exam submissions based on user role."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    exam_id = request.args.get('exam_id', type=int)
    status = request.args.get('status')
    
    # Build query based on user role
    if current_user.has_role('Exam Administrator') or current_user.has_role('HR Admin'):
        # Admins can see all submissions
        query = EMMExamSubmission.query
    else:
        # Regular users can only see their own submissions
        query = EMMExamSubmission.query.filter_by(candidate_id=current_user_id)
    
    if exam_id:
        query = query.filter(EMMExamSubmission.exam_id == exam_id)
    if status:
        query = query.filter(EMMExamSubmission.status == status)
    
    submissions = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'submissions': [submission.to_dict() for submission in submissions.items],
        'total': submissions.total,
        'pages': submissions.pages,
        'current_page': page
    }), 200

@emm_bp.route('/submissions/<int:submission_id>', methods=['GET'])
@jwt_required()
@require_emm_access
def get_submission(submission_id):
    """Get specific submission."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    submission = EMMExamSubmission.query.get_or_404(submission_id)
    
    # Check access permissions
    if not (current_user.has_role('Exam Administrator') or 
            current_user.has_role('HR Admin') or
            submission.candidate_id == current_user_id):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    include_answers = (current_user.has_role('Exam Administrator') or 
                      current_user.has_role('HR Admin') or
                      submission.status == 'Completed')
    
    return jsonify({
        'submission': submission.to_dict(include_answers=include_answers)
    }), 200

# Dashboard and Statistics
@emm_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@require_emm_access
def get_emm_dashboard():
    """Get EMM dashboard data for current user."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    dashboard_data = {
        'user_info': current_user.to_dict(),
        'stats': {}
    }
    
    if current_user.has_role('Staff Member'):
        # Staff member dashboard
        my_submissions = EMMExamSubmission.query.filter_by(candidate_id=current_user_id).all()
        available_exams = EMMExam.query.filter_by(is_active=True).all()
        
        dashboard_data['stats'] = {
            'available_exams': len(available_exams),
            'completed_exams': len([s for s in my_submissions if s.status == 'Completed']),
            'in_progress_exams': len([s for s in my_submissions if s.status == 'In Progress']),
            'average_score': sum([s.percentage for s in my_submissions if s.percentage]) / len(my_submissions) if my_submissions else 0,
            'recent_submissions': [s.to_dict() for s in my_submissions[-3:]]
        }
    
    if current_user.has_role('Exam Administrator'):
        # Exam Administrator dashboard
        all_exams = EMMExam.query.all()
        all_submissions = EMMExamSubmission.query.all()
        all_questions = EMMQuestion.query.filter_by(is_active=True).all()
        
        dashboard_data['stats'].update({
            'total_exams': len(all_exams),
            'active_exams': len([e for e in all_exams if e.is_active]),
            'total_questions': len(all_questions),
            'total_submissions': len(all_submissions),
            'completed_submissions': len([s for s in all_submissions if s.status == 'Completed']),
            'average_exam_score': sum([s.percentage for s in all_submissions if s.percentage]) / len(all_submissions) if all_submissions else 0
        })
    
    return jsonify(dashboard_data), 200

# Integration with PMS
@emm_bp.route('/integration/promotion-scores', methods=['GET'])
@jwt_required()
@require_emm_access
def get_promotion_scores():
    """Get exam scores for promotion calculation (HR Admin only)."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    if not current_user.has_role('HR Admin'):
        return jsonify({'error': 'Only HR Admin can access promotion scores'}), 403
    
    # Get all completed exam submissions
    completed_submissions = EMMExamSubmission.query.filter_by(status='Completed').all()
    
    promotion_scores = []
    for submission in completed_submissions:
        promotion_scores.append({
            'candidate_id': submission.candidate_id,
            'candidate_name': f"{submission.candidate.first_name} {submission.candidate.last_name}",
            'exam_id': submission.exam_id,
            'exam_title': submission.exam.title,
            'score': submission.score,
            'percentage': submission.percentage,
            'submitted_at': submission.submitted_at.isoformat() if submission.submitted_at else None
        })
    
    return jsonify({
        'promotion_scores': promotion_scores,
        'total_candidates': len(set([s['candidate_id'] for s in promotion_scores]))
    }), 200


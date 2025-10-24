from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

# Association table for many-to-many relationship between exams and questions
exam_questions = db.Table('emm_exam_questions',
    db.Column('exam_id', db.Integer, db.ForeignKey('emm_exams.id'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('emm_questions.id'), primary_key=True)
)

class EMMQuestion(db.Model):
    __tablename__ = 'emm_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(255), nullable=False, default='MCQ')  # MCQ, Essay
    subject = db.Column(db.String(255), nullable=True)
    difficulty = db.Column(db.String(50), nullable=True)  # Easy, Medium, Hard
    points = db.Column(db.Integer, default=1)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    options = db.relationship('EMMOption', backref='question', lazy='dynamic', cascade='all, delete-orphan')
    exams = db.relationship('EMMExam', secondary=exam_questions, back_populates='questions')

    def __repr__(self):
        return f'<EMMQuestion {self.id}: {self.question_text[:50]}>'

    def to_dict(self, include_options=True):
        question_dict = {
            'id': self.id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'subject': self.subject,
            'difficulty': self.difficulty,
            'points': self.points,
            'created_by': self.created_by,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_options and self.question_type == 'MCQ':
            question_dict['options'] = [option.to_dict() for option in self.options]
        
        return question_dict

class EMMOption(db.Model):
    __tablename__ = 'emm_mcq_options'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('emm_questions.id'), nullable=False)
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<EMMOption {self.id}: {self.option_text[:30]}>'

    def to_dict(self, include_correct=False):
        option_dict = {
            'id': self.id,
            'question_id': self.question_id,
            'option_text': self.option_text,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_correct:
            option_dict['is_correct'] = self.is_correct
        
        return option_dict

class EMMExam(db.Model):
    __tablename__ = 'emm_exams'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    time_limit = db.Column(db.Integer, nullable=False)  # in minutes
    total_points = db.Column(db.Integer, default=0)
    passing_score = db.Column(db.Float, default=60.0)  # percentage
    is_active = db.Column(db.Boolean, default=True)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    
    # Promotional Exam Settings
    is_promotional_exam = db.Column(db.Boolean, default=False)
    target_conraiss_grade = db.Column(db.Integer, nullable=True)  # For promotional exams
    
    # Randomization Settings
    randomize_questions = db.Column(db.Boolean, default=False)
    randomize_options = db.Column(db.Boolean, default=False)
    
    # Exam Control
    attempts_allowed = db.Column(db.Integer, default=1)
    proctoring_enabled = db.Column(db.Boolean, default=False)
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('EMMQuestion', secondary=exam_questions, back_populates='exams')
    submissions = db.relationship('EMMExamSubmission', backref='exam', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<EMMExam {self.id}: {self.title}>'

    def calculate_total_points(self):
        """Calculate total points for the exam."""
        self.total_points = sum(question.points for question in self.questions)
        return self.total_points

    def to_dict(self, include_questions=False):
        exam_dict = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'time_limit': self.time_limit,
            'total_points': self.total_points,
            'passing_score': self.passing_score,
            'is_active': self.is_active,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_promotional_exam': self.is_promotional_exam,
            'target_conraiss_grade': self.target_conraiss_grade,
            'randomize_questions': self.randomize_questions,
            'randomize_options': self.randomize_options,
            'attempts_allowed': self.attempts_allowed,
            'proctoring_enabled': self.proctoring_enabled,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'question_count': len(self.questions)
        }
        
        if include_questions:
            exam_dict['questions'] = [question.to_dict() for question in self.questions]
        
        return exam_dict

class EMMExamSubmission(db.Model):
    __tablename__ = 'emm_exam_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('emm_exams.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Float, nullable=True)
    percentage = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(50), default='In Progress')  # In Progress, Completed, Submitted
    submitted_at = db.Column(db.DateTime, nullable=True)
    
    # Tracking and Security
    time_remaining = db.Column(db.Integer, nullable=True)  # Seconds remaining (for resume)
    ip_address = db.Column(db.String(45), nullable=True)
    browser_info = db.Column(db.Text, nullable=True)
    attempt_number = db.Column(db.Integer, default=1)
    is_flagged = db.Column(db.Boolean, default=False)  # Suspicious activity
    flagged_reason = db.Column(db.Text, nullable=True)
    
    # Relationships
    answers = db.relationship('EMMSubmissionAnswer', backref='submission', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<EMMExamSubmission {self.id}: Exam {self.exam_id} by User {self.candidate_id}>'

    def calculate_score(self):
        """Calculate the score for this submission."""
        total_points = 0
        earned_points = 0
        
        for answer in self.answers:
            question = answer.question
            total_points += question.points
            
            if question.question_type == 'MCQ':
                if answer.selected_option and answer.selected_option.is_correct:
                    earned_points += question.points
        
        self.score = earned_points
        if total_points > 0:
            self.percentage = (earned_points / total_points) * 100
        else:
            self.percentage = 0.0
        
        return self.score, self.percentage

    def to_dict(self, include_answers=False):
        submission_dict = {
            'id': self.id,
            'exam_id': self.exam_id,
            'candidate_id': self.candidate_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'score': self.score,
            'percentage': self.percentage,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'time_remaining': self.time_remaining,
            'attempt_number': self.attempt_number,
            'is_flagged': self.is_flagged,
            'flagged_reason': self.flagged_reason
        }
        
        if include_answers:
            submission_dict['answers'] = [answer.to_dict() for answer in self.answers]
        
        return submission_dict

class EMMSubmissionAnswer(db.Model):
    __tablename__ = 'emm_submission_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('emm_exam_submissions.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('emm_questions.id'), nullable=False)
    selected_option_id = db.Column(db.Integer, db.ForeignKey('emm_mcq_options.id'), nullable=True)
    text_answer = db.Column(db.Text, nullable=True)  # For essay questions
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    question = db.relationship('EMMQuestion', backref='answers')
    selected_option = db.relationship('EMMOption', backref='answers')

    def __repr__(self):
        return f'<EMMSubmissionAnswer {self.id}: Q{self.question_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'question_id': self.question_id,
            'selected_option_id': self.selected_option_id,
            'text_answer': self.text_answer,
            'answered_at': self.answered_at.isoformat() if self.answered_at else None
        }


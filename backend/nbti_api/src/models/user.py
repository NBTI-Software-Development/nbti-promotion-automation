from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()

# Association table for many-to-many relationship between users and roles
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    # Employee Information
    employee_id = db.Column(db.String(50), unique=True, nullable=True, index=True)
    ippis_number = db.Column(db.String(50), unique=True, nullable=True)
    file_no = db.Column(db.String(50), nullable=True)
    
    # Organizational Information
    department = db.Column(db.String(255), nullable=True)
    position = db.Column(db.String(255), nullable=True)
    rank = db.Column(db.String(100), nullable=True)
    cadre = db.Column(db.String(100), nullable=True)
    office_location = db.Column(db.String(100), nullable=True)
    
    # CONRAISS Information
    conraiss_grade = db.Column(db.Integer, nullable=True, index=True)  # 2-15
    conraiss_step = db.Column(db.Integer, nullable=True)  # 1-15 (varies by grade)
    
    # Dates
    date_of_first_appointment = db.Column(db.Date, nullable=True)
    confirmation_date = db.Column(db.Date, nullable=True)
    date_of_last_promotion = db.Column(db.Date, nullable=True)
    
    # Geographic Information
    state_of_origin = db.Column(db.String(100), nullable=True)
    local_government_area = db.Column(db.String(100), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    
    # Education
    qualifications = db.Column(db.Text, nullable=True)
    
    # Hierarchy
    supervisor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Promotion Tracking
    failed_promotion_attempts = db.Column(db.Integer, default=0)
    last_rrr_date = db.Column(db.Date, nullable=True)
    last_rrr_type = db.Column(db.String(50), nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = db.relationship('Role', secondary=user_roles, lazy='subquery',
                           backref=db.backref('users', lazy=True))
    supervisor = db.relationship('User', remote_side=[id], backref='subordinates', foreign_keys=[supervisor_id])
    
    # PMS relationships
    evaluations_as_staff = db.relationship('PMSEvaluation', foreign_keys='PMSEvaluation.staff_id', 
                                         backref='staff_member', lazy='dynamic')
    evaluations_as_supervisor = db.relationship('PMSEvaluation', foreign_keys='PMSEvaluation.supervisor_id', 
                                              backref='supervisor', lazy='dynamic')
    
    # EMM relationships
    exam_submissions = db.relationship('EMMExamSubmission', backref='candidate', lazy='dynamic')
    created_questions = db.relationship('EMMQuestion', backref='creator', lazy='dynamic')
    created_exams = db.relationship('EMMExam', backref='creator', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        """Check if the provided password matches the user's password."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def has_role(self, role_name):
        """Check if the user has a specific role."""
        return any(role.name == role_name for role in self.roles)

    def add_role(self, role):
        """Add a role to the user."""
        if role not in self.roles:
            self.roles.append(role)

    def remove_role(self, role):
        """Remove a role from the user."""
        if role in self.roles:
            self.roles.remove(role)

    @property
    def is_confirmed(self):
        """Check if user is confirmed (not on probation)."""
        return self.confirmation_date is not None
    
    @property
    def years_since_first_appointment(self):
        """Calculate years since first appointment."""
        if self.date_of_first_appointment:
            return (datetime.now().date() - self.date_of_first_appointment).days / 365.25
        return 0
    
    @property
    def time_in_grade(self):
        """Calculate time in current grade."""
        if self.date_of_last_promotion:
            return (datetime.now().date() - self.date_of_last_promotion).days / 365.25
        return self.years_since_first_appointment
    
    @property
    def current_salary(self):
        """Get current annual salary based on grade and step."""
        from .salary import SalaryScale
        if not self.conraiss_grade or not self.conraiss_step:
            return 0
        salary_record = SalaryScale.query.filter_by(
            conraiss_grade=self.conraiss_grade,
            step=self.conraiss_step,
            is_active=True
        ).first()
        return float(salary_record.annual_salary) if salary_record else 0
    
    def calculate_seniority_score(self, candidates_in_same_grade):
        """Calculate seniority score using priority-based ranking."""
        if not candidates_in_same_grade:
            return 100
        
        # Sort candidates by priority hierarchy
        sorted_candidates = sorted(candidates_in_same_grade, key=lambda x: (
            -x.conraiss_step if x.conraiss_step else 0,  # Higher step first
            x.confirmation_date if x.confirmation_date else datetime.max.date(),  # Earlier date first
            x.date_of_birth if x.date_of_birth else datetime.max.date(),  # Older first
            x.file_no if x.file_no else 'ZZZZ'  # Lower file number first
        ))
        
        # Find user's rank (1-indexed)
        try:
            user_rank = sorted_candidates.index(self) + 1
        except ValueError:
            return 0
        
        total_candidates = len(sorted_candidates)
        
        # Convert rank to score (0-100)
        # Rank 1 (most senior) = 100, Last rank = 0
        if total_candidates == 1:
            return 100
        
        seniority_score = ((total_candidates - user_rank) / (total_candidates - 1)) * 100
        return round(seniority_score, 2)
    
    def to_dict(self, include_roles=True):
        """Convert user object to dictionary."""
        user_dict = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'employee_id': self.employee_id,
            'ippis_number': self.ippis_number,
            'file_no': self.file_no,
            'department': self.department,
            'position': self.position,
            'rank': self.rank,
            'cadre': self.cadre,
            'office_location': self.office_location,
            'conraiss_grade': self.conraiss_grade,
            'conraiss_step': self.conraiss_step,
            'date_of_first_appointment': self.date_of_first_appointment.isoformat() if self.date_of_first_appointment else None,
            'confirmation_date': self.confirmation_date.isoformat() if self.confirmation_date else None,
            'date_of_last_promotion': self.date_of_last_promotion.isoformat() if self.date_of_last_promotion else None,
            'state_of_origin': self.state_of_origin,
            'local_government_area': self.local_government_area,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'phone_number': self.phone_number,
            'qualifications': self.qualifications,
            'supervisor_id': self.supervisor_id,
            'failed_promotion_attempts': self.failed_promotion_attempts,
            'last_rrr_date': self.last_rrr_date.isoformat() if self.last_rrr_date else None,
            'last_rrr_type': self.last_rrr_type,
            'is_active': self.is_active,
            'is_confirmed': self.is_confirmed,
            'years_since_first_appointment': self.years_since_first_appointment,
            'time_in_grade': self.time_in_grade,
            'current_salary': self.current_salary,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_roles:
            user_dict['roles'] = [role.to_dict() for role in self.roles]
        
        return user_dict

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Role {self.name}>'

    def to_dict(self):
        """Convert role object to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


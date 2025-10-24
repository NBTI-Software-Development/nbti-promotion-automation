from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class PMSEvaluation(db.Model):
    __tablename__ = 'pms_evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quarter = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(255), nullable=False, default='Pending')  # Pending, In Progress, Completed
    final_score = db.Column(db.Float, nullable=True)
    
    # Cycle Management
    cycle_id = db.Column(db.Integer, db.ForeignKey('pms_cycle.id'), nullable=True)
    
    # Second-Level Review (Calibration)
    second_level_reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    calibration_comments = db.Column(db.Text, nullable=True)
    calibrated_at = db.Column(db.DateTime, nullable=True)
    is_flagged_for_calibration = db.Column(db.Boolean, default=False)
    flagged_reason = db.Column(db.Text, nullable=True)
    
    # Mid-Quarter Review
    mid_quarter_review_date = db.Column(db.Date, nullable=True)
    mid_quarter_staff_comments = db.Column(db.Text, nullable=True)
    mid_quarter_supervisor_comments = db.Column(db.Text, nullable=True)
    goals_adjusted_mid_quarter = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    goals = db.relationship('PMSGoal', backref='evaluation', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<PMSEvaluation {self.id}: {self.quarter} {self.year}>'

    def calculate_final_score(self):
        """Calculate the final score based on weighted average of goal ratings."""
        agreed_goals = [goal for goal in self.goals if goal.agreed and goal.rating is not None]
        
        if not agreed_goals:
            self.final_score = 0.0
            return self.final_score
        
        total_weighted_score = sum(goal.rating * goal.weight for goal in agreed_goals)
        total_weight = sum(goal.weight for goal in agreed_goals)
        
        if total_weight == 0:
            self.final_score = 0.0
            return self.final_score
        
        # Average score (out of 5)
        average_score = total_weighted_score / total_weight
        self.final_score = average_score
        return self.final_score
    
    def get_pms_percentage(self):
        """Get PMS score as percentage (0-100)."""
        if self.final_score is None:
            self.calculate_final_score()
        return (self.final_score / 5.0) * 100 if self.final_score else 0

    def to_dict(self):
        return {
            'id': self.id,
            'staff_id': self.staff_id,
            'supervisor_id': self.supervisor_id,
            'quarter': self.quarter,
            'year': self.year,
            'status': self.status,
            'final_score': self.final_score,
            'pms_percentage': self.get_pms_percentage(),
            'cycle_id': self.cycle_id,
            'second_level_reviewer_id': self.second_level_reviewer_id,
            'calibration_comments': self.calibration_comments,
            'calibrated_at': self.calibrated_at.isoformat() if self.calibrated_at else None,
            'is_flagged_for_calibration': self.is_flagged_for_calibration,
            'flagged_reason': self.flagged_reason,
            'mid_quarter_review_date': self.mid_quarter_review_date.isoformat() if self.mid_quarter_review_date else None,
            'mid_quarter_staff_comments': self.mid_quarter_staff_comments,
            'mid_quarter_supervisor_comments': self.mid_quarter_supervisor_comments,
            'goals_adjusted_mid_quarter': self.goals_adjusted_mid_quarter,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'goals': [goal.to_dict() for goal in self.goals]
        }

class PMSGoal(db.Model):
    __tablename__ = 'pms_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('pms_evaluations.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    target = db.Column(db.Text, nullable=True)
    weight = db.Column(db.Float, default=1.0)  # Weight for scoring
    kra_category = db.Column(db.String(100), nullable=True)  # Key Result Area category
    agreed = db.Column(db.Boolean, default=False)
    
    # Self-Evaluation
    self_rating = db.Column(db.Integer, nullable=True)  # Staff self-assessment (1-5)
    self_comments = db.Column(db.Text, nullable=True)
    evidence = db.Column(db.JSON, nullable=True)  # Array of S3 file URLs
    
    # Supervisor Evaluation
    rating = db.Column(db.Integer, nullable=True)  # Supervisor rating (1-5 scale)
    supervisor_comments = db.Column(db.Text, nullable=True)
    staff_comments = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<PMSGoal {self.id}: {self.description[:50]}>'

    def to_dict(self):
        return {
            'id': self.id,
            'evaluation_id': self.evaluation_id,
            'description': self.description,
            'target': self.target,
            'weight': self.weight,
            'kra_category': self.kra_category,
            'agreed': self.agreed,
            'self_rating': self.self_rating,
            'self_comments': self.self_comments,
            'evidence': self.evidence,
            'rating': self.rating,
            'supervisor_comments': self.supervisor_comments,
            'staff_comments': self.staff_comments,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


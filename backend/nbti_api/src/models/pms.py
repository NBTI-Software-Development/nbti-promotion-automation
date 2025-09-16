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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    goals = db.relationship('PMSGoal', backref='evaluation', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<PMSEvaluation {self.id}: {self.quarter} {self.year}>'

    def calculate_final_score(self):
        """Calculate the final score based on goal ratings."""
        ratings = [goal.rating for goal in self.goals if goal.rating is not None]
        if ratings:
            self.final_score = sum(ratings) / len(ratings)
        else:
            self.final_score = 0.0
        return self.final_score

    def to_dict(self):
        return {
            'id': self.id,
            'staff_id': self.staff_id,
            'supervisor_id': self.supervisor_id,
            'quarter': self.quarter,
            'year': self.year,
            'status': self.status,
            'final_score': self.final_score,
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
    agreed = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Integer, nullable=True)  # 1-5 scale
    supervisor_comments = db.Column(db.Text, nullable=True)
    staff_comments = db.Column(db.Text, nullable=True)
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
            'agreed': self.agreed,
            'rating': self.rating,
            'supervisor_comments': self.supervisor_comments,
            'staff_comments': self.staff_comments,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


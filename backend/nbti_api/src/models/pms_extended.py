"""
Extended PMS Models - Cycle Management and Appeals
"""
from datetime import datetime
from .user import db


class PMSCycle(db.Model):
    """
    PMS Evaluation Cycle Management
    Manages quarterly evaluation cycles with deadlines
    """
    __tablename__ = 'pms_cycle'
    
    id = db.Column(db.Integer, primary_key=True)
    cycle_name = db.Column(db.String(100), nullable=False, unique=True)  # e.g., "Q1 2024"
    quarter = db.Column(db.String(10), nullable=False)  # Q1, Q2, Q3, Q4
    year = db.Column(db.Integer, nullable=False, index=True)
    
    # Deadlines
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    goal_setting_deadline = db.Column(db.Date)
    mid_quarter_review_deadline = db.Column(db.Date)
    self_evaluation_deadline = db.Column(db.Date)
    supervisor_review_deadline = db.Column(db.Date)
    second_level_review_deadline = db.Column(db.Date)
    calibration_meeting_date = db.Column(db.Date)
    
    # Status
    status = db.Column(db.String(50), default='Planning', index=True)  # Planning/Active/Closed
    is_active = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PMSCycle {self.cycle_name}>'
    
    def to_dict(self):
        """Convert PMS cycle to dictionary."""
        return {
            'id': self.id,
            'cycle_name': self.cycle_name,
            'quarter': self.quarter,
            'year': self.year,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'goal_setting_deadline': self.goal_setting_deadline.isoformat() if self.goal_setting_deadline else None,
            'mid_quarter_review_deadline': self.mid_quarter_review_deadline.isoformat() if self.mid_quarter_review_deadline else None,
            'self_evaluation_deadline': self.self_evaluation_deadline.isoformat() if self.self_evaluation_deadline else None,
            'supervisor_review_deadline': self.supervisor_review_deadline.isoformat() if self.supervisor_review_deadline else None,
            'second_level_review_deadline': self.second_level_review_deadline.isoformat() if self.second_level_review_deadline else None,
            'calibration_meeting_date': self.calibration_meeting_date.isoformat() if self.calibration_meeting_date else None,
            'status': self.status,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Appeal(db.Model):
    """
    Performance Evaluation Appeals
    """
    __tablename__ = 'appeal'
    
    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('pms_evaluations.id'), nullable=False, index=True)
    appellant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    # Appeal Details
    appeal_reason = db.Column(db.Text, nullable=False)
    supporting_evidence = db.Column(db.JSON)  # Array of S3 file URLs
    contested_goals = db.Column(db.JSON)  # Array of goal IDs
    
    # Workflow
    status = db.Column(db.String(50), default='Submitted', index=True)  # Submitted/Under Review/Resolved
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    resolution = db.Column(db.String(50))  # Upheld/Partially Upheld/Rejected
    resolution_details = db.Column(db.Text)
    resolved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    resolved_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    evaluation = db.relationship('PMSEvaluation', backref='appeals')
    appellant = db.relationship('User', foreign_keys=[appellant_id], backref='filed_appeals')
    assignee = db.relationship('User', foreign_keys=[assigned_to])
    resolver = db.relationship('User', foreign_keys=[resolved_by])
    
    def __repr__(self):
        return f'<Appeal {self.id} for Evaluation {self.evaluation_id}>'
    
    def to_dict(self):
        """Convert appeal to dictionary."""
        return {
            'id': self.id,
            'evaluation_id': self.evaluation_id,
            'appellant_id': self.appellant_id,
            'appeal_reason': self.appeal_reason,
            'supporting_evidence': self.supporting_evidence,
            'contested_goals': self.contested_goals,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'resolution': self.resolution,
            'resolution_details': self.resolution_details,
            'resolved_by': self.resolved_by,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DevelopmentNeed(db.Model):
    """
    Training and Development Needs Tracking
    """
    __tablename__ = 'development_need'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    competency_gap = db.Column(db.String(255), nullable=False)
    development_action = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(50), default='Medium')  # Low/Medium/High
    status = db.Column(db.String(50), default='Identified', index=True)  # Identified/In Progress/Completed
    target_completion_date = db.Column(db.Date)
    actual_completion_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='development_needs')
    
    def __repr__(self):
        return f'<DevelopmentNeed {self.id} for User {self.user_id}>'
    
    def to_dict(self):
        """Convert development need to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'competency_gap': self.competency_gap,
            'development_action': self.development_action,
            'priority': self.priority,
            'status': self.status,
            'target_completion_date': self.target_completion_date.isoformat() if self.target_completion_date else None,
            'actual_completion_date': self.actual_completion_date.isoformat() if self.actual_completion_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


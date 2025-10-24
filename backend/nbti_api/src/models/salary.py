"""
Salary Scale and Step Increment Models
"""
from datetime import datetime
from .user import db


class SalaryScale(db.Model):
    """
    CONRAISS Salary Scale Table
    Stores salary information for each grade and step combination.
    """
    __tablename__ = 'salary_scale'
    
    id = db.Column(db.Integer, primary_key=True)
    conraiss_grade = db.Column(db.Integer, nullable=False, index=True)
    step = db.Column(db.Integer, nullable=False)
    annual_salary = db.Column(db.Numeric(12, 2), nullable=False)
    effective_date = db.Column(db.Date, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('conraiss_grade', 'step', 'effective_date', 
                          name='unique_grade_step_date'),
    )
    
    def __repr__(self):
        return f'<SalaryScale Grade {self.conraiss_grade} Step {self.step}: ₦{self.annual_salary}>'
    
    def to_dict(self):
        """Convert salary scale object to dictionary."""
        return {
            'id': self.id,
            'conraiss_grade': self.conraiss_grade,
            'step': self.step,
            'annual_salary': float(self.annual_salary),
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class StepIncrementLog(db.Model):
    """
    Log of all step increments (annual and promotion-related)
    """
    __tablename__ = 'step_increment_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    previous_step = db.Column(db.Integer, nullable=False)
    new_step = db.Column(db.Integer, nullable=False)
    increment_date = db.Column(db.Date, nullable=False)
    increment_type = db.Column(db.String(50), nullable=False)  # 'Annual' or 'Promotion'
    processed_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # NULL for automated
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='step_increments')
    processor = db.relationship('User', foreign_keys=[processed_by])
    
    def __repr__(self):
        return f'<StepIncrementLog User {self.user_id}: Step {self.previous_step} → {self.new_step}>'
    
    def to_dict(self):
        """Convert step increment log to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'previous_step': self.previous_step,
            'new_step': self.new_step,
            'increment_date': self.increment_date.isoformat() if self.increment_date else None,
            'increment_type': self.increment_type,
            'processed_by': self.processed_by,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


"""
RRR (Recommendation, Recognition, and Reward) Models
"""
from datetime import datetime
from .user import db


class RRRVacancy(db.Model):
    """
    RRR Vacancy Configuration per CONRAISS Grade
    Defines how many promotion, recognition, and reward slots are available per grade per cycle.
    """
    __tablename__ = 'rrr_vacancy'
    
    id = db.Column(db.Integer, primary_key=True)
    conraiss_grade = db.Column(db.Integer, nullable=False, index=True)
    promotion_cycle = db.Column(db.String(50), nullable=False, index=True)  # e.g., "2024", "2025"
    promotion_vacancies = db.Column(db.Integer, default=0)
    recognition_slots = db.Column(db.Integer, default=0)
    reward_slots = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('conraiss_grade', 'promotion_cycle', 
                          name='unique_grade_cycle'),
    )
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<RRRVacancy Grade {self.conraiss_grade} Cycle {self.promotion_cycle}>'
    
    def to_dict(self):
        """Convert RRR vacancy to dictionary."""
        return {
            'id': self.id,
            'conraiss_grade': self.conraiss_grade,
            'promotion_cycle': self.promotion_cycle,
            'promotion_vacancies': self.promotion_vacancies,
            'recognition_slots': self.recognition_slots,
            'reward_slots': self.reward_slots,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class RRRRecommendation(db.Model):
    """
    RRR Recommendation for a user in a specific promotion cycle
    Tracks combined scores, ranking, and RRR allocations.
    """
    __tablename__ = 'rrr_recommendation'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    promotion_cycle = db.Column(db.String(50), nullable=False, index=True)
    conraiss_grade = db.Column(db.Integer, nullable=False)  # Current grade at time of evaluation
    
    # Scores (0-100)
    exam_score = db.Column(db.Float)
    pms_score = db.Column(db.Float)
    seniority_score = db.Column(db.Float)
    combined_score = db.Column(db.Float)
    
    # Ranking within grade
    rank_in_grade = db.Column(db.Integer)
    total_candidates_in_grade = db.Column(db.Integer)
    
    # RRR Allocations (can have multiple)
    is_promoted = db.Column(db.Boolean, default=False)
    is_recognized = db.Column(db.Boolean, default=False)
    is_rewarded = db.Column(db.Boolean, default=False)
    
    # Promotion details (if promoted)
    promoted_to_grade = db.Column(db.Integer)
    promoted_to_step = db.Column(db.Integer)
    promotion_effective_date = db.Column(db.Date)
    
    # Workflow
    status = db.Column(db.String(50), default='Pending')  # Pending/Approved/Rejected
    recommended_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approval_date = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='rrr_recommendations')
    recommender = db.relationship('User', foreign_keys=[recommended_by])
    approver = db.relationship('User', foreign_keys=[approved_by])
    
    def __repr__(self):
        return f'<RRRRecommendation User {self.user_id} Cycle {self.promotion_cycle} Rank {self.rank_in_grade}>'
    
    def to_dict(self):
        """Convert RRR recommendation to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'promotion_cycle': self.promotion_cycle,
            'conraiss_grade': self.conraiss_grade,
            'exam_score': self.exam_score,
            'pms_score': self.pms_score,
            'seniority_score': self.seniority_score,
            'combined_score': self.combined_score,
            'rank_in_grade': self.rank_in_grade,
            'total_candidates_in_grade': self.total_candidates_in_grade,
            'is_promoted': self.is_promoted,
            'is_recognized': self.is_recognized,
            'is_rewarded': self.is_rewarded,
            'promoted_to_grade': self.promoted_to_grade,
            'promoted_to_step': self.promoted_to_step,
            'promotion_effective_date': self.promotion_effective_date.isoformat() if self.promotion_effective_date else None,
            'status': self.status,
            'recommended_by': self.recommended_by,
            'approved_by': self.approved_by,
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'rejection_reason': self.rejection_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


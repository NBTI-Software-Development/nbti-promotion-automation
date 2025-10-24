"""
NBTI Promotion Automation - Database Models
Centralized import for all models
"""

# Import db instance
from .user import db

# User and Role models
from .user import User, Role, user_roles

# PMS models
from .pms import PMSEvaluation, PMSGoal
from .pms_extended import PMSCycle, Appeal, DevelopmentNeed

# EMM models
from .emm import (
    EMMQuestion, 
    EMMOption, 
    EMMExam, 
    EMMExamSubmission, 
    EMMSubmissionAnswer,
    exam_questions
)

# Salary and Step models
from .salary import SalaryScale, StepIncrementLog

# RRR models
from .rrr import RRRVacancy, RRRRecommendation

# System models
from .system import SystemConfiguration, AuditLog, Notification

# Export all models
__all__ = [
    'db',
    # User models
    'User',
    'Role',
    'user_roles',
    # PMS models
    'PMSEvaluation',
    'PMSGoal',
    'PMSCycle',
    'Appeal',
    'DevelopmentNeed',
    # EMM models
    'EMMQuestion',
    'EMMOption',
    'EMMExam',
    'EMMExamSubmission',
    'EMMSubmissionAnswer',
    'exam_questions',
    # Salary models
    'SalaryScale',
    'StepIncrementLog',
    # RRR models
    'RRRVacancy',
    'RRRRecommendation',
    # System models
    'SystemConfiguration',
    'AuditLog',
    'Notification',
]


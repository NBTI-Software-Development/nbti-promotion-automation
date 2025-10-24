"""
System Configuration and Audit Models
"""
from datetime import datetime
from .user import db
import uuid


class SystemConfiguration(db.Model):
    """
    System-wide configuration settings
    """
    __tablename__ = 'system_configuration'
    
    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    config_value = db.Column(db.Text)
    config_type = db.Column(db.String(50))  # string/integer/boolean/json/float
    description = db.Column(db.Text)
    is_editable = db.Column(db.Boolean, default=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    updater = db.relationship('User', foreign_keys=[updated_by])
    
    def __repr__(self):
        return f'<SystemConfiguration {self.config_key}: {self.config_value}>'
    
    def get_value(self):
        """Get the typed value based on config_type."""
        if self.config_value is None:
            return None
        
        if self.config_type == 'integer':
            return int(self.config_value)
        elif self.config_type == 'float':
            return float(self.config_value)
        elif self.config_type == 'boolean':
            return self.config_value.lower() in ['true', '1', 'yes']
        elif self.config_type == 'json':
            import json
            return json.loads(self.config_value)
        else:  # string
            return self.config_value
    
    def set_value(self, value):
        """Set the value with appropriate type conversion."""
        if self.config_type == 'json':
            import json
            self.config_value = json.dumps(value)
        else:
            self.config_value = str(value)
    
    def to_dict(self):
        """Convert system configuration to dictionary."""
        return {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': self.get_value(),
            'config_type': self.config_type,
            'description': self.description,
            'is_editable': self.is_editable,
            'updated_by': self.updated_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AuditLog(db.Model):
    """
    Forensic-level audit logging for all system actions
    UUID-based for tamper-proof tracking
    """
    __tablename__ = 'audit_log'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    
    # Action Details
    action_type = db.Column(db.String(50), nullable=False, index=True)  # CREATE/UPDATE/DELETE/VIEW/APPROVE/REJECT
    entity_type = db.Column(db.String(50), nullable=False, index=True)  # Evaluation/Goal/Exam/User/RRR
    entity_id = db.Column(db.Integer, index=True)
    
    # Change Tracking (JSON format for flexibility)
    old_value = db.Column(db.JSON)
    new_value = db.Column(db.JSON)
    
    # Security Context
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    session_id = db.Column(db.String(100))
    
    # Flags
    is_sensitive = db.Column(db.Boolean, default=False, index=True)  # RRR decisions, promotions
    
    # Timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    
    def __repr__(self):
        return f'<AuditLog {self.action_type} {self.entity_type} by User {self.user_id}>'
    
    def to_dict(self):
        """Convert audit log to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action_type': self.action_type,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'session_id': self.session_id,
            'is_sensitive': self.is_sensitive,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class Notification(db.Model):
    """
    System notifications for users
    """
    __tablename__ = 'notification'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    notification_type = db.Column(db.String(50), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, index=True)
    
    # Related entity (optional)
    related_entity_type = db.Column(db.String(50))
    related_entity_id = db.Column(db.Integer)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    read_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.notification_type} for User {self.user_id}>'
    
    def mark_as_read(self):
        """Mark notification as read."""
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert notification to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'notification_type': self.notification_type,
            'title': self.title,
            'message': self.message,
            'is_read': self.is_read,
            'related_entity_type': self.related_entity_type,
            'related_entity_id': self.related_entity_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }


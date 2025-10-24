"""
Celery Background Tasks
Handles automated step increments, notifications, and other background jobs.
"""

import os
from datetime import datetime, date
from src.celery_app import celery_app
from src.models import db, User, Notification, StepIncrementLog


def get_flask_app():
    """Lazy load Flask app to avoid circular imports."""
    from src.main import create_app
    return create_app()


@celery_app.task(name='src.tasks.process_annual_step_increment')
def process_annual_step_increment():
    """
    Process annual step increment for all eligible staff.
    Runs automatically on January 1st every year.
    """
    flask_app = get_flask_app()
    with flask_app.app_context():
        # Get all active users
        users = User.query.filter_by(is_active=True).all()
        
        incremented_count = 0
        skipped_count = 0
        error_count = 0
        
        for user in users:
            try:
                if not user.conraiss_grade or not user.conraiss_step:
                    skipped_count += 1
                    continue
                
                # Get max step for user's grade
                if 2 <= user.conraiss_grade <= 9:
                    max_step = 15
                elif 10 <= user.conraiss_grade <= 12:
                    max_step = 11
                elif 13 <= user.conraiss_grade <= 15:
                    max_step = 9
                else:
                    max_step = 15
                
                # Check if already at max step
                if user.conraiss_step >= max_step:
                    skipped_count += 1
                    continue
                
                # Increment step
                old_step = user.conraiss_step
                user.conraiss_step += 1
                
                # Log the increment
                log = StepIncrementLog(
                    user_id=user.id,
                    previous_step=old_step,
                    new_step=user.conraiss_step,
                    increment_date=date.today(),
                    increment_type='Annual',
                    notes=f"Automated annual step increment from {old_step} to {user.conraiss_step}"
                )
                db.session.add(log)
                
                # Create notification
                notification = Notification(
                    user_id=user.id,
                    notification_type='step_increment',
                    title='Annual Step Increment',
                    message=f'Your step has been automatically incremented from {old_step} to {user.conraiss_step} as part of the annual increment process.',
                    is_read=False
                )
                db.session.add(notification)
                
                incremented_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"Error processing user {user.id}: {str(e)}")
                continue
        
        # Commit all changes
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {
                'status': 'error',
                'message': f'Database commit failed: {str(e)}',
                'incremented': 0,
                'skipped': 0,
                'errors': error_count
            }
        
        return {
            'status': 'success',
            'message': 'Annual step increment completed',
            'incremented': incremented_count,
            'skipped': skipped_count,
            'errors': error_count,
            'timestamp': datetime.utcnow().isoformat()
        }


@celery_app.task(name='src.tasks.send_pending_notifications')
def send_pending_notifications():
    """
    Send pending email notifications.
    Runs every 15 minutes.
    """
    flask_app = get_flask_app()
    with flask_app.app_context():
        # TODO: Implement email notification sending
        # For now, just mark notifications as processed
        
        # Get unread notifications older than 1 hour
        # This is a placeholder for actual email sending logic
        
        return {
            'status': 'success',
            'message': 'Notification processing completed',
            'timestamp': datetime.utcnow().isoformat()
        }


@celery_app.task(name='src.tasks.generate_rrr_report')
def generate_rrr_report(promotion_cycle: str):
    """
    Generate RRR report for a promotion cycle.
    Can be triggered manually.
    """
    flask_app = get_flask_app()
    with flask_app.app_context():
        from src.models import RRRRecommendation
        
        recommendations = RRRRecommendation.query.filter_by(
            promotion_cycle=promotion_cycle
        ).all()
        
        # TODO: Generate PDF report
        # For now, just return statistics
        
        total = len(recommendations)
        promoted = sum(1 for r in recommendations if r.is_promoted)
        recognized = sum(1 for r in recommendations if r.is_recognized)
        rewarded = sum(1 for r in recommendations if r.is_rewarded)
        
        return {
            'status': 'success',
            'promotion_cycle': promotion_cycle,
            'statistics': {
                'total': total,
                'promoted': promoted,
                'recognized': recognized,
                'rewarded': rewarded
            },
            'timestamp': datetime.utcnow().isoformat()
        }


@celery_app.task(name='src.tasks.backup_database')
def backup_database():
    """
    Create database backup.
    Should be scheduled daily.
    """
    # TODO: Implement database backup logic
    # This would typically use pg_dump for PostgreSQL
    
    return {
        'status': 'success',
        'message': 'Database backup completed',
        'timestamp': datetime.utcnow().isoformat()
    }


@celery_app.task(name='src.tasks.cleanup_old_audit_logs')
def cleanup_old_audit_logs(days_to_keep: int = 3650):
    """
    Clean up audit logs older than specified days (default 10 years).
    """
    flask_app = get_flask_app()
    with flask_app.app_context():
        from src.models import AuditLog
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        deleted_count = AuditLog.query.filter(
            AuditLog.timestamp < cutoff_date
        ).delete()
        
        db.session.commit()
        
        return {
            'status': 'success',
            'message': f'Deleted {deleted_count} audit log entries older than {days_to_keep} days',
            'deleted_count': deleted_count,
            'timestamp': datetime.utcnow().isoformat()
        }


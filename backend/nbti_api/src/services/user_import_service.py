"""
User Import Service
Handles bulk import of users from CSV files.
"""

import csv
import io
from typing import List, Dict, Tuple
from datetime import datetime, date
from src.models import db, User, Role
from src.services.audit_service import log_action


def parse_date(date_str: str) -> date:
    """
    Parse date string in various formats.
    
    Args:
        date_str: Date string (YYYY-MM-DD, DD/MM/YYYY, etc.)
    
    Returns:
        date object or None
    """
    if not date_str or date_str.strip() == '':
        return None
    
    # Try different date formats
    formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    
    return None


def generate_username(first_name: str, last_name: str, employee_id: str = None) -> str:
    """
    Generate username from name and employee ID.
    
    Args:
        first_name: First name
        last_name: Last name
        employee_id: Optional employee ID
    
    Returns:
        Generated username
    """
    if employee_id:
        return employee_id.lower().replace(' ', '')
    else:
        # Use first.last format
        username = f"{first_name.lower()}.{last_name.lower()}"
        return username.replace(' ', '')


def generate_temp_password() -> str:
    """
    Generate temporary password for new user.
    
    Returns:
        Temporary password
    """
    import secrets
    import string
    
    # Generate 12-character password with letters and digits
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(12))
    
    return password


def validate_csv_row(row: Dict, row_num: int) -> Tuple[bool, List[str]]:
    """
    Validate a CSV row.
    
    Args:
        row: Dictionary of CSV row data
        row_num: Row number for error reporting
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    required_fields = ['first_name', 'last_name', 'email', 'employee_id']
    
    for field in required_fields:
        if field not in row or not row[field] or row[field].strip() == '':
            errors.append(f"Row {row_num}: Missing required field '{field}'")
    
    # Validate email format
    if 'email' in row and row['email']:
        email = row['email'].strip()
        if '@' not in email or '.' not in email:
            errors.append(f"Row {row_num}: Invalid email format '{email}'")
    
    # Validate CONRAISS grade
    if 'conraiss_grade' in row and row['conraiss_grade']:
        try:
            grade = int(row['conraiss_grade'])
            if grade < 2 or grade > 15:
                errors.append(f"Row {row_num}: CONRAISS grade must be between 2 and 15")
        except ValueError:
            errors.append(f"Row {row_num}: CONRAISS grade must be a number")
    
    return len(errors) == 0, errors


def import_users_from_csv(csv_file, imported_by: int) -> Dict:
    """
    Import users from CSV file.
    
    CSV Format:
    employee_id, first_name, last_name, email, department, position, rank, cadre,
    ippis_number, date_of_birth, state_of_origin, local_government_area, file_no,
    confirmation_date, qualifications, conraiss_grade, date_of_hire, phone_number,
    office_location, supervisor_employee_id
    
    Args:
        csv_file: File object containing CSV data
        imported_by: User ID of person performing import
    
    Returns:
        Dictionary with import statistics and errors
    """
    # Read CSV file
    csv_data = csv_file.read().decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(csv_data))
    
    # Statistics
    total_rows = 0
    successful = 0
    skipped = 0
    errors = []
    created_users = []
    
    # Get default "Staff Member" role
    staff_role = Role.query.filter_by(name='Staff Member').first()
    if not staff_role:
        staff_role = Role(name='Staff Member', description='Regular staff member')
        db.session.add(staff_role)
        db.session.flush()
    
    for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is row 1)
        total_rows += 1
        
        # Validate row
        is_valid, validation_errors = validate_csv_row(row, row_num)
        
        if not is_valid:
            errors.extend(validation_errors)
            skipped += 1
            continue
        
        try:
            # Check if user already exists
            employee_id = row['employee_id'].strip()
            email = row['email'].strip().lower()
            
            existing_user = User.query.filter(
                (User.employee_id == employee_id) | (User.email == email)
            ).first()
            
            if existing_user:
                errors.append(f"Row {row_num}: User with employee_id '{employee_id}' or email '{email}' already exists")
                skipped += 1
                continue
            
            # Create new user
            user = User(
                employee_id=employee_id,
                first_name=row['first_name'].strip(),
                last_name=row['last_name'].strip(),
                email=email,
                department=row.get('department', '').strip() or None,
                position=row.get('position', '').strip() or None,
                rank=row.get('rank', '').strip() or None,
                cadre=row.get('cadre', '').strip() or None,
                ippis_number=row.get('ippis_number', '').strip() or None,
                file_no=row.get('file_no', '').strip() or None,
                state_of_origin=row.get('state_of_origin', '').strip() or None,
                local_government_area=row.get('local_government_area', '').strip() or None,
                phone_number=row.get('phone_number', '').strip() or None,
                office_location=row.get('office_location', '').strip() or None,
                qualifications=row.get('qualifications', '').strip() or None,
                is_active=True
            )
            
            # Generate username
            user.username = generate_username(user.first_name, user.last_name, employee_id)
            
            # Generate temporary password
            temp_password = generate_temp_password()
            user.set_password(temp_password)
            
            # Parse dates
            if 'date_of_birth' in row:
                user.date_of_birth = parse_date(row['date_of_birth'])
            
            if 'confirmation_date' in row:
                user.confirmation_date = parse_date(row['confirmation_date'])
            
            if 'date_of_hire' in row:
                user.date_of_first_appointment = parse_date(row['date_of_hire'])
            
            # Parse CONRAISS grade
            if 'conraiss_grade' in row and row['conraiss_grade']:
                try:
                    user.conraiss_grade = int(row['conraiss_grade'])
                    # Default to step 1 if not specified
                    user.conraiss_step = 1
                except ValueError:
                    pass
            
            # Add default role
            user.add_role(staff_role)
            
            # Store supervisor_employee_id for later linking
            supervisor_employee_id = row.get('supervisor_employee_id', '').strip()
            if supervisor_employee_id:
                # We'll link supervisors in a second pass
                user._temp_supervisor_employee_id = supervisor_employee_id
            
            db.session.add(user)
            db.session.flush()  # Get user ID
            
            # Store for later supervisor linking
            created_users.append({
                'user': user,
                'temp_password': temp_password,
                'supervisor_employee_id': supervisor_employee_id
            })
            
            successful += 1
            
        except Exception as e:
            errors.append(f"Row {row_num}: Error creating user - {str(e)}")
            skipped += 1
            continue
    
    # Second pass: Link supervisors
    supervisor_link_errors = []
    for user_data in created_users:
        user = user_data['user']
        supervisor_employee_id = user_data['supervisor_employee_id']
        
        if supervisor_employee_id:
            supervisor = User.query.filter_by(employee_id=supervisor_employee_id).first()
            if supervisor:
                user.supervisor_id = supervisor.id
            else:
                supervisor_link_errors.append(
                    f"User {user.employee_id}: Supervisor with employee_id '{supervisor_employee_id}' not found"
                )
    
    # Commit all changes
    try:
        db.session.commit()
        
        # Log the import action
        log_action(
            user_id=imported_by,
            action_type='BULK_IMPORT',
            entity_type='User',
            new_value={
                'total_rows': total_rows,
                'successful': successful,
                'skipped': skipped,
                'errors_count': len(errors)
            },
            is_sensitive=False
        )
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'Database commit failed: {str(e)}',
            'statistics': {
                'total_rows': total_rows,
                'successful': 0,
                'skipped': total_rows,
                'errors': len(errors) + 1
            },
            'errors': errors + [f'Database error: {str(e)}']
        }
    
    # Prepare result
    result = {
        'success': True,
        'message': f'Import completed: {successful} users created, {skipped} skipped',
        'statistics': {
            'total_rows': total_rows,
            'successful': successful,
            'skipped': skipped,
            'errors': len(errors),
            'supervisor_link_errors': len(supervisor_link_errors)
        },
        'errors': errors + supervisor_link_errors,
        'created_users': [
            {
                'employee_id': u['user'].employee_id,
                'username': u['user'].username,
                'email': u['user'].email,
                'temp_password': u['temp_password']
            }
            for u in created_users
        ]
    }
    
    return result


def get_csv_template() -> str:
    """
    Get CSV template with headers.
    
    Returns:
        CSV template string
    """
    headers = [
        'employee_id',
        'first_name',
        'last_name',
        'email',
        'department',
        'position',
        'rank',
        'cadre',
        'ippis_number',
        'date_of_birth',
        'state_of_origin',
        'local_government_area',
        'file_no',
        'confirmation_date',
        'qualifications',
        'conraiss_grade',
        'date_of_hire',
        'phone_number',
        'office_location',
        'supervisor_employee_id'
    ]
    
    return ','.join(headers)


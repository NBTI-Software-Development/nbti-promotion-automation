# NBTI Promotion Automation System: Final Complete Specifications

**Author:** Manus AI  
**Date:** October 24, 2025  
**Document Version:** 3.0 (Final - All Questions Answered)

---

## Document Status: ✅ COMPLETE - READY FOR IMPLEMENTATION

This document contains all finalized requirements, business rules, and technical specifications. All ambiguities have been resolved.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [RRR Scoring Formula (Corrected)](#2-rrr-scoring-formula-corrected)
3. [Seniority System (Complete Specification)](#3-seniority-system-complete-specification)
4. [CONRAISS Salary Scale](#4-conraiss-salary-scale)
5. [Promotion Step Allocation Logic](#5-promotion-step-allocation-logic)
6. [Annual Step Increment (Automated)](#6-annual-step-increment-automated)
7. [RRR Allocation (Rank-Based System)](#7-rrr-allocation-rank-based-system)
8. [Promotion Eligibility Rules](#8-promotion-eligibility-rules)
9. [User Data Import Specification](#9-user-data-import-specification)
10. [Complete Database Schema](#10-complete-database-schema)
11. [Implementation Roadmap](#11-implementation-roadmap)
12. [Critical Business Rules Summary](#12-critical-business-rules-summary)

---

## 1. Executive Summary

The NBTI Promotion Automation System implements a comprehensive **Recommendation, Recognition, and Reward (RRR) Policy** that combines:

- **70% Exam Score** - Performance on promotional examinations
- **20% PMS Score** - Quarterly performance evaluation average  
- **10% Seniority Score** - Based on CONRAISS step, confirmation date, age, and file number

The system uses a **rank-based allocation** with limited vacancies per CONRAISS grade, not fixed thresholds. It manages the complete lifecycle of performance evaluations, exams, and promotions with forensic-level audit trails.

---

## 2. RRR Scoring Formula (Corrected)

### 2.1 Combined Promotion Score

```
Final Promotion Score = (Exam Score × 0.70) + (PMS Score × 0.20) + (Seniority Score × 0.10)
```

**Where:**
- **Exam Score:** 0-100 (percentage score on promotional exam)
- **PMS Score:** 0-100 (weighted average of goal ratings, converted to percentage)
- **Seniority Score:** 0-100 (calculated using priority-based tie-breaking system)

### 2.2 Example Calculation

**Staff Member Profile:**
- Exam Score: 85%
- PMS Score: 78%
- Seniority Score: 65%

**Combined Score:**
```
= (85 × 0.70) + (78 × 0.20) + (65 × 0.10)
= 59.5 + 15.6 + 6.5
= 81.6%
```

---

## 3. Seniority System (Complete Specification)

### 3.1 Seniority Calculation Method

**CRITICAL:** Seniority is **NOT a weighted combination**. It uses a **priority-based tie-breaking system**.

### 3.2 Priority Hierarchy

When ranking candidates with the same combined score (or when calculating seniority):

**Priority 1: CONRAISS Step (Highest Priority)**
- Staff with higher step ranks higher
- Example: Grade 8 Step 7 > Grade 8 Step 5

**Priority 2: Confirmation Date (If steps are equal)**
- Staff confirmed earlier ranks higher
- Example: Confirmed 2018-01-15 > Confirmed 2019-03-20

**Priority 3: Age (If confirmation dates are equal)**
- Older staff ranks higher
- Example: Born 1985-05-10 > Born 1990-08-15

**Priority 4: File Number (If ages are equal)**
- Lower file number ranks higher (earlier employee)
- Example: File No. 1234 > File No. 5678

### 3.3 Seniority Score Calculation Algorithm

```python
def calculate_seniority_score(user, all_candidates_in_same_grade):
    """
    Calculate seniority score (0-100) using priority-based ranking.
    """
    # Sort candidates by priority hierarchy
    sorted_candidates = sorted(all_candidates_in_same_grade, key=lambda x: (
        -x.conraiss_step,  # Higher step first (negative for descending)
        x.confirmation_date if x.confirmation_date else datetime.max.date(),  # Earlier date first
        x.date_of_birth if x.date_of_birth else datetime.max.date(),  # Older first
        x.file_no  # Lower file number first
    ))
    
    # Find user's rank (1-indexed)
    user_rank = sorted_candidates.index(user) + 1
    total_candidates = len(sorted_candidates)
    
    # Convert rank to score (0-100)
    # Rank 1 (most senior) = 100, Last rank = 0
    seniority_score = ((total_candidates - user_rank) / (total_candidates - 1)) * 100 if total_candidates > 1 else 100
    
    return round(seniority_score, 2)
```

### 3.4 Seniority Tie-Breaking Example

**Scenario:** Three staff members competing for promotion to Grade 9:

| Staff | Step | Confirmation Date | Age (DOB) | File No. | Seniority Rank |
|-------|------|-------------------|-----------|----------|----------------|
| Alice | 7 | 2018-06-15 | 1985-03-20 | 2345 | **1st** (Highest step) |
| Bob | 6 | 2017-01-10 | 1987-08-12 | 1234 | **2nd** (Lower step) |
| Carol | 6 | 2017-01-10 | 1990-05-05 | 3456 | **3rd** (Same step & confirmation, but younger) |

**Seniority Scores:**
- Alice: 100 (rank 1 of 3)
- Bob: 50 (rank 2 of 3)
- Carol: 0 (rank 3 of 3)

### 3.5 Database Requirements for Seniority

**User Model Fields:**
```python
conraiss_grade = db.Column(db.Integer)  # 2-15
conraiss_step = db.Column(db.Integer)   # 1-15 (varies by grade)
confirmation_date = db.Column(db.Date)
date_of_birth = db.Column(db.Date)
file_no = db.Column(db.String(50))
```

---

## 4. CONRAISS Salary Scale

### 4.1 Step Structure by Grade

| CONRAISS Grade | Maximum Steps |
|----------------|---------------|
| Grade 2-9 | 15 steps |
| Grade 10-12 | 11 steps |
| Grade 13-15 | 9 steps |

### 4.2 Salary Scale Table (From Official Document)

**Grade 2 (15 steps):**
| Step | Annual Salary (₦) |
|------|------------------|
| 1 | 938,074 |
| 2 | 947,088 |
| 3 | 960,741 |
| 4 | 975,575 |
| 5 | 986,409 |
| 6 | 999,243 |
| 7 | 1,012,076 |
| 8 | 1,029,098 |
| 9 | 1,037,744 |
| 10 | 1,057,518 |
| 11 | 1,071,151 |
| 12 | 1,076,745 |
| 13 | 1,089,079 |
| 14 | 1,101,913 |
| 15 | 1,076,195 |

**[Complete salary scale for all grades 2-15 with all steps is provided in the attached PDF]**

### 4.3 Database Model

```python
class SalaryScale(db.Model):
    __tablename__ = 'salary_scale'
    
    id = db.Column(db.Integer, primary_key=True)
    conraiss_grade = db.Column(db.Integer, nullable=False, index=True)
    step = db.Column(db.Integer, nullable=False)
    annual_salary = db.Column(db.Numeric(12, 2), nullable=False)
    effective_date = db.Column(db.Date, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    __table_args__ = (
        db.UniqueConstraint('conraiss_grade', 'step', 'effective_date', name='unique_grade_step_date'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'conraiss_grade': self.conraiss_grade,
            'step': self.step,
            'annual_salary': float(self.annual_salary),
            'effective_date': self.effective_date.isoformat() if self.effective_date else None
        }
```

### 4.4 Salary Scale Data Import

**Implementation Note:** Create a database seed script to import all salary data from the official CONRAISS document.

```python
# seed_salary_scale.py
def seed_salary_scale():
    """Import salary scale data from official CONRAISS table."""
    salary_data = [
        # Grade 2
        (2, 1, 938074),
        (2, 2, 947088),
        # ... (all entries from the PDF)
    ]
    
    for grade, step, salary in salary_data:
        scale = SalaryScale(
            conraiss_grade=grade,
            step=step,
            annual_salary=salary,
            effective_date=date(2024, 1, 1),  # Effective date
            is_active=True
        )
        db.session.add(scale)
    
    db.session.commit()
```

---

## 5. Promotion Step Allocation Logic

### 5.1 Business Rule

**When a staff member is promoted to a higher CONRAISS grade, their new step must ensure a financial increment from their previous position.**

### 5.2 Step Allocation Algorithm

```python
def calculate_promotion_step(current_grade, current_step, new_grade):
    """
    Calculate the appropriate step in the new grade that ensures salary increment.
    
    Args:
        current_grade: Current CONRAISS grade
        current_step: Current step in current grade
        new_grade: Target CONRAISS grade after promotion
    
    Returns:
        new_step: Recommended step in new grade
        new_salary: Annual salary at new step
    """
    # Get current salary
    current_salary_record = SalaryScale.query.filter_by(
        conraiss_grade=current_grade,
        step=current_step,
        is_active=True
    ).first()
    
    if not current_salary_record:
        raise ValueError(f"Salary not found for Grade {current_grade} Step {current_step}")
    
    current_salary = current_salary_record.annual_salary
    
    # Find minimum step in new grade where salary > current salary
    new_grade_salaries = SalaryScale.query.filter_by(
        conraiss_grade=new_grade,
        is_active=True
    ).order_by(SalaryScale.step).all()
    
    for salary_record in new_grade_salaries:
        if salary_record.annual_salary > current_salary:
            return salary_record.step, salary_record.annual_salary
    
    # If no step provides increment (edge case), return highest step
    highest_step = new_grade_salaries[-1]
    return highest_step.step, highest_step.annual_salary
```

### 5.3 Example

**Current Position:**
- Grade 7, Step 6
- Salary: ₦1,213,851 (from salary table)

**Promoted to Grade 8:**
- System finds minimum step in Grade 8 where salary > ₦1,213,851
- Grade 8, Step 4 = ₦1,256,525 ✅
- **Allocated Step: 4**

### 5.4 Manual Override

HR Admin can manually adjust the allocated step if needed (with justification logged in audit trail).

---

## 6. Annual Step Increment (Automated)

### 6.1 Business Rule

**Every staff member receives an automatic +1 step increment at the beginning of each year (January 1st), provided they have not reached the maximum step for their grade.**

### 6.2 Automated Process

**Trigger:** Scheduled job runs on January 1st at 00:00 (midnight)

**Process:**
1. Query all active staff members
2. For each staff:
   - Check current grade and step
   - Check maximum step for their grade
   - If `current_step < max_step`, increment by 1
   - Update salary based on new step
   - Log the increment in `StepIncrementLog`
3. Send email notification to each staff about their step increment
4. Generate summary report for HR

### 6.3 Implementation

```python
from celery import Celery
from datetime import datetime

@celery.task
def process_annual_step_increment():
    """
    Automated annual step increment for all staff.
    Runs on January 1st at 00:00.
    """
    # Maximum steps by grade
    max_steps = {
        range(2, 10): 15,   # Grades 2-9: 15 steps
        range(10, 13): 11,  # Grades 10-12: 11 steps
        range(13, 16): 9    # Grades 13-15: 9 steps
    }
    
    # Get all active staff
    active_staff = User.query.filter_by(is_active=True).all()
    
    increment_count = 0
    skipped_count = 0
    
    for staff in active_staff:
        # Determine max step for staff's grade
        max_step = None
        for grade_range, steps in max_steps.items():
            if staff.conraiss_grade in grade_range:
                max_step = steps
                break
        
        if not max_step:
            continue
        
        # Check if eligible for increment
        if staff.conraiss_step < max_step:
            # Log the increment
            log = StepIncrementLog(
                user_id=staff.id,
                previous_step=staff.conraiss_step,
                new_step=staff.conraiss_step + 1,
                increment_date=datetime.now().date(),
                increment_type='Annual',
                processed_by=None  # System-generated
            )
            db.session.add(log)
            
            # Update staff step
            staff.conraiss_step += 1
            increment_count += 1
            
            # Send notification
            send_step_increment_notification(staff)
        else:
            skipped_count += 1
    
    db.session.commit()
    
    # Generate HR report
    generate_step_increment_report(increment_count, skipped_count)
    
    return {
        'incremented': increment_count,
        'skipped': skipped_count,
        'total': len(active_staff)
    }
```

### 6.4 Celery Beat Schedule

```python
# celeryconfig.py
from celery.schedules import crontab

beat_schedule = {
    'annual-step-increment': {
        'task': 'tasks.process_annual_step_increment',
        'schedule': crontab(month_of_year=1, day_of_month=1, hour=0, minute=0),
    },
}
```

### 6.5 Database Model

```python
class StepIncrementLog(db.Model):
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
```

---

## 7. RRR Allocation (Rank-Based System)

### 7.1 Critical Clarification

**The entire RRR system is RANK-BASED, not threshold-based.**

- Promotion, Recognition, and Reward are all allocated based on ranking
- Vacancies are limited and set per CONRAISS grade
- Staff can receive multiple RRR types in one cycle

### 7.2 Vacancy Configuration

**Vacancies are set PER CONRAISS GRADE:**

Example configuration:
- Grade 8: 5 promotion vacancies, 10 recognition slots, 15 reward slots
- Grade 9: 3 promotion vacancies, 8 recognition slots, 12 reward slots
- Grade 10: 2 promotion vacancies, 5 recognition slots, 8 reward slots

### 7.3 RRR Allocation Algorithm

```python
def allocate_rrr_for_grade(grade, promotion_vacancies, recognition_slots, reward_slots):
    """
    Allocate RRR for a specific CONRAISS grade based on ranking.
    
    Args:
        grade: CONRAISS grade (e.g., 8)
        promotion_vacancies: Number of promotion spots available
        recognition_slots: Number of recognition awards
        reward_slots: Number of reward recipients
    
    Returns:
        Dictionary with promoted, recognized, and rewarded staff
    """
    # Get all eligible candidates for this grade
    eligible_candidates = get_eligible_candidates_for_grade(grade)
    
    # Calculate combined scores for all candidates
    for candidate in eligible_candidates:
        candidate.exam_score = get_exam_score(candidate)
        candidate.pms_score = get_pms_score(candidate)
        candidate.seniority_score = calculate_seniority_score(candidate, eligible_candidates)
        candidate.combined_score = (
            (candidate.exam_score * 0.70) +
            (candidate.pms_score * 0.20) +
            (candidate.seniority_score * 0.10)
        )
    
    # Sort by combined score (descending), then by seniority tie-breaking
    ranked_candidates = sorted(eligible_candidates, key=lambda x: (
        -x.combined_score,  # Higher score first
        -x.conraiss_step,   # Tie-break: higher step
        x.confirmation_date if x.confirmation_date else datetime.max.date(),
        x.date_of_birth if x.date_of_birth else datetime.max.date(),
        x.file_no
    ))
    
    # Allocate promotions (top N)
    promoted = ranked_candidates[:promotion_vacancies]
    
    # Allocate recognition (can overlap with promotion)
    recognized = ranked_candidates[:recognition_slots]
    
    # Allocate rewards (can overlap with promotion and recognition)
    rewarded = ranked_candidates[:reward_slots]
    
    return {
        'promoted': promoted,
        'recognized': recognized,
        'rewarded': rewarded,
        'ranked_list': ranked_candidates
    }
```

### 7.4 Multiple RRR Types

**A staff member CAN receive multiple RRR types in one cycle.**

Example:
- Staff ranks 1st in Grade 8 promotion candidates
- They receive:
  - ✅ Promotion (top 5)
  - ✅ Recognition (top 10)
  - ✅ Reward (top 15)

### 7.5 Database Model

```python
class RRRVacancy(db.Model):
    __tablename__ = 'rrr_vacancy'
    
    id = db.Column(db.Integer, primary_key=True)
    conraiss_grade = db.Column(db.Integer, nullable=False)
    promotion_cycle = db.Column(db.String(50), nullable=False)  # e.g., "2024"
    promotion_vacancies = db.Column(db.Integer, default=0)
    recognition_slots = db.Column(db.Integer, default=0)
    reward_slots = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('conraiss_grade', 'promotion_cycle', name='unique_grade_cycle'),
    )
```

### 7.6 RRR Recommendation Model (Updated)

```python
class RRRRecommendation(db.Model):
    __tablename__ = 'rrr_recommendation'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    promotion_cycle = db.Column(db.String(50), nullable=False)
    conraiss_grade = db.Column(db.Integer, nullable=False)  # Current grade
    
    # Scores
    exam_score = db.Column(db.Float)
    pms_score = db.Column(db.Float)
    seniority_score = db.Column(db.Float)
    combined_score = db.Column(db.Float)
    
    # Ranking
    rank_in_grade = db.Column(db.Integer)  # Rank within their grade
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
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='rrr_recommendations')
    recommender = db.relationship('User', foreign_keys=[recommended_by])
    approver = db.relationship('User', foreign_keys=[approved_by])
```

---

## 8. Promotion Eligibility Rules

### 8.1 CONRAISS Grade-Based Eligibility

| CONRAISS Grade | Standard Eligibility Cycle | After Failed Promotion |
|----------------|---------------------------|------------------------|
| 2-5 | Every **2 years** | Eligible **every year** |
| 6-12 | Every **3 years** | Eligible **every year** |
| 13-14 | Every **4 years** | Eligible **every year** |

### 8.2 Additional Eligibility Conditions

1. **Vacancy Available:** Must be vacancy in target grade
2. **No Disciplinary Actions:** No active disciplinary proceedings
3. **Minimum PMS Score:** Must meet minimum PMS threshold (configurable, e.g., 60%)
4. **Exam Passed:** Must have taken and passed promotional exam

### 8.3 Eligibility Calculation Function

```python
def is_eligible_for_promotion(user, target_grade):
    """
    Determine if a user is eligible for promotion to target grade.
    """
    # Check if there's a vacancy for target grade
    vacancy = RRRVacancy.query.filter_by(
        conraiss_grade=target_grade,
        promotion_cycle=current_promotion_cycle(),
        is_active=True
    ).first()
    
    if not vacancy or vacancy.promotion_vacancies == 0:
        return False, "No vacancy available"
    
    # Check disciplinary status
    if has_active_disciplinary_action(user):
        return False, "Active disciplinary action"
    
    # Calculate years since last promotion
    if user.date_of_last_promotion:
        years_since_promotion = (datetime.now().date() - user.date_of_last_promotion).days / 365.25
    else:
        years_since_promotion = user.years_since_first_appointment
    
    # Determine standard cycle based on current grade
    if user.conraiss_grade in [2, 3, 4, 5]:
        standard_cycle = 2
    elif user.conraiss_grade in range(6, 13):
        standard_cycle = 3
    elif user.conraiss_grade in [13, 14]:
        standard_cycle = 4
    else:
        return False, "Invalid CONRAISS grade"
    
    # Edge case: If staff has failed promotion before, eligible every year
    if user.failed_promotion_attempts > 0:
        if years_since_promotion >= 1:
            return True, "Eligible (failed previous attempt)"
        else:
            return False, f"Must wait until {user.date_of_last_promotion.year + 1}"
    
    # Standard case
    if years_since_promotion >= standard_cycle:
        return True, "Eligible (standard cycle)"
    else:
        return False, f"Must wait until {user.date_of_last_promotion.year + standard_cycle}"
```

---

## 9. User Data Import Specification

### 9.1 CSV Import Columns (Complete List)

**Required Columns:**

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| `employee_id` | String | Unique employee identifier | EMP001234 |
| `first_name` | String | First name | John |
| `last_name` | String | Last name | Doe |
| `email` | String | Email address (unique) | john.doe@nbti.gov.ng |
| `department` | String | Department name | ICT Department |
| `position` | String | Job title | Senior Officer |
| `rank` | String | Official rank | Senior Officer II |
| `cadre` | String | Staff cadre | Administrative |
| `conraiss_grade` | Integer | CONRAISS grade (2-15) | 8 |
| `conraiss_step` | Integer | Current step | 5 |
| `ippis_number` | String | IPPIS number | IPPIS123456 |
| `date_of_birth` | Date | Date of birth (YYYY-MM-DD) | 1985-05-15 |
| `state_of_origin` | String | State of origin | Lagos |
| `local_government_area` | String | LGA | Ikeja |
| `file_no` | String | File number | FILE/2018/1234 |
| `date_of_first_appointment` | Date | First appointment date | 2018-03-01 |
| `confirmation_date` | Date | Confirmation date | 2019-03-01 |
| `qualifications` | String | Academic qualifications | BSc Computer Science, MSc IT |

**Optional Columns:**

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| `phone_number` | String | Phone number | +234-xxx-xxx-xxxx |
| `date_of_last_promotion` | Date | Last promotion date | 2020-01-15 |
| `gender` | String | Gender (Male/Female/Other) | Male |
| `office_location` | String | Office location | Abuja HQ |
| `supervisor_employee_id` | String | Supervisor's employee ID | EMP005678 |

### 9.2 Auto-Generated Fields

The system will automatically generate:
- `username` - Derived from employee_id (e.g., EMP001234 → emp001234)
- `temporary_password` - Random 12-character password
- `roles` - Default: ["Staff Member"]

### 9.3 Import Behavior

**Supervisor Assignment:**
- If `supervisor_employee_id` doesn't exist → Skip, assign later via UI
- If `supervisor_employee_id` is blank → Skip, assign later via UI

**Confirmation Status:**
- If `confirmation_date` is blank → Staff is on probation
- If `confirmation_date` is provided → Staff is confirmed

**Date of Last Promotion:**
- If blank → Use `date_of_first_appointment` as default

### 9.4 Import Validation Rules

1. **employee_id:** Must be unique, cannot be blank
2. **email:** Must be unique, valid email format
3. **conraiss_grade:** Must be between 2-15
4. **conraiss_step:** Must be valid for the grade (check max steps)
5. **date_of_birth:** Must be at least 18 years ago
6. **date_of_first_appointment:** Cannot be in the future
7. **confirmation_date:** Must be after date_of_first_appointment (if provided)

### 9.5 Bulk Import API Endpoint

```python
@user_bp.route('/users/bulk-import', methods=['POST'])
@jwt_required()
@require_role('HR Admin')
def bulk_import_users():
    """
    Bulk import users from CSV file.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be CSV format'}), 400
    
    # Parse CSV
    import csv
    import io
    
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_reader = csv.DictReader(stream)
    
    imported = 0
    errors = []
    
    for row_num, row in enumerate(csv_reader, start=2):
        try:
            # Validate and create user
            user = create_user_from_csv_row(row)
            db.session.add(user)
            imported += 1
        except Exception as e:
            errors.append({
                'row': row_num,
                'error': str(e),
                'data': row
            })
    
    if imported > 0:
        db.session.commit()
    
    return jsonify({
        'imported': imported,
        'errors': errors,
        'total_rows': imported + len(errors)
    }), 200 if not errors else 207
```

---

## 10. Complete Database Schema

### 10.1 Updated User Model

```python
class User(db.Model):
    __tablename__ = 'user'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Authentication
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Personal Information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    phone_number = db.Column(db.String(20))
    
    # Employee Information
    employee_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    ippis_number = db.Column(db.String(50), unique=True)
    file_no = db.Column(db.String(50))
    
    # Organizational Information
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    rank = db.Column(db.String(100))
    cadre = db.Column(db.String(100))
    office_location = db.Column(db.String(100))
    
    # CONRAISS Information
    conraiss_grade = db.Column(db.Integer, index=True)  # 2-15
    conraiss_step = db.Column(db.Integer)  # 1-15 (varies by grade)
    
    # Dates
    date_of_first_appointment = db.Column(db.Date)
    confirmation_date = db.Column(db.Date)
    date_of_last_promotion = db.Column(db.Date)
    
    # Geographic Information
    state_of_origin = db.Column(db.String(100))
    local_government_area = db.Column(db.String(100))
    
    # Education
    qualifications = db.Column(db.Text)
    
    # Hierarchy
    supervisor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Promotion Tracking
    failed_promotion_attempts = db.Column(db.Integer, default=0)
    last_rrr_date = db.Column(db.Date)
    last_rrr_type = db.Column(db.String(50))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    roles = db.relationship('Role', secondary='user_roles', backref='users')
    supervisor = db.relationship('User', remote_side=[id], backref='subordinates')
    
    # Calculated Properties
    @property
    def is_confirmed(self):
        return self.confirmation_date is not None
    
    @property
    def years_since_first_appointment(self):
        if self.date_of_first_appointment:
            return (datetime.now().date() - self.date_of_first_appointment).days / 365.25
        return 0
    
    @property
    def time_in_grade(self):
        if self.date_of_last_promotion:
            return (datetime.now().date() - self.date_of_last_promotion).days / 365.25
        return self.years_since_first_appointment
    
    @property
    def current_salary(self):
        """Get current annual salary based on grade and step."""
        salary_record = SalaryScale.query.filter_by(
            conraiss_grade=self.conraiss_grade,
            step=self.conraiss_step,
            is_active=True
        ).first()
        return float(salary_record.annual_salary) if salary_record else 0
    
    def calculate_seniority_score(self, candidates_in_same_grade):
        """Calculate seniority score using priority-based ranking."""
        # Implementation as described in Section 3.3
        pass
```

### 10.2 All Database Models Summary

**Existing Models (Updated):**
1. User (extended with seniority fields)
2. Role
3. UserRoles (association table)
4. PMSEvaluation (extended)
5. PMSGoal (extended)
6. EMMQuestion
7. EMMOption
8. EMMExam (extended)
9. EMMExamSubmission (extended)
10. EMMSubmissionAnswer

**New Models:**
11. SalaryScale
12. StepIncrementLog
13. RRRVacancy
14. RRRRecommendation
15. PMSCycle
16. Appeal
17. AuditLog (enhanced)
18. SystemConfiguration
19. Notification
20. DevelopmentNeed

---

## 11. Implementation Roadmap

### Phase 1: Critical Foundation (Weeks 1-3)

**Priority 0 - Must Have:**

1. **Database Schema Implementation**
   - Create all new models (SalaryScale, StepIncrementLog, RRRVacancy, RRRRecommendation, etc.)
   - Add new fields to existing models (User, PMSEvaluation, PMSGoal, etc.)
   - Create migration scripts
   - Seed salary scale data from CONRAISS document
   - **Effort:** Very High | **Impact:** Critical

2. **Corrected RRR Calculation**
   - Implement: `Combined Score = (Exam × 0.70) + (PMS × 0.20) + (Seniority × 0.10)`
   - Implement priority-based seniority calculation
   - **Effort:** High | **Impact:** Critical

3. **Rank-Based RRR Allocation**
   - Implement ranking algorithm per CONRAISS grade
   - Implement vacancy management (per grade)
   - Support multiple RRR types per staff
   - **Effort:** High | **Impact:** Critical

4. **Promotion Step Allocation**
   - Implement step allocation algorithm (salary increment guarantee)
   - Manual override capability for HR
   - **Effort:** Medium | **Impact:** Critical

5. **Promotion Eligibility Logic**
   - CONRAISS grade-based eligibility (2-5: 2yr, 6-12: 3yr, 13-14: 4yr)
   - Edge case: Failed promotion → eligible every year
   - Vacancy checking per grade
   - **Effort:** High | **Impact:** Critical

6. **Annual Step Increment (Automated)**
   - Celery task for January 1st automation
   - Step increment logic with max step checking
   - Notification system
   - **Effort:** Medium | **Impact:** Critical

7. **Forensic Audit Logging**
   - UUID-based tamper-proof logs
   - Log all RRR decisions with before/after values
   - **Effort:** High | **Impact:** Critical

8. **AWS S3 Integration**
   - File upload/download for evidence
   - Signed URLs for secure access
   - **Effort:** Medium | **Impact:** Critical

9. **Bulk User Import**
   - CSV import with 18+ fields
   - Validation and error handling
   - Auto-generate username/password
   - **Effort:** Medium | **Impact:** Critical

### Phase 2: Core Workflows (Weeks 4-5)

10. **Second-Level Review (Calibration)**
    - Director review interface
    - Outlier detection algorithm
    - Calibration reports
    - **Effort:** High | **Impact:** High

11. **Appeal Process**
    - Appeal submission form
    - Appeal review workflow
    - Appeal tracking dashboard
    - **Effort:** Medium | **Impact:** High

12. **Email Notification System**
    - SMTP integration
    - Notification templates
    - Trigger points
    - **Effort:** Medium | **Impact:** High

13. **Staff Self-Evaluation**
    - Self-rating interface
    - Evidence upload (S3)
    - **Effort:** Medium | **Impact:** High

14. **Mid-Quarter Review Tracking**
    - Mid-quarter review form
    - Goal adjustment workflow
    - **Effort:** Low | **Impact:** Medium

### Phase 3: User Management & Configuration (Week 6)

15. **User Management UI**
    - User CRUD operations
    - Supervisor assignment
    - CONRAISS grade/step management
    - **Effort:** High | **Impact:** High

16. **Settings/Configuration UI**
    - PMS cycle management
    - RRR vacancy configuration (per grade)
    - System configuration
    - **Effort:** Medium | **Impact:** High

17. **Salary Scale Management**
    - View salary scale
    - Update salary scale (for future adjustments)
    - Historical tracking
    - **Effort:** Low | **Impact:** Medium

### Phase 4: Reporting & Analytics (Weeks 7-8)

18. **Essential Reports**
    - Personal Performance Report
    - Team Performance Overview
    - RRR Ranking Report (per grade)
    - Promotion Eligibility Report
    - Step Increment Report
    - Calibration Reports
    - Audit Log Reports
    - **Effort:** Very High | **Impact:** High

19. **Export Functionality**
    - PDF export
    - Excel export
    - **Effort:** Medium | **Impact:** Medium

20. **Dashboard Visualizations**
    - Charts and graphs
    - Performance trends
    - Rating distributions
    - **Effort:** Medium | **Impact:** Medium

### Phase 5: EMM Enhancements (Week 9)

21. **Manual Grading Interface**
    - Grader assignment
    - Essay grading UI
    - **Effort:** High | **Impact:** Medium

22. **Exam Randomization**
    - Question/option randomization
    - **Effort:** Low | **Impact:** Low

### Phase 6: Testing & Documentation (Weeks 10-11)

23. **Comprehensive Testing**
    - Unit tests (80% coverage)
    - Integration tests
    - E2E tests
    - Load testing
    - **Effort:** Very High | **Impact:** Critical

24. **Documentation**
    - API documentation
    - User manuals
    - Admin guide
    - **Effort:** High | **Impact:** High

---

## 12. Critical Business Rules Summary

### 12.1 RRR Scoring

```
Combined Score = (Exam × 0.70) + (PMS × 0.20) + (Seniority × 0.10)
```

### 12.2 Seniority Priority

1. **Step** (highest priority)
2. **Confirmation Date**
3. **Age**
4. **File Number** (lowest priority)

### 12.3 Promotion Eligibility

| CONRAISS Grade | Standard Cycle | After Failed Attempt |
|----------------|----------------|----------------------|
| 2-5 | Every 2 years | Every year |
| 6-12 | Every 3 years | Every year |
| 13-14 | Every 4 years | Every year |

### 12.4 RRR Allocation

- **Rank-based** with limited vacancies per grade
- Staff can receive **multiple RRR types** in one cycle
- Vacancies set **per CONRAISS grade**

### 12.5 Step Increment

- **Automatic** on January 1st each year
- +1 step (if not at maximum)
- Fully automated via Celery

### 12.6 Promotion Step Allocation

- New step must ensure **salary increment** from previous position
- System calculates minimum step automatically
- HR can manually override

### 12.7 Data Retention

- Performance data: **10 years**
- Audit logs: **10 years**
- Forensic-level detail required

---

## Document Control

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Oct 23, 2025 | Initial analysis | Manus AI |
| 2.0 | Oct 23, 2025 | Updated with client answers, corrected RRR formula | Manus AI |
| 3.0 | Oct 24, 2025 | **FINAL** - Seniority system, salary scale, rank-based RRR, all questions answered | Manus AI |

---

## ✅ DOCUMENT STATUS: COMPLETE AND APPROVED FOR IMPLEMENTATION

All ambiguities resolved. All questions answered. Ready to begin development.

---

**Document End**


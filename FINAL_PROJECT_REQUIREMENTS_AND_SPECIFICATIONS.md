# NBTI Promotion Automation System: Final Requirements and Specifications

**Author:** Manus AI  
**Date:** October 23, 2025  
**Document Version:** 2.0 (Updated with Client Answers)

---

## Executive Summary

This document consolidates all project requirements, specifications, and clarifications for the NBTI Promotion Automation System. It incorporates answers to all outstanding questions and corrects the RRR scoring formula.

---

## 1. Corrected RRR Scoring Formula

### **CRITICAL CORRECTION**

The promotion score calculation is:

```
Final Promotion Score = (Exam Score × 0.70) + (PMS Score × 0.20) + (Seniority Score × 0.10)
```

**Component Breakdown:**
- **Exam Score: 70%** - Performance on promotional examination
- **PMS Score: 20%** - Quarterly performance evaluation average
- **Seniority Score: 10%** - Based on years of service and time in current grade

### **Seniority Calculation Requirements**

The system must calculate seniority score based on:
- **Years of Service** at NBTI
- **Time in Current Grade** (years since last promotion)

**Implementation Note:** The exact seniority scoring algorithm needs to be defined. Suggested approach:
- Seniority Score = MIN(100, (Years in Grade / Expected Years in Grade) × 100)
- Where Expected Years in Grade varies by CONRAISS level (see eligibility rules below)

---

## 2. RRR Policy - Complete Specifications

### 2.1 RRR Thresholds (Dynamic Configuration)

**Requirement:** RRR thresholds must be **configurable by HR Admin** through the system UI.

**Database Design:**
```
RRRThreshold Model:
- threshold_name (e.g., "Promotion - Excellent")
- rrr_type (Recommendation/Recognition/Reward)
- min_score (e.g., 85.0)
- max_score (e.g., 100.0)
- description
- is_active
- effective_date
- created_by
- updated_at
```

**UI Requirements:**
- HR Admin can create, edit, and deactivate thresholds
- Historical threshold data must be preserved (for audit trail)
- System uses the active threshold at the time of evaluation
- Validation: Thresholds cannot overlap for the same RRR type

**Suggested Default Thresholds (configurable):**
- **Promotion (Recommendation):** ≥ 80%
- **Recognition:** 70-79%
- **Reward:** 60-69%
- **No RRR:** < 60%

### 2.2 RRR Frequency Rules

**Promotion:**
- Frequency: Once every **3 years** (after successful promotion)
- Exception: Staff can be eligible more frequently if they fail promotion (see eligibility rules)

**Recognition and Reward (excluding Promotion):**
- Frequency: Once every **1 year**
- Staff can receive recognition/reward annually even if not eligible for promotion

**Implementation:**
- Track `last_promotion_date` in User model
- Track `last_rrr_date` and `last_rrr_type` in User model
- Validation logic to prevent RRR awards outside frequency rules

### 2.3 Promotion Eligibility Rules (CONRAISS Grade-Based)

**Critical Business Rule:** Eligibility varies by CONRAISS grade level.

| CONRAISS Grade | Standard Eligibility Cycle | Edge Case (Failed Promotion) |
|----------------|---------------------------|------------------------------|
| 2-5 | Every **2 years** | Eligible **every year** until promoted |
| 6-12 | Every **3 years** | Eligible **every year** until promoted |
| 13-14 | Every **4 years** | Eligible **every year** until promoted |

**Additional Conditions:**
- Must have vacancy in target position
- No active disciplinary actions
- Minimum PMS performance (configurable threshold)

**Edge Case Handling:**
When a staff member becomes eligible for the first time but fails to be promoted:
- They become eligible to take the exam **every year** thereafter
- This continues until they are successfully promoted OR there is no vacancy
- Once promoted, the standard cycle resets

**Database Requirements:**
- `User.conraiss_grade` (integer, 2-14)
- `User.date_of_last_promotion`
- `User.promotion_eligibility_status` (Eligible/Not Eligible/Pending)
- `User.failed_promotion_attempts` (counter)

**Eligibility Calculation Logic:**
```python
def is_eligible_for_promotion(user):
    # Check if there's a vacancy (system-wide setting)
    if not has_vacancy():
        return False
    
    # Check disciplinary status
    if has_active_disciplinary_action(user):
        return False
    
    # Calculate years since last promotion
    years_since_promotion = calculate_years(user.date_of_last_promotion, today)
    
    # Determine standard cycle based on grade
    if user.conraiss_grade in [2, 3, 4, 5]:
        standard_cycle = 2
    elif user.conraiss_grade in range(6, 13):
        standard_cycle = 3
    elif user.conraiss_grade in [13, 14]:
        standard_cycle = 4
    
    # Edge case: If staff has failed promotion before, eligible every year
    if user.failed_promotion_attempts > 0:
        return years_since_promotion >= 1
    
    # Standard case
    return years_since_promotion >= standard_cycle
```

### 2.4 Exam Retake Policy

**Rule:** If a staff member fails a promotional exam:
- They can retake the exam during the **next promotion cycle** (following year)
- They can continue to take the exam **every year** as long as:
  - There is a vacancy
  - They remain eligible

**No Limit:** There is no maximum number of retake attempts.

**Implementation:**
- Track exam attempts in `EMMExamSubmission` model
- Display attempt history to staff and supervisors
- Flag repeated failures for HR review (optional alert)

---

## 3. Calibration Process - Detailed Workflow

### 3.1 Calibration Roles and Responsibilities

**Directors (Second-Level Reviewers):**
- Review all evaluations within their directorate/area
- Identify rating inconsistencies across departments
- Make adjustments to ensure fairness and consistency
- Flag outliers for discussion

**Calibration Committee:**
- Composed of Directors, HR Admin, and senior leadership
- Holds final calibration meetings
- Discusses flagged evaluations
- Makes final promotion decisions
- Approves RRR recommendations

### 3.2 Calibration Workflow Steps

**Step 1: Supervisor Completes First-Level Review**
- Supervisor rates all goals for their subordinates
- Evaluation status: "Pending Second-Level Review"

**Step 2: System Flags Outliers (Automated)**
- System analyzes rating distributions within each directorate
- Flags evaluations that are statistical outliers:
  - Ratings significantly higher than department average
  - Ratings significantly lower than department average
  - Inconsistent ratings (high variance across goals)

**Step 3: Director Reviews Evaluations**
- Director views all evaluations in their area
- Reviews flagged outliers
- Can adjust ratings with justification
- Adds calibration comments
- Marks evaluation as "Calibrated" or "Flagged for Committee"

**Step 4: Calibration Committee Meeting**
- Committee reviews all flagged evaluations
- Discusses edge cases and disputes
- Makes final adjustments
- Approves final ratings

**Step 5: Finalization**
- HR Admin finalizes all evaluations
- System calculates final PMS scores
- System calculates combined promotion scores (Exam + PMS + Seniority)
- RRR recommendations are generated

### 3.3 Calibration Reports

**Pre-Calibration Reports:**
- Rating distribution by department (histogram)
- List of statistical outliers
- Supervisor leniency/severity analysis

**Post-Calibration Reports:**
- Before/after rating comparison
- Calibration adjustment summary
- Final rating distribution

---

## 4. Appeal Process - Complete Specifications

### 4.1 Grounds for Appeal

Staff can appeal their performance evaluation if:
- They feel the evaluation is **not a true reflection** of their performance
- They believe they were **victimized** or unfairly rated
- They have evidence that contradicts the supervisor's assessment
- They disagree with the **calibration adjustments**

### 4.2 Appeal Workflow

**Step 1: Staff Submits Appeal**
- Staff member submits appeal within **14 days** of evaluation finalization
- Must provide:
  - Reason for appeal
  - Supporting evidence (documents, emails, etc.)
  - Specific goals/ratings being contested

**Step 2: Appeal Review Assignment**
- System assigns appeal to:
  - HR Admin (for procedural issues)
  - Director (for rating disputes)
  - Appeal Committee (for complex cases)

**Step 3: Appeal Investigation**
- Reviewer examines evidence
- May request additional information from staff and supervisor
- Reviews original evaluation and supporting documents

**Step 4: Appeal Decision**
- Reviewer makes decision:
  - **Upheld** - Appeal is valid, evaluation is adjusted
  - **Partially Upheld** - Some adjustments made
  - **Rejected** - Original evaluation stands
- Decision includes detailed justification

**Step 5: Notification**
- Staff member is notified of decision
- If upheld, evaluation is updated and PMS score recalculated
- Appeal decision is final (no further appeals)

### 4.3 Appeal Tracking

**Database Model:**
```
Appeal Model:
- evaluation_id (FK)
- appellant_id (FK to User)
- appeal_reason (text)
- supporting_evidence (file references)
- contested_goals (JSON array of goal IDs)
- status (Submitted/Under Review/Resolved)
- assigned_to (FK to User)
- resolution (Upheld/Partially Upheld/Rejected)
- resolution_details (text)
- resolved_by (FK to User)
- resolved_at (timestamp)
- created_at
```

**Appeal Reports:**
- Appeal tracking dashboard for HR
- Appeal resolution timeline
- Appeal outcome statistics

---

## 5. Goal Management - Specifications

### 5.1 Goal Weights

**Rule:** Goal weights are **not fixed** and **do not need to sum to 100%**.

**Rationale:** Different goals may have different importance levels, and supervisors have flexibility in weighting.

**Calculation Method:**
```
Goal Score = (Rating × Weight) / Sum of All Weights

Example:
Goal 1: Rating 4, Weight 2 → Weighted Score = 4 × 2 = 8
Goal 2: Rating 5, Weight 3 → Weighted Score = 5 × 3 = 15
Goal 3: Rating 3, Weight 1 → Weighted Score = 3 × 1 = 3

Total Weighted Score = 8 + 15 + 3 = 26
Total Weight = 2 + 3 + 1 = 6
Final PMS Score = 26 / 6 = 4.33 (out of 5)
Percentage = (4.33 / 5) × 100 = 86.6%
```

**UI Considerations:**
- Display weight as a number (not percentage)
- Show calculated contribution of each goal to final score
- Allow supervisors to adjust weights during goal setting

### 5.2 Mid-Quarter Review

**Requirement:** Mid-quarter reviews **should be tracked** in the system.

**Implementation:**
- Add `mid_quarter_review_date` to PMSEvaluation model
- Add `mid_quarter_comments` (staff and supervisor)
- Add `goals_adjusted` boolean flag
- Optional: Allow goal modifications during mid-quarter review

**Workflow:**
- System sends reminder at mid-quarter point
- Staff and supervisor meet (offline or online)
- Both parties add comments to the system
- Goals can be adjusted if needed (with approval)
- Mid-quarter review is optional but encouraged

---

## 6. Technical Specifications - Answers to All Questions

### 6.1 User Data and Authentication

**User Data Source:**
- **No existing HRIS integration required**
- User data will be:
  - Self-entered by staff during signup (basic info)
  - Uploaded in bulk by HR Admin (CSV import)
  - Manually entered by HR Admin (individual users)

**Authentication:**
- **No SSO required**
- Use existing JWT-based authentication
- Username/password login
- Password reset via email

**Required User Fields:**
```
User Model (Extended):
- username
- email
- password_hash
- first_name
- last_name
- employee_id (unique)
- department
- position
- conraiss_grade (2-14)
- date_of_hire
- date_of_last_promotion
- supervisor_id (FK to User)
- years_of_service (calculated)
- time_in_grade (calculated)
- is_active
- created_at
- updated_at
```

### 6.2 File Storage

**Storage Solution:** **AWS S3**

**Implementation Requirements:**
- Use boto3 library for S3 integration
- Store files in organized bucket structure:
  - `/evaluations/{evaluation_id}/evidence/`
  - `/appeals/{appeal_id}/documents/`
  - `/exams/{exam_id}/attachments/`
  - `/user-profiles/{user_id}/`

**File Types Allowed:**
- Documents: PDF, DOCX, XLSX
- Images: JPG, PNG
- Max file size: 10MB per file

**Security:**
- Use signed URLs for temporary access
- Files are private by default
- Access controlled by user permissions

### 6.3 Scalability

**Expected Load:**
- **Total Users:** 1,500 staff members
- **Concurrent Users:** Not all will access simultaneously
- **Peak Load:** Estimated 200-300 concurrent users during exam periods

**Infrastructure Sizing:**
- **Backend:** 2-4 application servers (load balanced)
- **Database:** Single PostgreSQL instance with read replicas (optional)
- **Redis:** Single instance for caching and session management
- **S3:** Unlimited storage

**Performance Targets:**
- Page load time: < 2 seconds
- API response time: < 500ms (95th percentile)
- Exam submission: < 1 second

### 6.4 Backup and Disaster Recovery

**Backup Schedule:**
- **Frequency:** Daily automated backups
- **Retention:** 30 days of daily backups, 12 months of monthly backups
- **Scope:** Full database backup + S3 file versioning

**Disaster Recovery:**
- **RTO (Recovery Time Objective):** 4 hours (industry standard for non-critical systems)
- **RPO (Recovery Point Objective):** 24 hours (daily backups)

**Backup Strategy:**
- Automated PostgreSQL backups to S3
- S3 versioning enabled for file storage
- Cross-region replication (optional for critical data)
- Regular backup restoration testing (quarterly)

### 6.5 Deployment Infrastructure

**Cloud Provider:** **AWS**

**Architecture:**
- **Compute:** EC2 instances or ECS (Docker containers)
- **Database:** RDS PostgreSQL
- **Caching:** ElastiCache Redis
- **Storage:** S3
- **Load Balancer:** Application Load Balancer (ALB)
- **CDN:** CloudFront (for static assets)
- **DNS:** Route 53

**Environments:**
- **Development:** Single instance, SQLite or small RDS
- **Staging:** Production-like setup (smaller instances)
- **Production:** Full setup with monitoring

**Database:**
- **PostgreSQL** in all environments (confirmed)
- Version: PostgreSQL 14 or later

**High Availability:**
- **Not a priority** (confirmed)
- Single-region deployment is acceptable
- Optional: Multi-AZ RDS for database redundancy

**Access:**
- **Internet-facing** (confirmed)
- Accessible to anyone with credentials
- No VPN or IP whitelisting required
- HTTPS enforced (SSL/TLS certificate via AWS Certificate Manager)

### 6.6 Compliance and Security

**Data Privacy:**
- **No specific regulations** (GDPR, NDPR) to comply with
- Follow general best practices for data protection

**Data Retention:**
- **Performance Data:** 10 years (internal standard)
- **Audit Logs:** 10 years (internal standard)
- **User Data:** Retained while user is active + 10 years after termination

**Audit Requirements:**
- **Forensic-level audit detail** (critical requirement)
- Track every action in the system:
  - Who did what, when, where (IP address)
  - Before and after values for all changes
  - Especially critical for RRR decisions
- Audit logs must be tamper-proof (append-only)
- Audit log viewing restricted to HR Admin and Directors

**Audit Log Model:**
```
AuditLog Model:
- id (UUID)
- user_id (FK)
- action_type (CREATE/UPDATE/DELETE/VIEW/APPROVE/REJECT)
- entity_type (Evaluation/Goal/Exam/User/RRR)
- entity_id
- old_value (JSON)
- new_value (JSON)
- ip_address
- user_agent
- session_id
- timestamp
- is_sensitive (flag for RRR decisions)
```

**Access Control:**
- Role-based access control (already implemented)
- No IP whitelisting required
- No VPN requirement
- Strong password enforcement (already implemented)
- Session timeout: 30 minutes of inactivity

---

## 7. Updated Database Schema Requirements

### 7.1 New Models to Implement

**1. RRRThreshold**
```python
class RRRThreshold(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    threshold_name = db.Column(db.String(100), nullable=False)
    rrr_type = db.Column(db.String(50), nullable=False)  # Promotion/Recognition/Reward
    min_score = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    effective_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
```

**2. RRRRecommendation**
```python
class RRRRecommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('pms_evaluation.id'))
    exam_submission_id = db.Column(db.Integer, db.ForeignKey('emm_exam_submission.id'))
    
    # Scores
    exam_score = db.Column(db.Float)  # Out of 100
    pms_score = db.Column(db.Float)   # Out of 100
    seniority_score = db.Column(db.Float)  # Out of 100
    combined_score = db.Column(db.Float)  # Final weighted score
    
    # RRR Details
    rrr_type = db.Column(db.String(50))  # Promotion/Recognition/Reward
    recommendation_details = db.Column(db.Text)
    
    # Workflow
    status = db.Column(db.String(50), default='Pending')  # Pending/Approved/Rejected
    recommended_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approval_date = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
```

**3. Appeal**
```python
class Appeal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('pms_evaluation.id'), nullable=False)
    appellant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Appeal Details
    appeal_reason = db.Column(db.Text, nullable=False)
    supporting_evidence = db.Column(db.JSON)  # Array of S3 file URLs
    contested_goals = db.Column(db.JSON)  # Array of goal IDs
    
    # Workflow
    status = db.Column(db.String(50), default='Submitted')
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    resolution = db.Column(db.String(50))  # Upheld/Partially Upheld/Rejected
    resolution_details = db.Column(db.Text)
    resolved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    resolved_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
```

**4. PMSCycle**
```python
class PMSCycle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cycle_name = db.Column(db.String(100), nullable=False)  # e.g., "Q1 2024"
    quarter = db.Column(db.String(10))  # Q1, Q2, Q3, Q4
    year = db.Column(db.Integer)
    
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
    status = db.Column(db.String(50), default='Planning')  # Planning/Active/Closed
    is_active = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
```

**5. AuditLog (Enhanced)**
```python
class AuditLog(db.Model):
    id = db.Column(db.String(36), primary_key=True)  # UUID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Action Details
    action_type = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer)
    
    # Change Tracking
    old_value = db.Column(db.JSON)
    new_value = db.Column(db.JSON)
    
    # Security Context
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    session_id = db.Column(db.String(100))
    
    # Flags
    is_sensitive = db.Column(db.Boolean, default=False)  # RRR decisions
    
    # Timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
```

**6. SystemConfiguration**
```python
class SystemConfiguration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False)
    config_value = db.Column(db.Text)
    config_type = db.Column(db.String(50))  # string/integer/boolean/json
    description = db.Column(db.Text)
    is_editable = db.Column(db.Boolean, default=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
```

**Example Configuration Keys:**
- `promotion_vacancy_available` (boolean)
- `exam_score_weight` (0.70)
- `pms_score_weight` (0.20)
- `seniority_score_weight` (0.10)
- `min_pms_score_for_exam_eligibility` (60.0)
- `appeal_deadline_days` (14)

### 7.2 Updated Existing Models

**User Model - Add Fields:**
```python
# Add to existing User model
employee_id = db.Column(db.String(50), unique=True)
department = db.Column(db.String(100))
position = db.Column(db.String(100))
conraiss_grade = db.Column(db.Integer)  # 2-14
date_of_hire = db.Column(db.Date)
date_of_last_promotion = db.Column(db.Date)
supervisor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
failed_promotion_attempts = db.Column(db.Integer, default=0)
last_rrr_date = db.Column(db.Date)
last_rrr_type = db.Column(db.String(50))

# Calculated properties
@property
def years_of_service(self):
    if self.date_of_hire:
        return (datetime.now().date() - self.date_of_hire).days / 365.25
    return 0

@property
def time_in_grade(self):
    if self.date_of_last_promotion:
        return (datetime.now().date() - self.date_of_last_promotion).days / 365.25
    return 0

@property
def seniority_score(self):
    # Calculate seniority score (0-100)
    # Logic based on time_in_grade and expected promotion cycle
    expected_years = {
        range(2, 6): 2,
        range(6, 13): 3,
        range(13, 15): 4
    }
    for grade_range, years in expected_years.items():
        if self.conraiss_grade in grade_range:
            return min(100, (self.time_in_grade / years) * 100)
    return 0
```

**PMSEvaluation Model - Add Fields:**
```python
# Add to existing PMSEvaluation model
cycle_id = db.Column(db.Integer, db.ForeignKey('pms_cycle.id'))
second_level_reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
calibration_comments = db.Column(db.Text)
calibrated_at = db.Column(db.DateTime)
is_flagged_for_calibration = db.Column(db.Boolean, default=False)
flagged_reason = db.Column(db.Text)

# Mid-quarter review
mid_quarter_review_date = db.Column(db.Date)
mid_quarter_staff_comments = db.Column(db.Text)
mid_quarter_supervisor_comments = db.Column(db.Text)
goals_adjusted_mid_quarter = db.Column(db.Boolean, default=False)
```

**PMSGoal Model - Add Fields:**
```python
# Add to existing PMSGoal model
self_rating = db.Column(db.Integer)  # Staff self-assessment (1-5)
self_comments = db.Column(db.Text)
evidence = db.Column(db.JSON)  # Array of S3 file URLs
kra_category = db.Column(db.String(100))  # Key Result Area category
```

**EMMExam Model - Add Fields:**
```python
# Add to existing EMMExam model
randomize_questions = db.Column(db.Boolean, default=False)
randomize_options = db.Column(db.Boolean, default=False)
attempts_allowed = db.Column(db.Integer, default=1)
proctoring_enabled = db.Column(db.Boolean, default=False)
is_promotional_exam = db.Column(db.Boolean, default=False)
target_conraiss_grade = db.Column(db.Integer)  # For promotional exams
```

**EMMExamSubmission Model - Add Fields:**
```python
# Add to existing EMMExamSubmission model
time_remaining = db.Column(db.Integer)  # Seconds remaining (for resume)
ip_address = db.Column(db.String(45))
browser_info = db.Column(db.Text)
attempt_number = db.Column(db.Integer, default=1)
is_flagged = db.Column(db.Boolean, default=False)  # Suspicious activity
flagged_reason = db.Column(db.Text)
```

---

## 8. Implementation Priority (Updated)

### Phase 1: Critical Foundation (Weeks 1-3)

**Priority 0 - Must Have:**

1. **Database Schema Updates**
   - Add all new models (RRRThreshold, RRRRecommendation, Appeal, PMSCycle, AuditLog, SystemConfiguration)
   - Add new fields to existing models (User, PMSEvaluation, PMSGoal, EMMExam, EMMExamSubmission)
   - Create database migration scripts
   - **Effort:** High | **Impact:** Critical

2. **Corrected RRR Calculation**
   - Implement: `Combined Score = (Exam × 0.70) + (PMS × 0.20) + (Seniority × 0.10)`
   - Seniority score calculation based on time in grade
   - **Effort:** Medium | **Impact:** Critical

3. **Promotion Eligibility Logic**
   - CONRAISS grade-based eligibility (2-5: 2yr, 6-12: 3yr, 13-14: 4yr)
   - Edge case: Failed promotion → eligible every year
   - Vacancy checking
   - **Effort:** High | **Impact:** Critical

4. **RRR Threshold Configuration UI**
   - HR Admin can create/edit dynamic thresholds
   - Threshold history tracking
   - **Effort:** Medium | **Impact:** Critical

5. **Forensic Audit Logging**
   - Implement comprehensive audit trail for all actions
   - Special focus on RRR decisions
   - UUID-based tamper-proof logs
   - **Effort:** High | **Impact:** Critical

6. **AWS S3 Integration**
   - File upload/download for evidence and documents
   - Signed URLs for secure access
   - **Effort:** Medium | **Impact:** Critical

### Phase 2: Core Workflows (Weeks 4-5)

**Priority 1 - Should Have:**

7. **Second-Level Review (Calibration)**
   - Director review interface
   - Outlier detection algorithm
   - Rating adjustment with justification
   - Calibration reports
   - **Effort:** High | **Impact:** High

8. **Appeal Process**
   - Appeal submission form
   - Appeal review workflow
   - Appeal tracking dashboard
   - **Effort:** Medium | **Impact:** High

9. **Email Notification System**
   - SMTP integration (already configured)
   - Notification templates
   - Trigger points: cycle start, deadlines, approvals, appeals
   - **Effort:** Medium | **Impact:** High

10. **Staff Self-Evaluation**
    - Self-rating interface
    - Evidence upload (S3)
    - Goal achievement documentation
    - **Effort:** Medium | **Impact:** High

11. **Mid-Quarter Review Tracking**
    - Mid-quarter review form
    - Goal adjustment workflow
    - **Effort:** Low | **Impact:** Medium

### Phase 3: User Management & Configuration (Week 6)

**Priority 1 - Should Have:**

12. **User Management UI**
    - User CRUD operations
    - Bulk user import (CSV)
    - Supervisor assignment
    - CONRAISS grade management
    - **Effort:** High | **Impact:** High

13. **Settings/Configuration UI**
    - PMS cycle management
    - System configuration (weights, thresholds)
    - Notification templates
    - Vacancy status toggle
    - **Effort:** Medium | **Impact:** High

14. **Role Management**
    - Add "Second-Level Reviewer" role
    - Add "Grader" role
    - Role assignment UI
    - **Effort:** Low | **Impact:** Medium

### Phase 4: Reporting & Analytics (Weeks 7-8)

**Priority 2 - Nice to Have:**

15. **Essential Reports (Top 10)**
    - Personal Performance Report (Staff)
    - Team Performance Overview (Supervisors)
    - Calibration Support Reports (Directors)
    - Organizational Performance Dashboard (HR)
    - RRR Recommendation Status
    - Exam Score and PMS Score Integration Report
    - Appeal Tracking Report
    - Evaluation Completion Rate
    - Rating Distribution Analysis
    - Audit Log Reports
    - **Effort:** Very High | **Impact:** Medium

16. **Export Functionality**
    - PDF export for reports
    - Excel export for data analysis
    - **Effort:** Medium | **Impact:** Medium

17. **Dashboard Visualizations**
    - Charts and graphs (using recharts)
    - Performance trends
    - Rating distributions
    - **Effort:** Medium | **Impact:** Medium

### Phase 5: EMM Enhancements (Week 9)

**Priority 2 - Nice to Have:**

18. **Manual Grading Interface**
    - Grader assignment workflow
    - Essay grading UI with rubrics
    - Partial credit support
    - **Effort:** High | **Impact:** Medium

19. **Exam Randomization**
    - Question order randomization
    - Option order randomization
    - **Effort:** Low | **Impact:** Low

20. **Exam Proctoring Features**
    - Browser lockdown detection
    - Tab switching alerts
    - Suspicious activity flagging
    - **Effort:** Medium | **Impact:** Low

### Phase 6: Polish & Testing (Weeks 10-11)

**Priority 3 - Must Have Before Launch:**

21. **Comprehensive Testing**
    - Unit tests (80% coverage)
    - Integration tests
    - E2E tests for critical workflows
    - Load testing (300 concurrent users)
    - **Effort:** Very High | **Impact:** Critical

22. **Security Hardening**
    - Password strength enforcement (already coded, needs activation)
    - Rate limiting tuning
    - Security audit
    - **Effort:** Medium | **Impact:** High

23. **Documentation**
    - API documentation (Swagger/OpenAPI)
    - User manuals (Staff, Supervisor, HR Admin)
    - Admin guide
    - Deployment guide
    - **Effort:** High | **Impact:** High

24. **Performance Optimization**
    - Database query optimization
    - Redis caching implementation
    - Frontend code splitting
    - **Effort:** Medium | **Impact:** Medium

---

## 9. Key Business Rules Summary

### 9.1 RRR Scoring

```
Combined Score = (Exam Score × 0.70) + (PMS Score × 0.20) + (Seniority Score × 0.10)
```

### 9.2 Promotion Eligibility

| CONRAISS Grade | Standard Cycle | After Failed Attempt |
|----------------|----------------|----------------------|
| 2-5 | Every 2 years | Every year |
| 6-12 | Every 3 years | Every year |
| 13-14 | Every 4 years | Every year |

### 9.3 RRR Frequency

- **Promotion:** Once every 3 years (after successful promotion)
- **Recognition/Reward:** Once every year

### 9.4 Exam Retakes

- Can retake next year if failed
- Unlimited attempts (as long as vacancy exists)

### 9.5 Appeals

- Must be submitted within 14 days of evaluation finalization
- Reviewed by HR Admin or Director
- Decision is final

### 9.6 Data Retention

- Performance data: 10 years
- Audit logs: 10 years
- User data: Active + 10 years after termination

---

## 10. Critical Implementation Notes

### 10.1 Seniority Score Calculation

**Suggested Algorithm:**
```python
def calculate_seniority_score(user):
    """
    Calculate seniority score (0-100) based on time in current grade.
    """
    if not user.date_of_last_promotion:
        # Use date of hire if never promoted
        time_in_grade = (datetime.now().date() - user.date_of_hire).days / 365.25
    else:
        time_in_grade = (datetime.now().date() - user.date_of_last_promotion).days / 365.25
    
    # Determine expected years in grade based on CONRAISS level
    if user.conraiss_grade in [2, 3, 4, 5]:
        expected_years = 2
    elif user.conraiss_grade in range(6, 13):
        expected_years = 3
    elif user.conraiss_grade in [13, 14]:
        expected_years = 4
    else:
        expected_years = 3  # Default
    
    # Calculate score (capped at 100)
    seniority_score = min(100, (time_in_grade / expected_years) * 100)
    
    return round(seniority_score, 2)
```

**Note:** This algorithm needs validation with HR to ensure it aligns with organizational policy.

### 10.2 Vacancy Management

**System Configuration:**
- Add `promotion_vacancy_available` boolean flag in SystemConfiguration
- HR Admin can toggle this flag
- When vacancy = False, no staff can be marked as eligible for promotion
- Display vacancy status on promotion eligibility dashboard

### 10.3 Calibration Outlier Detection

**Statistical Approach:**
```python
def detect_outliers(evaluations):
    """
    Detect statistical outliers in evaluation ratings.
    """
    scores = [e.calculate_final_score() for e in evaluations]
    mean = np.mean(scores)
    std = np.std(scores)
    
    outliers = []
    for evaluation in evaluations:
        score = evaluation.calculate_final_score()
        z_score = (score - mean) / std
        
        # Flag if more than 2 standard deviations from mean
        if abs(z_score) > 2:
            outliers.append({
                'evaluation': evaluation,
                'score': score,
                'z_score': z_score,
                'reason': 'High' if z_score > 0 else 'Low'
            })
    
    return outliers
```

### 10.4 PMS Score Calculation (Weighted Average)

**Correct Formula:**
```python
def calculate_pms_score(evaluation):
    """
    Calculate PMS score as weighted average of goal ratings.
    """
    goals = evaluation.goals.filter_by(agreed=True).all()
    
    if not goals:
        return 0
    
    total_weighted_score = sum(goal.rating * goal.weight for goal in goals if goal.rating)
    total_weight = sum(goal.weight for goal in goals if goal.rating)
    
    if total_weight == 0:
        return 0
    
    # Average score (out of 5)
    average_score = total_weighted_score / total_weight
    
    # Convert to percentage (out of 100)
    pms_score = (average_score / 5) * 100
    
    return round(pms_score, 2)
```

---

## 11. Next Steps

### Immediate Actions (Before Implementation)

1. **Review and Approve:**
   - Confirm seniority score calculation algorithm
   - Confirm default RRR thresholds
   - Confirm appeal timeline (14 days)

2. **Prepare Data:**
   - Prepare sample user data for bulk import testing
   - Prepare organizational structure (departments, positions)
   - Prepare standard evaluation criteria templates

3. **Environment Setup:**
   - Set up AWS account and S3 bucket
   - Configure SMTP for email notifications
   - Set up staging environment

4. **Kick-off Development:**
   - Begin Phase 1 implementation
   - Set up project management board (track progress)
   - Schedule weekly check-ins

---

## 12. Open Items (For Final Confirmation)

1. **Seniority Score Algorithm:** Confirm the proposed calculation method is acceptable
2. **Default RRR Thresholds:** Confirm suggested defaults (Promotion ≥80%, Recognition 70-79%, Reward 60-69%)
3. **Appeal Deadline:** Confirm 14 days is appropriate
4. **Mid-Quarter Review:** Confirm it should be optional but tracked
5. **Bulk User Import Format:** Confirm required CSV columns for user import

---

## Document Control

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Oct 23, 2025 | Initial comprehensive analysis | Manus AI |
| 2.0 | Oct 23, 2025 | Updated with client answers, corrected RRR formula | Manus AI |

---

**Document End**

This document now serves as the **single source of truth** for all project requirements and specifications. All implementation should reference this document.


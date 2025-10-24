# Testing Checklist - Phase 1 Features
## NBTI Promotion Automation System

Use this checklist to systematically test all implemented features locally before pushing to GitHub.

---

## 🔐 Authentication & Authorization

### Login/Logout
- [ ] Login with admin credentials (admin / Admin@123)
- [ ] Receive access_token and refresh_token
- [ ] Access protected endpoint with token
- [ ] Logout successfully
- [ ] Token invalidated after logout

**Test Commands:**
```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Admin@123"}'

# Save the access_token from response
export TOKEN="your_access_token_here"

# Test protected endpoint
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Logout
curl -X POST http://localhost:5000/api/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

### Password Management
- [ ] Change password successfully
- [ ] Old password required
- [ ] New password validation works
- [ ] Login with new password

**Test Commands:**
```bash
curl -X POST http://localhost:5000/api/auth/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "Admin@123",
    "new_password": "NewAdmin@456"
  }'
```

---

## 👥 User Management

### Bulk Import
- [ ] Download CSV template
- [ ] Fill template with test data (5-10 users)
- [ ] Import users successfully
- [ ] Check import statistics
- [ ] Verify users in database
- [ ] Check supervisor linking
- [ ] Verify auto-generated passwords

**Test Commands:**
```bash
# Download template
curl -X GET http://localhost:5000/api/import-export/users/template \
  -H "Authorization: Bearer $TOKEN" \
  -o user_template.csv

# Create test data
cat > test_users.csv << 'EOF'
employee_id,first_name,last_name,email,department,position,rank,cadre,ippis_number,date_of_birth,state_of_origin,local_government_area,file_no,confirmation_date,qualifications,conraiss_grade,date_of_hire,phone_number,office_location,supervisor_employee_id
EMP001,John,Doe,john.doe@nbti.test,IT,Developer,Senior,Technical,IP001,1990-01-15,Lagos,Ikeja,F001,2020-06-01,B.Sc Computer Science,7,2018-01-10,08012345678,Lagos,
EMP002,Jane,Smith,jane.smith@nbti.test,HR,Manager,Principal,Admin,IP002,1985-05-20,Abuja,Gwagwalada,F002,2019-03-15,M.Sc HR,9,2017-02-01,08087654321,Abuja,
EMP003,Mike,Johnson,mike.j@nbti.test,Finance,Accountant,Senior,Finance,IP003,1988-03-10,Kano,Municipal,F003,2020-01-20,B.Sc Accounting,8,2018-06-15,08011122233,Kano,EMP002
EMP004,Sarah,Williams,sarah.w@nbti.test,IT,Analyst,Junior,Technical,IP004,1995-07-25,Lagos,Ikeja,F004,2021-09-01,B.Sc IT,6,2019-03-01,08099887766,Lagos,EMP001
EMP005,David,Brown,david.b@nbti.test,Admin,Officer,Principal,Admin,IP005,1982-11-30,Abuja,Gwagwalada,F005,2018-05-15,M.Sc Public Admin,10,2015-01-10,08077665544,Abuja,
EOF

# Import
curl -X POST http://localhost:5000/api/import-export/users/import \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_users.csv"
```

### User Export
- [ ] Export all users to CSV
- [ ] Verify all fields present
- [ ] Check data accuracy

**Test Commands:**
```bash
curl -X GET http://localhost:5000/api/import-export/users/export \
  -H "Authorization: Bearer $TOKEN" \
  -o exported_users.csv

# View exported data
cat exported_users.csv
```

### User CRUD
- [ ] Get user list
- [ ] Get specific user details
- [ ] Update user information
- [ ] Deactivate user

**Test Commands:**
```bash
# List users
curl -X GET http://localhost:5000/api/users \
  -H "Authorization: Bearer $TOKEN"

# Get specific user
curl -X GET http://localhost:5000/api/users/2 \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📊 RRR System

### RRR Calculation
- [ ] Calculate exam score (70%)
- [ ] Calculate PMS score (20%)
- [ ] Calculate seniority score (10%)
- [ ] Verify combined score formula
- [ ] Test with multiple users

**Test Script:**
```bash
cd ~/Documents/nbti-promotion-automation/backend/nbti_api
source venv/bin/activate

python3 << 'EOF'
from src.main import app
from src.services.rrr_service import calculate_combined_score

with app.app_context():
    # Test case 1: 85% exam, 75% PMS, 90% seniority
    score1 = calculate_combined_score(85.0, 75.0, 90.0)
    print(f'Test 1: {score1} (expected: 83.5)')
    
    # Test case 2: 100% exam, 100% PMS, 100% seniority
    score2 = calculate_combined_score(100.0, 100.0, 100.0)
    print(f'Test 2: {score2} (expected: 100.0)')
    
    # Test case 3: 70% exam, 60% PMS, 80% seniority
    score3 = calculate_combined_score(70.0, 60.0, 80.0)
    print(f'Test 3: {score3} (expected: 69.0)')
    
    assert score1 == 83.5, "Test 1 failed"
    assert score2 == 100.0, "Test 2 failed"
    assert score3 == 69.0, "Test 3 failed"
    print('\n✅ All RRR calculation tests PASSED')
EOF
```

### Seniority Ranking
- [ ] Rank by step (highest priority)
- [ ] Rank by confirmation date (2nd priority)
- [ ] Rank by age (3rd priority)
- [ ] Rank by file number (4th priority)
- [ ] Verify tie-breaking logic

**Test Script:**
```bash
python3 << 'EOF'
from src.main import app, db
from src.models import User
from src.services.rrr_service import calculate_seniority_score
from datetime import date

with app.app_context():
    # Get test users
    users = User.query.filter(User.employee_id.like('EMP%')).all()
    
    if len(users) >= 3:
        # Set different steps for testing
        users[0].conraiss_step = 5
        users[1].conraiss_step = 7
        users[2].conraiss_step = 5
        
        # Set confirmation dates
        users[0].confirmation_date = date(2020, 1, 1)
        users[2].confirmation_date = date(2019, 1, 1)
        
        db.session.commit()
        
        # Rank users
        ranked = calculate_seniority_score(users)
        
        print('Seniority Ranking:')
        for i, user in enumerate(ranked, 1):
            print(f'{i}. {user.first_name} {user.last_name} - Step: {user.conraiss_step}, Confirmed: {user.confirmation_date}')
        
        print('\n✅ Seniority ranking test completed')
    else:
        print('⚠️  Need at least 3 users for ranking test')
EOF
```

### Vacancy Configuration
- [ ] Create vacancy for promotion cycle
- [ ] Set vacancies per CONRAISS grade
- [ ] Get vacancy configuration
- [ ] Update vacancy numbers

**Test Commands:**
```bash
# Create vacancy configuration
curl -X POST http://localhost:5000/api/rrr/vacancies \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "promotion_cycle": "2025-Q1",
    "vacancies": [
      {"grade": 7, "promotion_slots": 2, "recognition_slots": 3, "reward_slots": 5},
      {"grade": 8, "promotion_slots": 1, "recognition_slots": 2, "reward_slots": 3},
      {"grade": 9, "promotion_slots": 1, "recognition_slots": 2, "reward_slots": 2}
    ]
  }'

# Get vacancies
curl -X GET http://localhost:5000/api/rrr/vacancies/2025-Q1 \
  -H "Authorization: Bearer $TOKEN"
```

### RRR Allocation
- [ ] Allocate RRR for promotion cycle
- [ ] Verify rank-based allocation
- [ ] Check top N get promoted
- [ ] Verify multiple RRR types allowed
- [ ] Get recommendations

**Test Commands:**
```bash
# Trigger allocation
curl -X POST http://localhost:5000/api/rrr/allocate/2025-Q1 \
  -H "Authorization: Bearer $TOKEN"

# Get recommendations
curl -X GET http://localhost:5000/api/rrr/recommendations/2025-Q1 \
  -H "Authorization: Bearer $TOKEN"

# Get rankings for specific grade
curl -X GET http://localhost:5000/api/rrr/rankings/7/2025-Q1 \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🎓 Promotion System

### Eligibility Checking
- [ ] Check eligibility for user
- [ ] Verify CONRAISS-based rules (2/3/4 years)
- [ ] Check failed attempt handling
- [ ] Get all eligible candidates

**Test Commands:**
```bash
# Check eligibility for specific user
curl -X GET http://localhost:5000/api/promotion/eligibility/2 \
  -H "Authorization: Bearer $TOKEN"

# Get all eligible candidates
curl -X GET http://localhost:5000/api/promotion/eligible-candidates \
  -H "Authorization: Bearer $TOKEN"
```

### Step Allocation
- [ ] Get step recommendation for promotion
- [ ] Verify salary increment guaranteed
- [ ] Check CONRAISS step limits (15/11/9)
- [ ] Apply promotion with step allocation

**Test Script:**
```bash
python3 << 'EOF'
from src.main import app, db
from src.models import User
from src.services.step_allocation_service import get_minimum_step_for_promotion

with app.app_context():
    # Get a test user
    user = User.query.filter_by(employee_id='EMP001').first()
    
    if user:
        # Set current grade and step
        user.conraiss_grade = 7
        user.conraiss_step = 10
        db.session.commit()
        
        # Get recommended step for promotion to grade 8
        target_grade = 8
        min_step, current_salary, new_salary = get_minimum_step_for_promotion(user, target_grade)
        
        print(f'User: {user.first_name} {user.last_name}')
        print(f'Current: Grade {user.conraiss_grade}, Step {user.conraiss_step}')
        print(f'Current Salary: ₦{current_salary:,.2f}')
        print(f'Promotion to Grade {target_grade}:')
        print(f'  Minimum Step: {min_step}')
        print(f'  New Salary: ₦{new_salary:,.2f}')
        print(f'  Increment: ₦{new_salary - current_salary:,.2f}')
        
        assert new_salary > current_salary, "Salary must increase"
        print('\n✅ Step allocation test PASSED')
    else:
        print('⚠️  Test user not found')
EOF
```

### Step Increment
- [ ] Increment user step manually
- [ ] Verify step doesn't exceed maximum
- [ ] Check step increment log created
- [ ] Get step increment history

**Test Commands:**
```bash
# Increment step for user
curl -X POST http://localhost:5000/api/promotion/increment-step/2 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Manual test increment"}'

# Get step history
curl -X GET http://localhost:5000/api/promotion/step-history/2 \
  -H "Authorization: Bearer $TOKEN"
```

---

## ⚙️ Background Tasks (Celery)

### Annual Step Increment
- [ ] Trigger manual step increment
- [ ] Verify all eligible users incremented
- [ ] Check step increment logs created
- [ ] Verify notifications sent
- [ ] Check task status

**Test Commands:**
```bash
# Trigger step increment
curl -X POST http://localhost:5000/api/tasks/trigger-step-increment \
  -H "Authorization: Bearer $TOKEN"

# Response will include task_id, check status:
curl -X GET http://localhost:5000/api/tasks/task-status/TASK_ID \
  -H "Authorization: Bearer $TOKEN"
```

### Task Monitoring
- [ ] Check Celery worker is running
- [ ] Verify tasks appear in worker logs
- [ ] Check task completion
- [ ] Verify task results

**Monitor Commands:**
```bash
# In Celery worker terminal, you should see:
# [2025-10-24 12:00:00,000: INFO/MainProcess] Received task: src.tasks.process_annual_step_increment

# Check active tasks
celery -A src.celery_app.celery_app inspect active

# Check scheduled tasks
celery -A src.celery_app.celery_app inspect scheduled
```

---

## 📝 Audit Logging

### Audit Log Creation
- [ ] Perform action (login, update user, etc.)
- [ ] Verify audit log created
- [ ] Check log contains user_id
- [ ] Check log contains IP address
- [ ] Check log contains old/new values

**Test Commands:**
```bash
# Get recent audit logs
curl -X GET "http://localhost:5000/api/audit/logs?limit=20" \
  -H "Authorization: Bearer $TOKEN"

# Get logs for specific user
curl -X GET "http://localhost:5000/api/audit/logs?user_id=1&limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Get logs for specific action
curl -X GET "http://localhost:5000/api/audit/logs?action_type=LOGIN&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

### Entity History
- [ ] Get complete history for entity
- [ ] Verify chronological order
- [ ] Check all changes recorded

**Test Commands:**
```bash
# Get user history
curl -X GET http://localhost:5000/api/audit/entity-history/User/2 \
  -H "Authorization: Bearer $TOKEN"
```

### User Activity
- [ ] Get user activity for last 30 days
- [ ] Verify all actions listed
- [ ] Check date filtering works

**Test Commands:**
```bash
# Get activity for user
curl -X GET "http://localhost:5000/api/audit/user-activity/1?days=30" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📁 File Management

### File Upload (Local Testing)
- [ ] Upload test file
- [ ] Verify file stored (or S3 key returned)
- [ ] Get download URL
- [ ] Download file

**Test Commands:**
```bash
# Create test file
echo "This is test evidence" > test_evidence.txt

# Upload PMS evidence
curl -X POST http://localhost:5000/api/audit/upload/pms-evidence/1 \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_evidence.txt"

# Note: This will fail without S3 configured, but should return proper error
```

---

## 🗄️ Database Integrity

### Data Verification
- [ ] Check all 21 tables exist
- [ ] Verify 180 salary records
- [ ] Check user count matches imports
- [ ] Verify foreign key relationships
- [ ] Check no orphaned records

**Test Script:**
```bash
python3 << 'EOF'
from src.main import app, db
from src.models import (
    User, Role, SalaryScale, StepIncrementLog,
    PMSEvaluation, PMSGoal, PMSCycle,
    EMMQuestion, EMMExam, EMMExamSubmission,
    RRRVacancy, RRRRecommendation,
    Appeal, DevelopmentNeed,
    SystemConfiguration, AuditLog, Notification
)

with app.app_context():
    print('Database Integrity Check:')
    print(f'  Tables: {len(db.metadata.tables)}')
    print(f'  Users: {User.query.count()}')
    print(f'  Roles: {Role.query.count()}')
    print(f'  Salary Scale: {SalaryScale.query.count()}')
    print(f'  Audit Logs: {AuditLog.query.count()}')
    
    # Check for orphaned records
    users_with_invalid_supervisor = User.query.filter(
        User.supervisor_id.isnot(None),
        ~User.supervisor_id.in_(db.session.query(User.id))
    ).count()
    
    print(f'  Orphaned supervisor links: {users_with_invalid_supervisor}')
    
    # Verify salary scale completeness
    grades = db.session.query(SalaryScale.grade).distinct().all()
    print(f'  Salary grades covered: {len(grades)} (expected: 14)')
    
    print('\n✅ Database integrity check complete')
EOF
```

---

## 🔍 API Endpoint Coverage

### Test All Endpoints
- [ ] Authentication endpoints (6)
- [ ] User endpoints (5)
- [ ] RRR endpoints (8)
- [ ] Promotion endpoints (7)
- [ ] Tasks endpoints (5)
- [ ] Audit endpoints (9)
- [ ] Import/Export endpoints (3)

**Quick Test Script:**
```bash
python3 << 'EOF'
from src.main import app

with app.app_context():
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            methods = ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            routes.append(f'{rule.rule} [{methods}]')
    
    print(f'Total API Routes: {len(routes)}')
    
    # Group by prefix
    prefixes = {}
    for route in routes:
        prefix = route.split('/')[2] if len(route.split('/')) > 2 else 'root'
        prefixes[prefix] = prefixes.get(prefix, 0) + 1
    
    print('\nRoutes by module:')
    for prefix, count in sorted(prefixes.items()):
        print(f'  {prefix}: {count} routes')
EOF
```

---

## ✅ Final Verification

Before pushing to GitHub, ensure:

- [ ] All services start without errors
- [ ] All authentication tests pass
- [ ] User import/export works
- [ ] RRR calculation is correct (70/20/10)
- [ ] Seniority ranking works (step → date → age → file)
- [ ] Step allocation guarantees salary increment
- [ ] Eligibility checking follows CONRAISS rules
- [ ] Celery tasks execute successfully
- [ ] Audit logs are created for all actions
- [ ] Database has no integrity issues
- [ ] All 74 API endpoints are accessible
- [ ] No Python errors in logs
- [ ] No database errors in logs

---

## 📊 Test Results Template

Use this template to document your test results:

```
NBTI Promotion Automation - Test Results
Date: _______________
Tester: _______________

Authentication: ✅ / ❌
User Management: ✅ / ❌
RRR Calculation: ✅ / ❌
Seniority Ranking: ✅ / ❌
Vacancy Management: ✅ / ❌
RRR Allocation: ✅ / ❌
Eligibility Checking: ✅ / ❌
Step Allocation: ✅ / ❌
Step Increment: ✅ / ❌
Celery Tasks: ✅ / ❌
Audit Logging: ✅ / ❌
File Upload: ✅ / ❌ (N/A without S3)
Database Integrity: ✅ / ❌
API Coverage: ✅ / ❌

Issues Found:
1. _______________
2. _______________

Overall Status: PASS / FAIL
```

---

**Ready for GitHub:** ☐ Yes ☐ No

**Notes:**
_______________________________________________
_______________________________________________
_______________________________________________



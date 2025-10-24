# NBTI Promotion Automation: Implementation Checklist

**Status:** Ready for Implementation  
**Last Updated:** October 24, 2025

---

## Pre-Implementation Checklist

### ✅ Requirements Gathering - COMPLETE
- [x] Reviewed existing codebase
- [x] Studied PMS PRD
- [x] Studied EMM PRD
- [x] Answered all 22 clarification questions
- [x] Clarified seniority calculation method
- [x] Clarified RRR allocation (rank-based, not threshold-based)
- [x] Obtained CONRAISS salary scale data
- [x] Defined CSV import specification
- [x] Confirmed all business rules

### ✅ Documentation - COMPLETE
- [x] Initial project analysis
- [x] Gap analysis
- [x] Final complete specifications document
- [x] Database schema design
- [x] Implementation roadmap
- [x] Salary scale SQL seed file

---

## Phase 1: Critical Foundation (Weeks 1-3)

### 1.1 Database Schema Implementation

**Backend Tasks:**

- [ ] Create database migration for new models:
  - [ ] `SalaryScale` model
  - [ ] `StepIncrementLog` model
  - [ ] `RRRVacancy` model
  - [ ] `RRRRecommendation` model
  - [ ] `PMSCycle` model
  - [ ] `Appeal` model
  - [ ] `AuditLog` model (enhanced)
  - [ ] `SystemConfiguration` model
  - [ ] `Notification` model
  - [ ] `DevelopmentNeed` model

- [ ] Update existing models:
  - [ ] `User` model - Add seniority fields (employee_id, ippis_number, file_no, rank, cadre, conraiss_step, date_of_birth, state_of_origin, lga, confirmation_date, qualifications, etc.)
  - [ ] `PMSEvaluation` model - Add cycle_id, second_level_reviewer_id, calibration fields, mid-quarter review fields
  - [ ] `PMSGoal` model - Add self_rating, self_comments, evidence, kra_category
  - [ ] `EMMExam` model - Add randomization fields, proctoring fields, is_promotional_exam, target_conraiss_grade
  - [ ] `EMMExamSubmission` model - Add time_remaining, ip_address, browser_info, attempt_number, flagged fields

- [ ] Run database migrations
- [ ] Seed salary scale data from `seed_salary_scale.sql`
- [ ] Create seed data for:
  - [ ] Default roles (including "Second-Level Reviewer", "Grader")
  - [ ] Standard evaluation criteria (13 items for staff, 18 KPIs for centre managers)
  - [ ] Sample system configuration

**Testing:**
- [ ] Verify all tables created successfully
- [ ] Verify salary scale data imported correctly (all grades 2-15, all steps)
- [ ] Test model relationships
- [ ] Test calculated properties (User.years_since_first_appointment, User.current_salary, etc.)

**Estimated Time:** 3-4 days

---

### 1.2 Corrected RRR Calculation

**Backend Tasks:**

- [ ] Create `services/rrr_service.py`:
  - [ ] `calculate_combined_score(exam_score, pms_score, seniority_score)` - 70/20/10 formula
  - [ ] `calculate_pms_score(evaluation)` - Weighted average of goals
  - [ ] `calculate_seniority_score(user, candidates_in_same_grade)` - Priority-based ranking
  - [ ] `get_exam_score(user, exam_submission)` - Extract exam score
  - [ ] Unit tests for all calculation functions

- [ ] Update `PMSEvaluation` model:
  - [ ] Add `calculate_final_score()` method (weighted average of goals)
  - [ ] Add `get_pms_percentage()` method (convert to 0-100 scale)

- [ ] Update `User` model:
  - [ ] Add `calculate_seniority_score(candidates)` method
  - [ ] Add `get_combined_promotion_score(exam_score, pms_score)` method

**Testing:**
- [ ] Test combined score calculation with sample data
- [ ] Test seniority ranking with multiple candidates
- [ ] Test tie-breaking logic (step → confirmation date → age → file number)
- [ ] Verify scores are correctly weighted (70/20/10)

**Estimated Time:** 2-3 days

---

### 1.3 Rank-Based RRR Allocation

**Backend Tasks:**

- [ ] Create `services/rrr_allocation_service.py`:
  - [ ] `get_eligible_candidates_for_grade(grade, promotion_cycle)` - Query eligible staff
  - [ ] `rank_candidates(candidates)` - Sort by combined score + tie-breaking
  - [ ] `allocate_rrr_for_grade(grade, promotion_vacancies, recognition_slots, reward_slots)` - Main allocation logic
  - [ ] `allocate_rrr_for_all_grades(promotion_cycle)` - Process all grades
  - [ ] `generate_rrr_recommendations(allocations)` - Create RRRRecommendation records

- [ ] Create API endpoints in `routes/rrr.py`:
  - [ ] `POST /api/rrr/vacancies` - Create/update vacancy configuration
  - [ ] `GET /api/rrr/vacancies/<cycle>` - Get vacancies for a cycle
  - [ ] `POST /api/rrr/allocate/<cycle>` - Trigger RRR allocation
  - [ ] `GET /api/rrr/recommendations/<cycle>` - Get recommendations
  - [ ] `GET /api/rrr/rankings/<grade>/<cycle>` - Get ranking for a grade
  - [ ] `PUT /api/rrr/recommendations/<id>/approve` - Approve recommendation
  - [ ] `PUT /api/rrr/recommendations/<id>/reject` - Reject recommendation

**Frontend Tasks:**

- [ ] Create `pages/RRR/VacancyConfiguration.jsx`:
  - [ ] Form to set vacancies per grade
  - [ ] Table showing current vacancy configuration
  - [ ] Validation (vacancies must be positive integers)

- [ ] Create `pages/RRR/RankingView.jsx`:
  - [ ] Display ranked candidates per grade
  - [ ] Show combined scores and component scores
  - [ ] Highlight top N candidates (promotion, recognition, reward)
  - [ ] Export to PDF/Excel

- [ ] Create `pages/RRR/RecommendationApproval.jsx`:
  - [ ] List of pending recommendations
  - [ ] Approve/reject actions
  - [ ] Bulk approval

**Testing:**
- [ ] Test ranking with sample candidates
- [ ] Test allocation with different vacancy configurations
- [ ] Test multiple RRR types per candidate
- [ ] Test edge cases (no vacancies, tie scores, etc.)

**Estimated Time:** 4-5 days

---

### 1.4 Promotion Step Allocation

**Backend Tasks:**

- [ ] Create `services/step_allocation_service.py`:
  - [ ] `calculate_promotion_step(current_grade, current_step, new_grade)` - Find minimum step with salary increment
  - [ ] `get_salary_for_grade_step(grade, step)` - Query salary scale
  - [ ] `apply_promotion(user, new_grade, new_step, effective_date)` - Update user record
  - [ ] `log_promotion(user, old_grade, old_step, new_grade, new_step)` - Audit trail

- [ ] Create API endpoints in `routes/promotion.py`:
  - [ ] `POST /api/promotion/calculate-step` - Calculate recommended step
  - [ ] `POST /api/promotion/apply` - Apply promotion to user
  - [ ] `GET /api/promotion/history/<user_id>` - Get promotion history

**Frontend Tasks:**

- [ ] Create `components/PromotionStepCalculator.jsx`:
  - [ ] Display current position (grade, step, salary)
  - [ ] Display target grade
  - [ ] Show recommended step and new salary
  - [ ] Show salary increment amount
  - [ ] Manual override option for HR

**Testing:**
- [ ] Test step calculation with various scenarios
- [ ] Test edge case: Current salary higher than all steps in new grade
- [ ] Test manual override
- [ ] Verify audit logging

**Estimated Time:** 2 days

---

### 1.5 Promotion Eligibility Logic

**Backend Tasks:**

- [ ] Create `services/eligibility_service.py`:
  - [ ] `is_eligible_for_promotion(user, target_grade)` - Main eligibility check
  - [ ] `get_standard_eligibility_cycle(conraiss_grade)` - Return 2, 3, or 4 years
  - [ ] `has_active_disciplinary_action(user)` - Check disciplinary status
  - [ ] `get_eligible_candidates(target_grade, promotion_cycle)` - Query eligible staff
  - [ ] `update_eligibility_status_for_all_staff()` - Batch update eligibility

- [ ] Create API endpoints in `routes/eligibility.py`:
  - [ ] `GET /api/eligibility/check/<user_id>/<target_grade>` - Check eligibility
  - [ ] `GET /api/eligibility/candidates/<grade>/<cycle>` - Get eligible candidates
  - [ ] `POST /api/eligibility/refresh` - Refresh eligibility for all staff

**Frontend Tasks:**

- [ ] Create `pages/Eligibility/EligibilityDashboard.jsx`:
  - [ ] Display eligibility status per grade
  - [ ] Show eligible candidates count
  - [ ] Filter by department, grade
  - [ ] Export eligible candidates list

- [ ] Create `components/EligibilityBadge.jsx`:
  - [ ] Show eligibility status (Eligible/Not Eligible/Pending)
  - [ ] Tooltip with reason

**Testing:**
- [ ] Test eligibility for different CONRAISS grades
- [ ] Test edge case: Failed promotion (eligible every year)
- [ ] Test vacancy checking
- [ ] Test disciplinary action blocking

**Estimated Time:** 3 days

---

### 1.6 Annual Step Increment (Automated)

**Backend Tasks:**

- [ ] Install and configure Celery + Redis:
  - [ ] Add `celery` and `redis` to requirements.txt
  - [ ] Create `celery_app.py` configuration
  - [ ] Create `celeryconfig.py` with beat schedule

- [ ] Create `tasks/step_increment.py`:
  - [ ] `process_annual_step_increment()` - Main Celery task
  - [ ] `get_max_step_for_grade(grade)` - Return 15, 11, or 9
  - [ ] `increment_user_step(user)` - Increment step and log
  - [ ] `send_step_increment_notification(user)` - Email notification
  - [ ] `generate_step_increment_report(incremented, skipped)` - HR report

- [ ] Create API endpoints in `routes/step_increment.py`:
  - [ ] `POST /api/step-increment/trigger` - Manual trigger (for testing)
  - [ ] `GET /api/step-increment/logs` - View increment logs
  - [ ] `GET /api/step-increment/report/<year>` - Get annual report

**Frontend Tasks:**

- [ ] Create `pages/StepIncrement/IncrementLogs.jsx`:
  - [ ] Table of all step increments
  - [ ] Filter by year, department, user
  - [ ] Export to Excel

- [ ] Create `pages/StepIncrement/ManualTrigger.jsx`:
  - [ ] Button to trigger increment (for testing)
  - [ ] Confirmation dialog
  - [ ] Progress indicator

**Testing:**
- [ ] Test increment logic with sample users
- [ ] Test max step boundary (should not exceed)
- [ ] Test Celery task execution
- [ ] Test email notifications
- [ ] Test scheduled execution (set to run in 1 minute for testing)

**Estimated Time:** 3-4 days

---

### 1.7 Forensic Audit Logging

**Backend Tasks:**

- [ ] Create `services/audit_service.py`:
  - [ ] `log_action(user, action_type, entity_type, entity_id, old_value, new_value, is_sensitive)` - Main logging function
  - [ ] `get_audit_logs(filters)` - Query logs with filters
  - [ ] `export_audit_logs(filters, format)` - Export to CSV/Excel
  - [ ] Decorator `@audit_log` for automatic logging

- [ ] Integrate audit logging into all critical endpoints:
  - [ ] User CRUD operations
  - [ ] Evaluation CRUD operations
  - [ ] Goal rating changes
  - [ ] RRR recommendations
  - [ ] Promotion applications
  - [ ] Step increments
  - [ ] Appeal submissions/resolutions
  - [ ] System configuration changes

- [ ] Create API endpoints in `routes/audit.py`:
  - [ ] `GET /api/audit/logs` - Get audit logs (paginated, filtered)
  - [ ] `GET /api/audit/logs/<entity_type>/<entity_id>` - Get logs for specific entity
  - [ ] `POST /api/audit/export` - Export logs

**Frontend Tasks:**

- [ ] Create `pages/Audit/AuditLogViewer.jsx`:
  - [ ] Table with filters (user, action, entity, date range)
  - [ ] Pagination
  - [ ] Highlight sensitive actions (RRR decisions)
  - [ ] Export button
  - [ ] Drill-down to see before/after values

**Testing:**
- [ ] Verify all critical actions are logged
- [ ] Test log querying with various filters
- [ ] Test export functionality
- [ ] Verify UUID generation
- [ ] Test log retention (should persist for 10 years)

**Estimated Time:** 3-4 days

---

### 1.8 AWS S3 Integration

**Backend Tasks:**

- [ ] Install boto3: `pip install boto3`
- [ ] Create `services/s3_service.py`:
  - [ ] `upload_file(file, bucket, key)` - Upload file to S3
  - [ ] `generate_signed_url(bucket, key, expiration)` - Generate temporary access URL
  - [ ] `delete_file(bucket, key)` - Delete file
  - [ ] `list_files(bucket, prefix)` - List files in folder

- [ ] Configure S3 credentials in `.env`:
  - [ ] `AWS_ACCESS_KEY_ID`
  - [ ] `AWS_SECRET_ACCESS_KEY`
  - [ ] `AWS_S3_BUCKET_NAME`
  - [ ] `AWS_REGION`

- [ ] Create API endpoints in `routes/files.py`:
  - [ ] `POST /api/files/upload` - Upload file
  - [ ] `GET /api/files/<file_id>` - Get signed URL
  - [ ] `DELETE /api/files/<file_id>` - Delete file

**Frontend Tasks:**

- [ ] Create `components/FileUpload.jsx`:
  - [ ] Drag-and-drop file upload
  - [ ] File type validation (PDF, DOCX, XLSX, JPG, PNG)
  - [ ] File size validation (max 10MB)
  - [ ] Progress indicator
  - [ ] Preview uploaded files

- [ ] Create `components/FileViewer.jsx`:
  - [ ] Display uploaded files
  - [ ] Download button
  - [ ] Delete button (with confirmation)

**Testing:**
- [ ] Test file upload to S3
- [ ] Test signed URL generation and access
- [ ] Test file deletion
- [ ] Test file type and size validation
- [ ] Test error handling (network errors, S3 errors)

**Estimated Time:** 2-3 days

---

### 1.9 Bulk User Import

**Backend Tasks:**

- [ ] Create `services/user_import_service.py`:
  - [ ] `parse_csv(file)` - Parse CSV file
  - [ ] `validate_row(row)` - Validate each row
  - [ ] `create_user_from_row(row)` - Create User object
  - [ ] `generate_username(employee_id)` - Generate username
  - [ ] `generate_temporary_password()` - Generate random password
  - [ ] `send_welcome_email(user, temp_password)` - Send credentials
  - [ ] `import_users(file)` - Main import function

- [ ] Create API endpoint in `routes/users.py`:
  - [ ] `POST /api/users/bulk-import` - Upload CSV and import

- [ ] Create CSV template file with all required columns

**Frontend Tasks:**

- [ ] Create `pages/Users/BulkImport.jsx`:
  - [ ] Download CSV template button
  - [ ] File upload component
  - [ ] Import progress indicator
  - [ ] Results display (imported count, errors)
  - [ ] Error details table

**Testing:**
- [ ] Test with valid CSV file
- [ ] Test with invalid data (missing required fields, invalid dates, etc.)
- [ ] Test with duplicate employee_id/email
- [ ] Test with non-existent supervisor_employee_id (should skip)
- [ ] Test username and password generation
- [ ] Test welcome email sending

**Estimated Time:** 3 days

---

## Phase 1 Summary

**Total Estimated Time:** 25-30 days (4-5 weeks)

**Deliverables:**
- ✅ Complete database schema with all models
- ✅ Salary scale data seeded
- ✅ Corrected RRR calculation (70/20/10)
- ✅ Priority-based seniority ranking
- ✅ Rank-based RRR allocation system
- ✅ Promotion step allocation logic
- ✅ CONRAISS-based eligibility checking
- ✅ Automated annual step increment
- ✅ Forensic-level audit logging
- ✅ AWS S3 file storage
- ✅ Bulk user import from CSV

**Testing Checklist:**
- [ ] All unit tests pass (80% coverage target)
- [ ] All integration tests pass
- [ ] Manual testing of critical workflows
- [ ] Load testing (simulate 300 concurrent users)
- [ ] Security testing (SQL injection, XSS, CSRF)

---

## Phase 2-6: Remaining Implementation

See `FINAL_COMPLETE_SPECIFICATIONS.md` Section 11 for detailed breakdown of:
- Phase 2: Core Workflows (Weeks 4-5)
- Phase 3: User Management & Configuration (Week 6)
- Phase 4: Reporting & Analytics (Weeks 7-8)
- Phase 5: EMM Enhancements (Week 9)
- Phase 6: Testing & Documentation (Weeks 10-11)

---

## Daily Progress Tracking

Use this section to track daily progress:

### Week 1
- [ ] Day 1: Database schema design and migration scripts
- [ ] Day 2: Create new models, update existing models
- [ ] Day 3: Run migrations, seed salary scale data
- [ ] Day 4: Test database schema, fix issues
- [ ] Day 5: Begin RRR calculation implementation

### Week 2
- [ ] Day 1: Complete RRR calculation, unit tests
- [ ] Day 2: Begin rank-based allocation
- [ ] Day 3: Complete allocation logic, API endpoints
- [ ] Day 4: Frontend for vacancy configuration
- [ ] Day 5: Frontend for ranking view

### Week 3
- [ ] Day 1: Promotion step allocation
- [ ] Day 2: Eligibility logic
- [ ] Day 3: Annual step increment (Celery setup)
- [ ] Day 4: Audit logging integration
- [ ] Day 5: AWS S3 integration

### Week 4
- [ ] Day 1: Bulk user import
- [ ] Day 2-5: Phase 1 testing and bug fixes

---

## Notes

- Prioritize backend implementation first, then frontend
- Write unit tests as you go (don't defer testing)
- Commit frequently with descriptive messages
- Document any deviations from specifications
- Flag any ambiguities immediately

---

**Document End**


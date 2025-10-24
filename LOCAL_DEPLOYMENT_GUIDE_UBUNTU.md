# Local Deployment Guide - Ubuntu 24.04.3
## NBTI Promotion Automation System

**Target OS:** Ubuntu 24.04.3  
**Purpose:** Local development and testing before GitHub deployment  
**Time Required:** ~30 minutes

---

## 📋 Prerequisites Check

Before starting, verify your system:

```bash
# Check Ubuntu version
lsb_release -a

# Check Python version (should be 3.11+)
python3 --version

# Check if you have sudo access
sudo -v
```

---

## 🚀 Step-by-Step Installation

### Step 1: System Updates and Dependencies

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential build tools
sudo apt install -y build-essential python3-dev python3-pip python3-venv

# Install PostgreSQL (for production-like testing)
sudo apt install -y postgresql postgresql-contrib

# Install Redis (required for Celery)
sudo apt install -y redis-server

# Install Git (if not already installed)
sudo apt install -y git

# Install Node.js and npm (for frontend)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### Step 2: Extract Project Files

```bash
# Navigate to your preferred directory
cd ~/Documents  # or wherever you want to work

# Extract the project archive
tar -xzf ~/Downloads/nbti-promotion-automation-phase1-complete.tar.gz

# Navigate into project directory
cd nbti-promotion-automation

# Verify extraction
ls -la
```

### Step 3: PostgreSQL Database Setup

```bash
# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE nbti_promotion;
CREATE USER nbti_user WITH PASSWORD 'nbti_password_2024';
GRANT ALL PRIVILEGES ON DATABASE nbti_promotion TO nbti_user;
ALTER DATABASE nbti_promotion OWNER TO nbti_user;
\q
EOF

# Verify database creation
sudo -u postgres psql -c "\l" | grep nbti_promotion
```

### Step 4: Redis Setup

```bash
# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify Redis is running
redis-cli ping
# Should output: PONG

# Check Redis status
sudo systemctl status redis-server
```

### Step 5: Backend Setup

```bash
# Navigate to backend directory
cd ~/Documents/nbti-promotion-automation/backend/nbti_api

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "Flask|celery|redis|boto3"
```

### Step 6: Environment Configuration

```bash
# Still in backend/nbti_api directory with venv activated

# Copy environment template
cp .env.example .env

# Edit .env file
nano .env
```

**Update the following in `.env`:**

```bash
# Database Configuration
DATABASE_URL=postgresql://nbti_user:nbti_password_2024@localhost:5432/nbti_promotion

# Security Keys (generate your own)
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-too

# Application Settings
FLASK_ENV=development
FLASK_DEBUG=True

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# AWS S3 Configuration (optional for local testing - can use local storage)
AWS_ACCESS_KEY_ID=test-key
AWS_SECRET_ACCESS_KEY=test-secret
AWS_S3_BUCKET=nbti-local-files
AWS_REGION=us-east-1

# Email Configuration (optional for local testing)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**Save and exit:** Press `Ctrl+X`, then `Y`, then `Enter`

### Step 7: Initialize Database

```bash
# Still in backend/nbti_api with venv activated

# Create database tables
python3 -c "
from src.main import app, db
with app.app_context():
    db.create_all()
    print('✓ Database tables created successfully')
"

# Seed salary scale data
python3 << 'EOF'
from src.main import app, db
from src.models import SalaryScale

with app.app_context():
    # Check if already seeded
    if SalaryScale.query.count() > 0:
        print('✓ Salary scale already seeded')
    else:
        # Import from seed file
        with open('../../seed_salary_scale.sql', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('--'):
                    db.session.execute(db.text(line))
        db.session.commit()
        count = SalaryScale.query.count()
        print(f'✓ Seeded {count} salary scale records')
EOF
```

### Step 8: Create Admin User

```bash
# Create initial admin user for testing
python3 << 'EOF'
from src.main import app, db
from src.models import User, Role

with app.app_context():
    # Create HR Admin role if it doesn't exist
    admin_role = Role.query.filter_by(name='HR Admin').first()
    if not admin_role:
        admin_role = Role(name='HR Admin', description='HR Administrator')
        db.session.add(admin_role)
        db.session.flush()
    
    # Create admin user if doesn't exist
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@nbti.local',
            first_name='System',
            last_name='Administrator',
            employee_id='ADMIN001',
            is_active=True
        )
        admin.set_password('Admin@123')
        admin.add_role(admin_role)
        db.session.add(admin)
        db.session.commit()
        print('✓ Admin user created')
        print('  Username: admin')
        print('  Password: Admin@123')
        print('  Email: admin@nbti.local')
    else:
        print('✓ Admin user already exists')
EOF
```

### Step 9: Test Backend

```bash
# Test that everything is working
python3 -c "
from src.main import app, db
from src.models import User, SalaryScale

with app.app_context():
    user_count = User.query.count()
    salary_count = SalaryScale.query.count()
    
    print('✓ Backend Test Results:')
    print(f'  - Database connection: OK')
    print(f'  - Users in database: {user_count}')
    print(f'  - Salary scale records: {salary_count}')
    print(f'  - Total tables: {len(db.metadata.tables)}')
    
    # Test RRR calculation
    from src.services.rrr_service import calculate_combined_score
    score = calculate_combined_score(85.0, 75.0, 90.0)
    print(f'  - RRR calculation: {score} (expected: 83.5)')
    
    if salary_count == 180 and score == 83.5:
        print('\n✅ All backend tests PASSED!')
    else:
        print('\n⚠️  Some tests failed - check configuration')
"
```

---

## 🎯 Running the Application

### Terminal 1: Start Backend API

```bash
cd ~/Documents/nbti-promotion-automation/backend/nbti_api
source venv/bin/activate
python3 src/main.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

**Test the API:**
```bash
# In a new terminal
curl http://localhost:5000/api/health
# Should return: {"status": "healthy"}
```

### Terminal 2: Start Celery Worker

```bash
cd ~/Documents/nbti-promotion-automation/backend/nbti_api
source venv/bin/activate
celery -A src.celery_app.celery_app worker --loglevel=info
```

**Expected output:**
```
[tasks]
  . src.tasks.process_annual_step_increment
  . src.tasks.send_pending_notifications
  ...
```

### Terminal 3: Start Celery Beat (Scheduler)

```bash
cd ~/Documents/nbti-promotion-automation/backend/nbti_api
source venv/bin/activate
celery -A src.celery_app.celery_app beat --loglevel=info
```

**Expected output:**
```
Scheduler: Sending due task annual-step-increment
```

### Terminal 4: Frontend (Optional)

```bash
cd ~/Documents/nbti-promotion-automation/frontend/nbti-frontend
npm install
npm run dev
```

**Expected output:**
```
Local: http://localhost:3000
```

---

## 🧪 Testing the System

### 1. Test Authentication

```bash
# Login as admin
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "Admin@123"
  }'
```

**Expected:** JSON response with `access_token` and `refresh_token`

### 2. Test User Import

```bash
# Download CSV template
curl -X GET http://localhost:5000/api/import-export/users/template \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -o user_template.csv

# Create sample CSV
cat > sample_users.csv << 'EOF'
employee_id,first_name,last_name,email,department,position,rank,cadre,ippis_number,date_of_birth,state_of_origin,local_government_area,file_no,confirmation_date,qualifications,conraiss_grade,date_of_hire,phone_number,office_location,supervisor_employee_id
EMP001,John,Doe,john.doe@nbti.local,IT,Developer,Senior,Technical,IP001,1990-01-15,Lagos,Ikeja,F001,2020-06-01,B.Sc Computer Science,7,2018-01-10,08012345678,Lagos Office,
EMP002,Jane,Smith,jane.smith@nbti.local,HR,Manager,Principal,Administrative,IP002,1985-05-20,Abuja,Gwagwalada,F002,2019-03-15,M.Sc Human Resources,9,2017-02-01,08087654321,Abuja Office,
EOF

# Import users
curl -X POST http://localhost:5000/api/import-export/users/import \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@sample_users.csv"
```

### 3. Test RRR Calculation

```bash
# Get RRR service test
python3 << 'EOF'
from src.main import app
from src.services.rrr_service import calculate_combined_score, calculate_seniority_score
from src.models import User

with app.app_context():
    # Test combined score
    score = calculate_combined_score(85.0, 75.0, 90.0)
    print(f'Combined Score: {score}')
    
    # Test seniority ranking
    users = User.query.limit(3).all()
    if users:
        ranked = calculate_seniority_score(users)
        print(f'Ranked {len(ranked)} users by seniority')
EOF
```

### 4. Test Celery Tasks

```bash
# Trigger manual step increment (for testing)
curl -X POST http://localhost:5000/api/tasks/trigger-step-increment \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Check task status
curl -X GET http://localhost:5000/api/tasks/task-status/TASK_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Test Audit Logging

```bash
# Get audit logs
curl -X GET "http://localhost:5000/api/audit/logs?limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 6. Test File Upload (without S3)

For local testing without AWS S3, you can modify the S3 service to use local storage:

```bash
# Create local file storage directory
mkdir -p ~/Documents/nbti-promotion-automation/backend/nbti_api/local_storage
```

---

## 📊 Monitoring and Debugging

### Check Service Status

```bash
# PostgreSQL
sudo systemctl status postgresql

# Redis
sudo systemctl status redis-server

# Check if ports are in use
sudo netstat -tlnp | grep -E "5000|6379|5432"
```

### View Logs

```bash
# Backend logs (if running in background)
tail -f ~/Documents/nbti-promotion-automation/backend/nbti_api/app.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-16-main.log

# Redis logs
sudo tail -f /var/log/redis/redis-server.log
```

### Database Management

```bash
# Connect to database
psql -U nbti_user -d nbti_promotion -h localhost

# Useful SQL commands
\dt                    # List all tables
\d+ user              # Describe user table
SELECT COUNT(*) FROM "user";
SELECT COUNT(*) FROM salary_scale;
\q                    # Quit
```

### Redis Management

```bash
# Connect to Redis
redis-cli

# Redis commands
KEYS *                # List all keys
GET key_name          # Get value
FLUSHALL              # Clear all data (careful!)
quit                  # Exit
```

---

## 🔧 Troubleshooting

### Problem: "ModuleNotFoundError"

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Problem: "Database connection failed"

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify database exists
sudo -u postgres psql -c "\l" | grep nbti_promotion

# Check .env DATABASE_URL is correct
cat .env | grep DATABASE_URL
```

### Problem: "Redis connection failed"

```bash
# Check Redis is running
sudo systemctl status redis-server

# Test Redis connection
redis-cli ping

# Restart Redis if needed
sudo systemctl restart redis-server
```

### Problem: "Celery worker not starting"

```bash
# Check Redis is accessible
redis-cli ping

# Verify Celery is installed
pip list | grep celery

# Check for Python errors
celery -A src.celery_app.celery_app worker --loglevel=debug
```

### Problem: "Port 5000 already in use"

```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill the process
sudo kill -9 PID

# Or use a different port in .env
echo "FLASK_RUN_PORT=5001" >> .env
```

---

## 📝 Development Workflow

### Daily Development Cycle

```bash
# 1. Start services
cd ~/Documents/nbti-promotion-automation/backend/nbti_api
source venv/bin/activate

# Terminal 1: Backend
python3 src/main.py

# Terminal 2: Celery Worker
celery -A src.celery_app.celery_app worker --loglevel=info

# Terminal 3: Celery Beat
celery -A src.celery_app.celery_app beat --loglevel=info

# 2. Make code changes

# 3. Test changes
python3 -m pytest tests/  # If you have tests

# 4. Stop services
# Ctrl+C in each terminal
```

### Before Committing to GitHub

```bash
# 1. Run all tests
cd ~/Documents/nbti-promotion-automation/backend/nbti_api
source venv/bin/activate
python3 -c "from src.main import app; print('✓ App loads successfully')"

# 2. Check for syntax errors
python3 -m py_compile src/**/*.py

# 3. Clean up
deactivate
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# 4. Initialize git (if not already)
cd ~/Documents/nbti-promotion-automation
git init
git add .
git commit -m "Initial commit - Phase 1 implementation"

# 5. Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/
dist/
build/

# Environment
.env
*.db
*.sqlite

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log

# OS
.DS_Store
Thumbs.db

# Node
node_modules/
npm-debug.log
EOF

# 6. Push to GitHub
git remote add origin YOUR_GITHUB_REPO_URL
git branch -M main
git push -u origin main
```

---

## 🎯 Quick Reference Commands

### Start Everything

```bash
# Create a startup script
cat > ~/start_nbti.sh << 'EOF'
#!/bin/bash
cd ~/Documents/nbti-promotion-automation/backend/nbti_api
source venv/bin/activate

# Start in separate terminals
gnome-terminal --tab --title="Backend" -- bash -c "python3 src/main.py; exec bash"
gnome-terminal --tab --title="Celery Worker" -- bash -c "celery -A src.celery_app.celery_app worker --loglevel=info; exec bash"
gnome-terminal --tab --title="Celery Beat" -- bash -c "celery -A src.celery_app.celery_app beat --loglevel=info; exec bash"

echo "✓ All services started in separate terminals"
EOF

chmod +x ~/start_nbti.sh
```

**Run with:** `~/start_nbti.sh`

### Stop Everything

```bash
# Kill all related processes
pkill -f "python3 src/main.py"
pkill -f "celery"
```

### Reset Database

```bash
cd ~/Documents/nbti-promotion-automation/backend/nbti_api
source venv/bin/activate

python3 << 'EOF'
from src.main import app, db
with app.app_context():
    db.drop_all()
    db.create_all()
    print('✓ Database reset complete')
EOF

# Re-seed data
python3 seed_database.py  # If you create this script
```

---

## ✅ Verification Checklist

Before considering deployment complete:

- [ ] PostgreSQL running and accessible
- [ ] Redis running and accessible
- [ ] Backend starts without errors
- [ ] Celery worker connects successfully
- [ ] Celery beat scheduler running
- [ ] Admin user can login
- [ ] User import works
- [ ] RRR calculation correct
- [ ] Audit logs being created
- [ ] All 74 API endpoints accessible

---

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review error messages in terminal
3. Check service logs
4. Verify all prerequisites are installed
5. Ensure all services are running

---

## 🎉 Success!

If all steps completed successfully, you should have:

✅ PostgreSQL database with 21 tables  
✅ Redis server running  
✅ Backend API on http://localhost:5000  
✅ Celery worker processing tasks  
✅ Celery beat scheduling tasks  
✅ Admin user ready for testing  
✅ 180 salary scale records loaded  
✅ All services ready for development

**You're ready to test all functionality locally before pushing to GitHub!**

---

**Prepared for:** Ubuntu 24.04.3  
**Last Updated:** October 24, 2025  
**Project:** NBTI Promotion Automation System


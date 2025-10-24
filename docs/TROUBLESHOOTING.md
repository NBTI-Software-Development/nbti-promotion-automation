# Troubleshooting Guide

Common issues and solutions for the NBTI Promotion Automation System.

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Database Issues](#database-issues)
3. [Authentication Issues](#authentication-issues)
4. [API Issues](#api-issues)
5. [Celery Issues](#celery-issues)
6. [Import/Export Issues](#import-export-issues)

---

## Installation Issues

### Python Version Error

**Problem**: `python3.11: command not found`

**Solution**:
```bash
# Install Python 3.11
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Verify installation
python3.11 --version
```

### Virtual Environment Issues

**Problem**: `ModuleNotFoundError` when running Python code

**Solution**:
```bash
# Always activate virtual environment first
cd ~/nbti-promotion-automation/backend/nbti_api
source venv/bin/activate

# Verify activation (prompt should show (venv))
which python3
# Should show: .../venv/bin/python3

# Reinstall dependencies if needed
pip install -r requirements.txt
```

### Permission Denied Errors

**Problem**: Permission errors during installation

**Solution**:
```bash
# Don't use sudo with pip inside virtual environment
# Instead, ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt

# For system packages, use sudo apt
sudo apt install postgresql
```

---

## Database Issues

### Cannot Connect to Database

**Problem**: `could not connect to server: Connection refused`

**Solution**:
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL if stopped
sudo systemctl start postgresql

# Enable auto-start on boot
sudo systemctl enable postgresql

# Test connection
psql -U nbti_user -d nbti_promotion -h localhost -c "SELECT 1;"
```

### Database Does Not Exist

**Problem**: `database "nbti_promotion" does not exist`

**Solution**:
```bash
# Create the database
sudo -u postgres psql -c "CREATE DATABASE nbti_promotion;"
sudo -u postgres psql -c "CREATE USER nbti_user WITH PASSWORD 'nbti_password_2024';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE nbti_promotion TO nbti_user;"

# Verify database exists
sudo -u postgres psql -c "\l" | grep nbti_promotion
```

### Wrong Password for Database User

**Problem**: `password authentication failed for user "nbti_user"`

**Solution**:
```bash
# Reset password
sudo -u postgres psql -c "ALTER USER nbti_user WITH PASSWORD 'nbti_password_2024';"

# Update .env file to match
cd ~/nbti-promotion-automation/backend/nbti_api
nano .env
# Ensure DATABASE_URL has correct password
```

### Tables Not Created

**Problem**: `relation "user" does not exist`

**Solution**:
```bash
cd ~/nbti-promotion-automation/backend/nbti_api
source venv/bin/activate

# Initialize database tables
python3 -c "from src.main import app, db; app.app_context().push(); db.create_all()"

# Verify tables were created
psql -U nbti_user -d nbti_promotion -h localhost -c "\dt"
```

### Salary Scale Data Missing

**Problem**: `No salary scale records found`

**Solution**:
```bash
cd ~/nbti-promotion-automation/backend/nbti_api

# Load salary scale data
psql -U nbti_user -d nbti_promotion -h localhost -f seed_salary_scale.sql

# Verify 180 records loaded
python3 -c "from src.main import app; from src.models import SalaryScale; app.app_context().push(); print(f'Records: {SalaryScale.query.count()}')"
```

---

## Authentication Issues

### Login Failed - Invalid Credentials

**Problem**: `{"error": "Invalid username or password"}`

**Solution**:
```bash
# Verify you're using correct credentials
# Default: username=admin, password=Admin@123

# Reset admin password if needed
cd ~/nbti-promotion-automation/backend/nbti_api
source venv/bin/activate

python3 << 'EOF'
from src.main import app, db
from src.models import User

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        admin.set_password('Admin@123')
        db.session.commit()
        print('✓ Admin password reset to: Admin@123')
    else:
        print('✗ Admin user not found')
EOF
```

### Admin User Does Not Exist

**Problem**: Admin user not found in database

**Solution**:
```bash
cd ~/nbti-promotion-automation/backend/nbti_api
source venv/bin/activate

python3 << 'EOF'
from src.main import app, db
from src.models import User, Role

with app.app_context():
    # Create HR Admin role
    admin_role = Role.query.filter_by(name='HR Admin').first()
    if not admin_role:
        admin_role = Role(name='HR Admin', description='HR Administrator')
        db.session.add(admin_role)
        db.session.flush()
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@nbti.gov.ng',
        first_name='System',
        last_name='Administrator',
        employee_id='ADMIN001',
        is_active=True
    )
    admin.set_password('Admin@123')
    admin.add_role(admin_role)
    db.session.add(admin)
    db.session.commit()
    print('✓ Admin user created: admin / Admin@123')
EOF
```

### JWT Token Errors

**Problem**: `{"msg": "Not enough segments"}` or token validation errors

**Solution**:
```bash
# This means you're using invalid or missing token

# 1. Login to get a fresh token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123"}'

# 2. Extract the access_token from response
# 3. Use it in subsequent requests:
curl -H "Authorization: Bearer YOUR_ACTUAL_TOKEN_HERE" \
  http://localhost:5000/api/auth/me
```

---

## API Issues

### Backend Not Running

**Problem**: `curl: (7) Failed to connect to localhost port 5000`

**Solution**:
```bash
# Check if backend is running
curl http://localhost:5000/api/health

# If not running, start it
cd ~/nbti-promotion-automation/backend/nbti_api
source venv/bin/activate
python3 src/main.py
```

### Port 5000 Already in Use

**Problem**: `Address already in use`

**Solution**:
```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill the process
sudo kill -9 <PID>

# Or use a different port
# Edit src/main.py and change:
# app.run(debug=True, port=5001)
```

### 404 Not Found

**Problem**: API endpoint returns 404

**Solution**:
```bash
# Verify endpoint exists
cd ~/nbti-promotion-automation/backend/nbti_api
source venv/bin/activate

python3 << 'EOF'
from src.main import app

with app.app_context():
    for rule in app.url_map.iter_rules():
        print(f'{rule.rule} - {rule.methods}')
EOF

# Check for typos in URL
# Ensure you're using correct HTTP method (GET, POST, etc.)
```

### 500 Internal Server Error

**Problem**: API returns 500 error

**Solution**:
```bash
# Check backend logs in the terminal where you ran python3 src/main.py
# Look for Python tracebacks

# Common causes:
# 1. Database connection issue
# 2. Missing required field in request
# 3. Invalid data type

# Enable debug mode for detailed errors
# In .env file:
FLASK_DEBUG=True
```

---

## Celery Issues

### Redis Connection Failed

**Problem**: `Error connecting to Redis`

**Solution**:
```bash
# Check Redis is running
sudo systemctl status redis-server

# Start Redis if stopped
sudo systemctl start redis-server

# Test connection
redis-cli ping
# Should return: PONG

# Check Redis URL in .env
cat .env | grep REDIS_URL
# Should be: redis://localhost:6379/0
```

### Celery Worker Not Starting

**Problem**: Celery worker fails to start

**Solution**:
```bash
# Ensure Redis is running first
sudo systemctl status redis-server

# Ensure virtual environment is activated
source venv/bin/activate

# Check for errors in Celery output
celery -A src.celery_app.celery_app worker --loglevel=debug

# Common issues:
# 1. Redis not running
# 2. Import errors in tasks.py
# 3. Wrong directory (must be in backend/nbti_api)
```

### Tasks Not Executing

**Problem**: Celery tasks queued but not running

**Solution**:
```bash
# Ensure both worker AND beat are running

# Terminal 1: Worker
celery -A src.celery_app.celery_app worker --loglevel=info

# Terminal 2: Beat (for scheduled tasks)
celery -A src.celery_app.celery_app beat --loglevel=info

# Check task status
python3 << 'EOF'
from src.celery_app import celery_app
i = celery_app.control.inspect()
print('Active tasks:', i.active())
print('Scheduled tasks:', i.scheduled())
EOF
```

---

## Import/Export Issues

### CSV Import Failed

**Problem**: User import returns errors

**Solution**:
```bash
# 1. Verify CSV format matches template
curl -X GET http://localhost:5000/api/import-export/users/template \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o template.csv

# 2. Check for common issues:
# - Missing required columns
# - Invalid date format (should be YYYY-MM-DD)
# - Invalid CONRAISS grade (must be 2-15)
# - Duplicate employee_id or email

# 3. Check error response for specific issues
```

### File Upload Failed

**Problem**: File upload to S3 fails

**Solution**:
```bash
# Check AWS credentials in .env
cat .env | grep AWS

# Verify credentials are correct
# Test AWS connection:
python3 << 'EOF'
import boto3
from botocore.exceptions import ClientError

try:
    s3 = boto3.client('s3')
    s3.list_buckets()
    print('✓ AWS connection successful')
except ClientError as e:
    print(f'✗ AWS error: {e}')
EOF

# If S3 is not configured, files won't upload
# This is optional for local development
```

---

## General Debugging

### Enable Debug Mode

```bash
# Edit .env file
nano ~/nbti-promotion-automation/backend/nbti_api/.env

# Set:
FLASK_DEBUG=True
FLASK_ENV=development

# Restart backend
```

### Check Logs

```bash
# Backend logs: Check terminal where you ran python3 src/main.py

# Celery logs: Check terminal where you ran celery worker

# PostgreSQL logs:
sudo tail -f /var/log/postgresql/postgresql-14-main.log

# Redis logs:
sudo tail -f /var/log/redis/redis-server.log
```

### Verify Installation

```bash
cd ~/nbti-promotion-automation/backend/nbti_api
source venv/bin/activate

python3 << 'EOF'
from src.main import app, db
from src.models import User, SalaryScale

with app.app_context():
    print('Database connection:', 'OK' if db.engine.connect() else 'FAILED')
    print('Users:', User.query.count())
    print('Salary records:', SalaryScale.query.count())
    print('Tables:', db.engine.table_names())
EOF
```

---

## Getting Help

If you can't resolve an issue:

1. **Check error messages carefully** - They usually indicate the problem
2. **Review logs** - Backend and Celery logs show detailed errors
3. **Verify prerequisites** - Ensure PostgreSQL, Redis, Python are installed correctly
4. **Check documentation** - Review SETUP_GUIDE.md and API_DOCUMENTATION.md
5. **Contact support** - Provide error messages and logs

---

## Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| `ModuleNotFoundError` | Python module not installed | Activate venv, run `pip install -r requirements.txt` |
| `Connection refused` | Service not running | Start PostgreSQL/Redis/Backend |
| `Permission denied` | Insufficient permissions | Check file permissions, don't use sudo with pip in venv |
| `Port already in use` | Another process using the port | Kill the process or use different port |
| `Invalid username or password` | Wrong credentials | Use admin/Admin@123 or reset password |
| `Not enough segments` | Invalid JWT token | Login again to get fresh token |
| `Database does not exist` | Database not created | Run database creation commands |
| `Relation does not exist` | Tables not created | Run `db.create_all()` |

---

**Troubleshooting Guide Version**: 1.0.0  
**Last Updated**: October 2025


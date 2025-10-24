# NBTI Promotion Automation - Setup Guide

Complete installation and configuration guide for Ubuntu 22.04+.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Database Setup](#database-setup)
4. [Environment Configuration](#environment-configuration)
5. [Initial Data Setup](#initial-data-setup)
6. [Starting the Application](#starting-the-application)
7. [Verification](#verification)

---

## System Requirements

### Minimum Requirements
- **OS**: Ubuntu 22.04 LTS or later
- **Python**: 3.11 or higher
- **PostgreSQL**: 14 or higher
- **Redis**: 6 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 20GB available space

### Required Software
- Git
- Python 3.11+
- PostgreSQL
- Redis
- pip (Python package manager)

---

## Installation Steps

### Step 1: Install System Dependencies

```bash
# Update package list
sudo apt update

# Install Python 3.11 and development tools
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install Redis
sudo apt install -y redis-server

# Install additional dependencies
sudo apt install -y build-essential libpq-dev git curl
```

### Step 2: Clone Repository

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/nbti-promotion-automation.git

# Navigate to project directory
cd nbti-promotion-automation
```

### Step 3: Backend Setup

```bash
# Navigate to backend directory
cd backend/nbti_api

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
```

---

## Database Setup

### Step 1: Create PostgreSQL Database

```bash
# Switch to postgres user and create database
sudo -u postgres psql << EOF
CREATE DATABASE nbti_promotion;
CREATE USER nbti_user WITH PASSWORD 'nbti_password_2024';
GRANT ALL PRIVILEGES ON DATABASE nbti_promotion TO nbti_user;
ALTER DATABASE nbti_promotion OWNER TO nbti_user;
\q
EOF
```

### Step 2: Initialize Database Tables

```bash
# Ensure you're in backend/nbti_api directory
cd ~/nbti-promotion-automation/backend/nbti_api

# Activate virtual environment
source venv/bin/activate

# Initialize database schema
python3 -c "from src.main import app, db; app.app_context().push(); db.create_all()"
```

### Step 3: Seed Salary Scale Data

```bash
# Load CONRAISS salary scale (180 records)
psql -U nbti_user -d nbti_promotion -h localhost -f seed_salary_scale.sql
# When prompted, enter password: nbti_password_2024
```

---

## Environment Configuration

### Step 1: Create Environment File

```bash
cd ~/nbti-promotion-automation/backend/nbti_api

# Copy example environment file
cp .env.example .env
```

### Step 2: Configure Environment Variables

Edit the `.env` file:

```bash
nano .env
```

**Required Configuration:**

```bash
# Database Configuration
DATABASE_URL=postgresql://nbti_user:nbti_password_2024@localhost:5432/nbti_promotion

# Security Keys (IMPORTANT: Generate unique keys for production)
SECRET_KEY=your-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-change-this-in-production

# Application Settings
FLASK_ENV=development
FLASK_DEBUG=True

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# AWS S3 Configuration (Optional - for file storage)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=nbti-promotion-files
AWS_REGION=us-east-1

# Email Configuration (Optional - for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@nbti.gov.ng
```

**To generate secure keys:**

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
# Run twice to generate two different keys
```

---

## Initial Data Setup

### Step 1: Create Admin User

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
        admin_role = Role(name='HR Admin', description='HR Administrator with full system access')
        db.session.add(admin_role)
        db.session.flush()
    
    # Create admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
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
        print('✓ Admin user created successfully')
        print('  Username: admin')
        print('  Password: Admin@123')
        print('  IMPORTANT: Change this password after first login!')
    else:
        print('✓ Admin user already exists')
EOF
```

### Step 2: Create Additional Roles

```bash
python3 << 'EOF'
from src.main import app, db
from src.models import Role

with app.app_context():
    roles = [
        ('Supervisor', 'Can evaluate supervised staff'),
        ('Second-Level Reviewer', 'Can review and calibrate evaluations'),
        ('Staff Member', 'Regular staff member'),
        ('Exam Administrator', 'Can create and manage exams'),
    ]
    
    for role_name, description in roles:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, description=description)
            db.session.add(role)
            print(f'✓ Created role: {role_name}')
    
    db.session.commit()
    print('\n✓ All roles created successfully')
EOF
```

---

## Starting the Application

### Method 1: Manual Start (Recommended for Development)

Open **3 separate terminal windows**:

**Terminal 1: Backend API**
```bash
cd ~/nbti-promotion-automation/backend/nbti_api
source venv/bin/activate
python3 src/main.py
```
Output: `Running on http://127.0.0.1:5000`

**Terminal 2: Celery Worker**
```bash
cd ~/nbti-promotion-automation/backend/nbti_api
source venv/bin/activate
celery -A src.celery_app.celery_app worker --loglevel=info
```

**Terminal 3: Celery Beat (Scheduler)**
```bash
cd ~/nbti-promotion-automation/backend/nbti_api
source venv/bin/activate
celery -A src.celery_app.celery_app beat --loglevel=info
```

### Method 2: Using Docker (Production)

```bash
cd ~/nbti-promotion-automation
docker-compose up -d
```

---

## Verification

### Step 1: Check Services

```bash
# Check PostgreSQL
sudo systemctl status postgresql
# Should show: active (running)

# Check Redis
sudo systemctl status redis-server
# Should show: active (running)

# Test Redis connection
redis-cli ping
# Should return: PONG
```

### Step 2: Test API

```bash
# Test health endpoint
curl http://localhost:5000/api/health
# Expected: {"status":"healthy"}

# Test login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123"}'
# Expected: JSON with access_token
```

### Step 3: Verify Database

```bash
cd ~/nbti-promotion-automation/backend/nbti_api
source venv/bin/activate

python3 << 'EOF'
from src.main import app, db
from src.models import User, SalaryScale

with app.app_context():
    user_count = User.query.count()
    salary_count = SalaryScale.query.count()
    
    print(f'✓ Users in database: {user_count}')
    print(f'✓ Salary scale records: {salary_count}')
    
    if salary_count == 180:
        print('✓ Salary scale data loaded correctly')
    else:
        print(f'⚠ Expected 180 salary records, found {salary_count}')
EOF
```

Expected output:
```
✓ Users in database: 1
✓ Salary scale records: 180
✓ Salary scale data loaded correctly
```

---

## Next Steps

After successful setup:

1. **Change Admin Password**
   - Login and change the default admin password immediately

2. **Import Users**
   - Use bulk import feature to add staff members
   - See [USER_GUIDE.md](USER_GUIDE.md) for instructions

3. **Configure System Settings**
   - Set up PMS cycles
   - Configure RRR thresholds
   - Set up exam categories

4. **Review Documentation**
   - [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference
   - [ADMIN_GUIDE.md](ADMIN_GUIDE.md) - Administration tasks
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues

---

## Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Restart if needed
sudo systemctl restart postgresql

# Verify database exists
sudo -u postgres psql -c "\l" | grep nbti_promotion
```

### Redis Connection Error

```bash
# Check Redis is running
sudo systemctl status redis-server

# Restart if needed
sudo systemctl restart redis-server

# Test connection
redis-cli ping
```

### Module Not Found Error

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Verify you're in the correct directory
pwd
# Should show: .../backend/nbti_api

# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use

```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill the process
sudo kill -9 <PID>
```

For more troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Security Notes

### Production Deployment

Before deploying to production:

1. **Change all default passwords**
2. **Generate new SECRET_KEY and JWT_SECRET_KEY**
3. **Set FLASK_DEBUG=False**
4. **Set FLASK_ENV=production**
5. **Enable HTTPS/SSL**
6. **Configure firewall rules**
7. **Set up regular database backups**
8. **Configure monitoring and logging**

### Secure Key Generation

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# Generate JWT_SECRET_KEY
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
```

---

## Support

For issues or questions:
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- Contact the development team

---

**Setup Guide Version**: 1.0.0  
**Last Updated**: October 2025  
**Tested On**: Ubuntu 22.04 LTS, Ubuntu 24.04 LTS


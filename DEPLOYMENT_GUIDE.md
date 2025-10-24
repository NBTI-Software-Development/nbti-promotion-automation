# Deployment Guide
## NBTI Promotion Automation System - Phase 1

---

## Prerequisites

### System Requirements
- **OS:** Ubuntu 22.04 LTS or similar
- **Python:** 3.9+
- **Node.js:** 18+ (for frontend)
- **PostgreSQL:** 14+
- **Redis:** 6+
- **Docker:** 20+ (optional, for containerized deployment)

### AWS Requirements
- AWS account with S3 access
- S3 bucket created
- IAM user with S3 permissions
- Access key and secret key

---

## Installation Steps

### 1. Clone Repository
```bash
git clone <repository-url>
cd nbti-promotion-automation
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd backend/nbti_api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Configure Environment Variables
```bash
cp .env.example .env
nano .env
```

Edit the following variables:
```bash
# Database (use PostgreSQL in production)
DATABASE_URL=postgresql://user:password@localhost:5432/nbti_promotion

# Security (generate strong random keys)
SECRET_KEY=<generate-strong-key>
JWT_SECRET_KEY=<generate-strong-key>

# Redis
REDIS_URL=redis://localhost:6379/0

# AWS S3
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>
AWS_S3_BUCKET=nbti-promotion-files
AWS_REGION=us-east-1

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=<your-email>
SMTP_PASSWORD=<your-app-password>
```

#### Initialize Database
```bash
# Create database
createdb nbti_promotion

# Run migrations (if using Flask-Migrate)
flask db upgrade

# Or let the app create tables automatically
python3 -c "from src.main import app, db; app.app_context().push(); db.create_all()"

# Seed salary scale data
python3 -c "from src.main import app, db; from src.models import SalaryScale; app.app_context().push(); exec(open('seed_salary_scale.sql').read())"
```

### 3. Redis Setup
```bash
# Install Redis
sudo apt-get update
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis
sudo systemctl enable redis

# Verify Redis is running
redis-cli ping  # Should return PONG
```

### 4. Celery Setup

#### Start Celery Worker
```bash
cd backend/nbti_api
celery -A src.celery_app.celery_app worker --loglevel=info
```

#### Start Celery Beat (for scheduled tasks)
```bash
celery -A src.celery_app.celery_app beat --loglevel=info
```

**Recommended:** Use supervisor or systemd to manage Celery processes in production.

### 5. Start Backend Server

#### Development
```bash
cd backend/nbti_api
python3 src/main.py
```

#### Production (with Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

### 6. Frontend Setup
```bash
cd frontend/nbti-frontend
npm install
npm run dev  # Development
npm run build  # Production
```

---

## Docker Deployment

### Using Docker Compose
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Services Included
- **backend:** Flask API (port 5000)
- **frontend:** React app (port 3000)
- **postgres:** PostgreSQL database (port 5432)
- **redis:** Redis server (port 6379)

---

## Initial Setup

### 1. Create Admin User
```bash
python3 -c "
from src.main import app, db
from src.models import User, Role

with app.app_context():
    # Create HR Admin role
    admin_role = Role(name='HR Admin', description='HR Administrator')
    db.session.add(admin_role)
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@nbti.gov.ng',
        first_name='System',
        last_name='Administrator',
        is_active=True
    )
    admin.set_password('ChangeMe123!')
    admin.add_role(admin_role)
    
    db.session.add(admin)
    db.session.commit()
    
    print('Admin user created: admin / ChangeMe123!')
"
```

### 2. Import Users
1. Download CSV template: `GET /api/import-export/users/template`
2. Fill in user data
3. Upload via API: `POST /api/import-export/users/import`

### 3. Configure System Settings
- Set RRR thresholds
- Configure PMS cycles
- Set up vacancy allocations

---

## Production Checklist

### Security
- [ ] Change all default passwords
- [ ] Generate strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Enable security headers
- [ ] Configure CORS properly

### Database
- [ ] Use PostgreSQL (not SQLite)
- [ ] Set up database backups
- [ ] Configure connection pooling
- [ ] Enable query logging
- [ ] Set up monitoring

### File Storage
- [ ] Create S3 bucket
- [ ] Configure bucket policies
- [ ] Enable versioning
- [ ] Set up lifecycle rules
- [ ] Configure CORS for S3

### Monitoring
- [ ] Set up application logging
- [ ] Configure error tracking (e.g., Sentry)
- [ ] Set up performance monitoring
- [ ] Configure health checks
- [ ] Set up alerts

### Backup
- [ ] Database daily backups
- [ ] S3 bucket replication
- [ ] Configuration backups
- [ ] Test restore procedures

---

## Maintenance

### Regular Tasks

#### Daily
- Monitor application logs
- Check Celery task queue
- Review audit logs

#### Weekly
- Review system performance
- Check disk space
- Review security logs

#### Monthly
- Update dependencies
- Review and optimize database
- Test backup restoration

### Troubleshooting

#### Application Won't Start
1. Check environment variables
2. Verify database connection
3. Check Redis connection
4. Review application logs

#### Celery Tasks Not Running
1. Verify Redis is running
2. Check Celery worker status
3. Review Celery logs
4. Verify task configuration

#### Database Issues
1. Check connection string
2. Verify database exists
3. Check user permissions
4. Review database logs

---

## Useful Commands

### Database
```bash
# Backup database
pg_dump nbti_promotion > backup.sql

# Restore database
psql nbti_promotion < backup.sql

# Check database size
psql -c "SELECT pg_size_pretty(pg_database_size('nbti_promotion'));"
```

### Redis
```bash
# Check Redis memory usage
redis-cli info memory

# Clear all Redis data
redis-cli FLUSHALL

# Monitor Redis commands
redis-cli MONITOR
```

### Celery
```bash
# Check active tasks
celery -A src.celery_app.celery_app inspect active

# Check scheduled tasks
celery -A src.celery_app.celery_app inspect scheduled

# Purge all tasks
celery -A src.celery_app.celery_app purge
```

### Application
```bash
# Check API health
curl http://localhost:5000/api/health

# View all routes
python3 -c "from src.main import app; print('\n'.join([str(r) for r in app.url_map.iter_rules()]))"

# Run tests
pytest tests/
```

---

## Support

For issues or questions:
1. Check application logs
2. Review this deployment guide
3. Consult the implementation summary
4. Contact the development team

---

**Last Updated:** October 24, 2025  
**Version:** Phase 1.0

# NBTI Promotion Automation System

A comprehensive web-based system for managing staff promotions, performance evaluations, and promotional examinations at the National Biotechnology Development Agency (NBTI).

## Overview

This system automates the promotion process using the **Recommendation, Recognition, and Reward (RRR) Policy**:
- **70% Promotional Exam Score**
- **20% Performance Management System (PMS) Score**  
- **10% Seniority Score**

---

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Ubuntu 22.04+ (or similar Linux distribution)

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/YOUR_USERNAME/nbti-promotion-automation.git
cd nbti-promotion-automation
```

2. **Backend Setup**
```bash
cd backend/nbti_api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
```

3. **Database Setup**
```bash
# Create PostgreSQL database
sudo -u postgres psql -c "CREATE DATABASE nbti_promotion;"
sudo -u postgres psql -c "CREATE USER nbti_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE nbti_promotion TO nbti_user;"

# Initialize tables
python3 -c "from src.main import app, db; app.app_context().push(); db.create_all()"
```

4. **Start Services**
```bash
# Terminal 1: Backend
python3 src/main.py

# Terminal 2: Celery Worker
celery -A src.celery_app.celery_app worker --loglevel=info

# Terminal 3: Celery Beat
celery -A src.celery_app.celery_app beat --loglevel=info
```

See **[docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** for detailed instructions.

---

## Key Features

- ✅ RRR Calculation (70/20/10 formula)
- ✅ Rank-based promotion allocation
- ✅ Performance Management System (PMS)
- ✅ Exam Management Module (EMM)
- ✅ CONRAISS-based eligibility
- ✅ Automated step increment
- ✅ Forensic audit logging
- ✅ Bulk user import/export

---

## Documentation

- **[Setup Guide](docs/SETUP_GUIDE.md)** - Installation and configuration
- **[API Documentation](docs/API_DOCUMENTATION.md)** - API reference
- **[User Guide](docs/USER_GUIDE.md)** - End-user documentation
- **[Admin Guide](docs/ADMIN_GUIDE.md)** - System administration
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues

---

## Technology Stack

- **Backend**: Flask, SQLAlchemy, Celery
- **Database**: PostgreSQL
- **Cache**: Redis
- **Frontend**: React, Vite
- **Storage**: AWS S3

---

## License

Proprietary - National Biotechnology Development Agency (NBTI)

---

**Version**: 1.0.0 | **Status**: Production Ready

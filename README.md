# NBTI Promotion Automation System

A comprehensive web application for automating the staff promotion process at the National Board for Technology Incubation (NBTI), featuring Performance Management System (PMS) and Exam Management Module (EMM).

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Local Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd nbti-promotion-automation
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Start the development environment:
```bash
docker-compose up --build
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- API Documentation: http://localhost:5000/docs

## Project Structure

```
nbti-promotion-automation/
├── backend/
│   └── nbti_api/           # Flask API application
├── frontend/
│   └── nbti-frontend/      # React frontend application
├── docs/                   # Documentation
├── scripts/                # Utility scripts
├── docker-compose.yml      # Development environment
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Features

### Performance Management System (PMS)
- User roles and permissions
- Quarterly evaluation cycles
- Goal setting and tracking
- Performance evaluation and scoring
- Dashboard for evaluation status

### Exam Management Module (EMM)
- Question bank management (MCQs)
- Exam creation and configuration
- Secure exam-taking environment
- Automated grading
- Integration with PMS for promotion scoring

## Technology Stack

- **Frontend:** React, TypeScript, TailwindCSS, shadcn/ui
- **Backend:** Python, Flask, SQLAlchemy
- **Database:** PostgreSQL
- **Authentication:** JWT with refresh tokens
- **DevOps:** Docker, Docker Compose

## Development

### Backend Development
```bash
cd backend/nbti_api
source venv/bin/activate
python src/main.py
```

### Frontend Development
```bash
cd frontend/nbti-frontend
pnpm run dev
```

### Testing
```bash
# Backend tests
cd backend/nbti_api
pytest

# Frontend tests
cd frontend/nbti-frontend
npm test
```

## API Documentation

The API documentation is automatically generated using OpenAPI/Swagger and is available at:
- Development: http://localhost:5000/docs
- Production: https://your-domain.com/docs

## Security

- JWT-based authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- CORS configuration for frontend-backend communication
- Environment-based configuration management

## Deployment

See `EXPORT_INSTRUCTIONS.md` for detailed deployment instructions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is proprietary software developed for NBTI.


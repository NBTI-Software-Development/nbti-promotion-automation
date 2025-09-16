#!/bin/bash

# NBTI Promotion Automation - Deployment Script
# This script handles the deployment of the application in different environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="development"
BUILD_FRONTEND=true
BUILD_BACKEND=true
RUN_MIGRATIONS=true
SKIP_TESTS=false

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Set environment (development|staging|production) [default: development]"
    echo "  -f, --no-frontend       Skip frontend build"
    echo "  -b, --no-backend        Skip backend build"
    echo "  -m, --no-migrations     Skip database migrations"
    echo "  -t, --skip-tests        Skip running tests"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -e production                    # Deploy to production"
    echo "  $0 -e development --skip-tests      # Deploy to development without tests"
    echo "  $0 -e staging --no-frontend         # Deploy to staging without rebuilding frontend"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -f|--no-frontend)
            BUILD_FRONTEND=false
            shift
            ;;
        -b|--no-backend)
            BUILD_BACKEND=false
            shift
            ;;
        -m|--no-migrations)
            RUN_MIGRATIONS=false
            shift
            ;;
        -t|--skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    print_error "Valid environments: development, staging, production"
    exit 1
fi

print_status "Starting deployment for environment: $ENVIRONMENT"

# Check if required files exist
if [[ ! -f ".env.$ENVIRONMENT" ]]; then
    print_error "Environment file .env.$ENVIRONMENT not found!"
    exit 1
fi

if [[ ! -f "docker-compose.yml" ]]; then
    print_error "docker-compose.yml not found!"
    exit 1
fi

# Load environment variables
print_status "Loading environment configuration..."
export $(cat .env.$ENVIRONMENT | grep -v '^#' | xargs)

# Pre-deployment checks
print_status "Running pre-deployment checks..."

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed or not in PATH"
    exit 1
fi

# Check if ports are available (for development)
if [[ "$ENVIRONMENT" == "development" ]]; then
    if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null ; then
        print_warning "Port 5000 is already in use"
    fi
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
        print_warning "Port 3000 is already in use"
    fi
fi

# Run tests (unless skipped)
if [[ "$SKIP_TESTS" == false ]]; then
    print_status "Running tests..."
    
    # Backend tests
    if [[ "$BUILD_BACKEND" == true ]]; then
        print_status "Running backend tests..."
        cd backend/nbti_api
        if [[ -f "test_runner.py" ]]; then
            python test_runner.py || print_warning "Some backend tests failed"
        else
            print_warning "Backend test runner not found, skipping backend tests"
        fi
        cd ../..
    fi
    
    # Frontend tests
    if [[ "$BUILD_FRONTEND" == true ]]; then
        print_status "Running frontend tests..."
        cd frontend/nbti-frontend
        if [[ -f "package.json" ]] && grep -q "test:run" package.json; then
            pnpm test:run || print_warning "Some frontend tests failed"
        else
            print_warning "Frontend tests not configured, skipping frontend tests"
        fi
        cd ../..
    fi
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose down --remove-orphans

# Build and start services
print_status "Building and starting services..."

if [[ "$ENVIRONMENT" == "production" ]]; then
    # Production deployment with all services
    docker-compose --profile production up -d --build
else
    # Development/staging deployment
    docker-compose up -d --build
fi

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
sleep 10

# Check service health
print_status "Checking service health..."

# Check database
if docker-compose ps database | grep -q "healthy"; then
    print_success "Database is healthy"
else
    print_error "Database is not healthy"
    docker-compose logs database
    exit 1
fi

# Check backend
if docker-compose ps backend | grep -q "healthy"; then
    print_success "Backend is healthy"
else
    print_error "Backend is not healthy"
    docker-compose logs backend
    exit 1
fi

# Check frontend
if docker-compose ps frontend | grep -q "healthy"; then
    print_success "Frontend is healthy"
else
    print_error "Frontend is not healthy"
    docker-compose logs frontend
    exit 1
fi

# Run database migrations
if [[ "$RUN_MIGRATIONS" == true ]]; then
    print_status "Running database migrations..."
    docker-compose exec backend flask db upgrade || print_warning "Migration failed or no migrations to run"
fi

# Initialize default data (for development)
if [[ "$ENVIRONMENT" == "development" ]]; then
    print_status "Initializing default data..."
    docker-compose exec backend python -c "
from src.main import create_app
from src.models.user import db, User, Role
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Create default admin user if not exists
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_role = Role.query.filter_by(name='HR Admin').first()
        if admin_role:
            admin_user = User(
                username='admin',
                email='admin@nbti.com',
                first_name='System',
                last_name='Administrator',
                password_hash=generate_password_hash('admin123')
            )
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)
            db.session.commit()
            print('Default admin user created')
        else:
            print('Admin role not found')
    else:
        print('Admin user already exists')
" || print_warning "Failed to initialize default data"
fi

# Show deployment summary
print_success "Deployment completed successfully!"
echo ""
print_status "Deployment Summary:"
echo "  Environment: $ENVIRONMENT"
echo "  Frontend URL: http://localhost:${FRONTEND_PORT:-3000}"
echo "  Backend URL: http://localhost:${BACKEND_PORT:-5000}"
echo "  API Documentation: http://localhost:${BACKEND_PORT:-5000}/api/docs"
echo ""

if [[ "$ENVIRONMENT" == "development" ]]; then
    print_status "Development credentials:"
    echo "  Username: admin"
    echo "  Password: admin123"
    echo ""
fi

print_status "To view logs: docker-compose logs -f [service_name]"
print_status "To stop services: docker-compose down"

# Show running containers
print_status "Running containers:"
docker-compose ps


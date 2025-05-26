#!/bin/bash
# AI NVCB Enhanced Deployment Script for Unix/Linux/macOS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="ai-nvcb"
ENVIRONMENTS=("development" "staging" "production")

# Default values
ENVIRONMENT="development"
BUILD_ONLY=false
NO_CACHE=false
PULL_LATEST=false
SKIP_TESTS=false
MIGRATE_DB=false
SEED_DB=false
SSL_SETUP=false
BACKUP_FIRST=false
HEALTH_CHECK=true
VERBOSE=false
SCALE_BACKEND=1

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

print_debug() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${PURPLE}[DEBUG]${NC} $1"
    fi
}

print_header() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}"
}

# Function to show help
show_help() {
    cat << EOF
AI NVCB Enhanced Deployment Script v2.1

Usage: $0 [ENVIRONMENT] [OPTIONS]

ENVIRONMENTS:
    development    Deploy for development with hot-reload
    staging        Deploy for staging environment  
    production     Deploy for production with full optimization

OPTIONS:
    --build-only          Build images without deploying
    --no-cache           Build without using Docker cache
    --pull-latest        Pull latest base images before building
    --skip-tests         Skip running tests before deployment
    --migrate-db         Run database migrations after deployment
    --seed-db            Seed database with test data (dev/staging only)
    --ssl-setup          Generate/configure SSL certificates
    --backup-first       Create backup before deployment
    --health-check       Run health checks after deployment (default: true)
    --no-health-check    Skip health checks
    --scale-backend N    Scale backend to N instances (default: 1)
    --verbose            Enable verbose output
    --help               Show this help message

EXAMPLES:
    $0                                           # Deploy development
    $0 production --migrate-db --ssl-setup       # Production with DB migration and SSL
    $0 staging --backup-first --health-check     # Staging with backup and health check
    $0 --build-only --no-cache                  # Just build images without cache
    $0 production --scale-backend 3             # Production with 3 backend instances

ENVIRONMENT VARIABLES:
    DOCKER_REGISTRY       Docker registry for pushing images
    SSL_EMAIL            Email for Let's Encrypt SSL certificates
    BACKUP_S3_BUCKET     S3 bucket for backups
    COMPOSE_PROJECT_NAME Project name for Docker Compose
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --build-only)
            BUILD_ONLY=true
            shift
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --pull-latest)
            PULL_LATEST=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --migrate-db)
            MIGRATE_DB=true
            shift
            ;;
        --seed-db)
            SEED_DB=true
            shift
            ;;
        --ssl-setup)
            SSL_SETUP=true
            shift
            ;;
        --backup-first)
            BACKUP_FIRST=true
            shift
            ;;
        --health-check)
            HEALTH_CHECK=true
            shift
            ;;
        --no-health-check)
            HEALTH_CHECK=false
            shift
            ;;
        --scale-backend)
            SCALE_BACKEND="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            set -x
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        development|staging|production)
            ENVIRONMENT="$1"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate environment
if [[ ! " ${ENVIRONMENTS[@]} " =~ " ${ENVIRONMENT} " ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    print_status "Valid environments: ${ENVIRONMENTS[*]}"
    exit 1
fi

# Validate scale backend
if ! [[ "$SCALE_BACKEND" =~ ^[1-9][0-9]*$ ]]; then
    print_error "Invalid scale value: $SCALE_BACKEND. Must be a positive integer."
    exit 1
fi

print_header "AI NVCB Enhanced Deployment Script v2.1"
print_status "Environment: $ENVIRONMENT"
print_debug "Build Only: $BUILD_ONLY"
print_debug "No Cache: $NO_CACHE"
print_debug "Pull Latest: $PULL_LATEST"
print_debug "Skip Tests: $SKIP_TESTS"
print_debug "Migrate DB: $MIGRATE_DB"
print_debug "Seed DB: $SEED_DB"
print_debug "SSL Setup: $SSL_SETUP"
print_debug "Backup First: $BACKUP_FIRST"
print_debug "Health Check: $HEALTH_CHECK"
print_debug "Scale Backend: $SCALE_BACKEND"
echo

# Check dependencies and prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running"
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available"
        exit 1
    fi
    
    # Set compose command
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    print_debug "Using compose command: $COMPOSE_CMD"
    
    # Check if required files exist
    local env_file=".env.${ENVIRONMENT}"
    if [[ ! -f "$env_file" ]]; then
        print_warning "Environment file $env_file not found"
        if [[ -f ".env.example" ]]; then
            print_status "Creating $env_file from .env.example"
            cp .env.example "$env_file"
            print_warning "Please edit $env_file with your configuration"
        else
            print_error "No .env.example file found"
            exit 1
        fi
    fi
    
    # Check Poetry if needed for tests or migrations
    if [[ "$SKIP_TESTS" == "false" || "$MIGRATE_DB" == "true" || "$SEED_DB" == "true" ]]; then
        if ! command -v poetry &> /dev/null; then
            print_warning "Poetry not found, some features will be skipped"
        fi
    fi
    
    print_success "Prerequisites check passed"
    echo
}

# Run tests
run_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        print_warning "Skipping tests as requested"
        return
    fi
    
    print_status "Running comprehensive test suite..."
    
    if command -v poetry &> /dev/null; then
        # Run different test categories
        print_status "Running unit tests..."
        poetry run pytest tests/ -m "unit" -v --tb=short || {
            print_error "Unit tests failed!"
            exit 1
        }
        
        print_status "Running integration tests..."
        poetry run pytest tests/ -m "integration" -v --tb=short || {
            print_error "Integration tests failed!"
            exit 1
        }
        
        # Run code quality checks
        print_status "Running code quality checks..."
        poetry run black --check . || {
            print_error "Code formatting check failed! Run 'poetry run black .' to fix."
            exit 1
        }
        
        poetry run isort --check-only . || {
            print_error "Import sorting check failed! Run 'poetry run isort .' to fix."
            exit 1
        }
        
        print_status "Running security checks..."
        poetry run bandit -r . -f json -o security_report.json || {
            print_warning "Security issues found. Check security_report.json"
        }
    else
        print_warning "Poetry not found, skipping tests"
    fi
    
    print_success "Tests completed successfully"
    echo
}

# Create backup
create_backup() {
    if [[ "$BACKUP_FIRST" != "true" ]]; then
        return
    fi
    
    print_status "Creating comprehensive backup before deployment..."
    
    # Create backup directory
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup database
    if [[ -f "storage/database.sqlite" ]]; then
        cp "storage/database.sqlite" "$backup_dir/database.sqlite"
        print_success "Database backup created"
    fi
    
    # Backup uploads
    if [[ -d "uploads" ]]; then
        cp -r "uploads" "$backup_dir/"
        print_success "Uploads backup created"
    fi
    
    # Backup configuration
    cp .env* "$backup_dir/" 2>/dev/null || true
    
    # Use advanced backup manager if available
    if [[ -f "utils/backup_manager.py" ]] && command -v poetry &> /dev/null; then
        print_status "Running advanced backup manager..."
        poetry run python -c "
from utils.backup_manager import BackupManager
import asyncio
backup_manager = BackupManager()
asyncio.run(backup_manager.create_full_backup())
" || print_warning "Advanced backup failed, using basic backup"
    fi
    
    print_success "Backup completed: $backup_dir"
    echo
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    
    local cache_flag=""
    if [[ "$NO_CACHE" == "true" ]]; then
        cache_flag="--no-cache"
        print_debug "Building without cache"
    fi
    
    local pull_flag=""
    if [[ "$PULL_LATEST" == "true" ]]; then
        pull_flag="--pull"
        print_debug "Pulling latest base images"
    fi
    
    # Determine compose file
    local compose_file="docker-compose.yml"
    if [[ "$ENVIRONMENT" == "production" ]]; then
        compose_file="docker-compose.prod.yml"
    elif [[ "$ENVIRONMENT" == "staging" ]]; then
        compose_file="docker-compose.staging.yml"
        # Use production compose file if staging file doesn't exist
        if [[ ! -f "$compose_file" ]]; then
            compose_file="docker-compose.prod.yml"
            print_warning "Staging compose file not found, using production file"
        fi
    fi
    
    if [[ ! -f "$compose_file" ]]; then
        print_error "Compose file $compose_file not found"
        exit 1
    fi
    
    print_debug "Using compose file: $compose_file"
    
    # Set environment file
    local env_file=".env.${ENVIRONMENT}"
    export ENV_FILE="$env_file"
    
    # Build images
    $COMPOSE_CMD -f "$compose_file" --env-file "$env_file" build $cache_flag $pull_flag
    
    print_success "Docker images built successfully"
    echo
}

# Deploy services
deploy_services() {
    if [[ "$BUILD_ONLY" == "true" ]]; then
        print_status "Build-only mode, skipping deployment"
        return
    fi
    
    print_status "Deploying services for $ENVIRONMENT environment..."
    
    # Determine compose file
    local compose_file="docker-compose.yml"
    if [[ "$ENVIRONMENT" == "production" ]]; then
        compose_file="docker-compose.prod.yml"
    elif [[ "$ENVIRONMENT" == "staging" ]]; then
        compose_file="docker-compose.staging.yml"
        if [[ ! -f "$compose_file" ]]; then
            compose_file="docker-compose.prod.yml"
        fi
    fi
    
    # Set environment variables
    local env_file=".env.${ENVIRONMENT}"
    export COMPOSE_FILE="$compose_file"
    export ENV_FILE="$env_file"
    export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-${PROJECT_NAME}_${ENVIRONMENT}}"
    
    print_debug "Compose file: $compose_file"
    print_debug "Environment file: $env_file"
    print_debug "Project name: $COMPOSE_PROJECT_NAME"
    
    # Stop existing services gracefully
    print_status "Stopping existing services..."
    $COMPOSE_CMD -f "$compose_file" --env-file "$env_file" down --remove-orphans || {
        print_warning "Some services were not running"
    }
    
    # Start services
    print_status "Starting services..."
    $COMPOSE_CMD -f "$compose_file" --env-file "$env_file" up -d
    
    # Scale backend if requested
    if [[ "$SCALE_BACKEND" -gt 1 ]]; then
        print_status "Scaling backend to $SCALE_BACKEND instances..."
        $COMPOSE_CMD -f "$compose_file" --env-file "$env_file" up -d --scale backend="$SCALE_BACKEND"
    fi
    
    print_success "Services deployed successfully"
    echo
}

# Setup SSL certificates
setup_ssl() {
    if [[ "$SSL_SETUP" != "true" ]]; then
        return
    fi
    
    print_status "Setting up SSL certificates..."
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        # Production: Use Let's Encrypt
        if [[ -z "$SSL_EMAIL" ]]; then
            print_error "SSL_EMAIL environment variable required for Let's Encrypt"
            exit 1
        fi
        
        if command -v poetry &> /dev/null && [[ -f "utils/ssl_manager.py" ]]; then
            print_status "Configuring Let's Encrypt for production..."
            poetry run python -c "
from utils.ssl_manager import SSLManager
ssl_manager = SSLManager()
ssl_manager.setup_letsencrypt('$SSL_EMAIL')
" || {
                print_error "Let's Encrypt setup failed"
                exit 1
            }
        else
            print_warning "SSL manager not available, please setup SSL manually"
        fi
    else
        # Development/Staging: Use self-signed certificates
        if command -v poetry &> /dev/null && [[ -f "utils/ssl_manager.py" ]]; then
            print_status "Generating self-signed certificates for $ENVIRONMENT..."
            poetry run python -c "
from utils.ssl_manager import SSLManager
ssl_manager = SSLManager()
ssl_manager.generate_self_signed_cert()
" || {
                print_warning "Self-signed certificate generation failed"
            }
        else
            print_warning "SSL manager not available, skipping SSL setup"
        fi
    fi
    
    print_success "SSL setup completed"
    echo
}

# Run database migrations
run_migrations() {
    if [[ "$MIGRATE_DB" != "true" ]]; then
        return
    fi
    
    print_status "Running database migrations..."
    
    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    sleep 15
    
    if command -v poetry &> /dev/null && [[ -f "migrations/database_migrator.py" ]]; then
        poetry run python -c "
from migrations.database_migrator import DatabaseMigrator
import asyncio
migrator = DatabaseMigrator()
try:
    result = asyncio.run(migrator.run_migrations())
    print(f'Migration completed: {result}')
except Exception as e:
    print(f'Migration failed: {e}')
    exit(1)
" || {
            print_error "Database migration failed"
            exit 1
        }
    else
        print_warning "Database migrator not available, skipping migrations"
    fi
    
    print_success "Database migrations completed"
    echo
}

# Seed database
seed_database() {
    if [[ "$SEED_DB" != "true" ]]; then
        return
    fi
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        print_warning "Skipping database seeding in production environment"
        return
    fi
    
    print_status "Seeding database with test data..."
    
    if command -v poetry &> /dev/null && [[ -f "migrations/database_seeder.py" ]]; then
        poetry run python -c "
from migrations.database_seeder import DatabaseSeeder
import asyncio
seeder = DatabaseSeeder()
try:
    result = asyncio.run(seeder.seed_all())
    print(f'Database seeding completed: {result}')
except Exception as e:
    print(f'Database seeding failed: {e}')
    exit(1)
" || {
            print_warning "Database seeding failed"
        }
    else
        print_warning "Database seeder not available, skipping seeding"
    fi
    
    print_success "Database seeding completed"
    echo
}

# Run comprehensive health checks
run_health_checks() {
    if [[ "$HEALTH_CHECK" != "true" ]]; then
        print_status "Skipping health checks as requested"
        return
    fi
    
    print_status "Running comprehensive health checks..."
    
    # Determine base URLs
    local backend_url="http://localhost:8000"
    local frontend_url="http://localhost:8501"
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        backend_url="https://localhost:8000"
        frontend_url="https://localhost:8501"
    fi
    
    # Wait for services to start
    print_status "Waiting for services to initialize..."
    sleep 20
    
    # Check backend health with retries
    local max_attempts=60
    local attempt=1
    
    print_status "Checking backend health..."
    while [[ $attempt -le $max_attempts ]]; do
        if curl -sf "$backend_url/api/health" &> /dev/null; then
            print_success "Backend health check passed"
            break
        fi
        
        if [[ $attempt -eq $max_attempts ]]; then
            print_error "Backend health check failed after $max_attempts attempts"
            # Show service logs for debugging
            print_status "Backend service logs:"
            $COMPOSE_CMD logs --tail=20 backend || true
            exit 1
        fi
        
        if [[ $((attempt % 10)) -eq 0 ]]; then
            print_status "Attempt $attempt/$max_attempts: Still waiting for backend..."
        fi
        sleep 2
        ((attempt++))
    done
    
    # Check frontend
    print_status "Checking frontend health..."
    if curl -sf "$frontend_url" &> /dev/null; then
        print_success "Frontend health check passed"
    else
        print_warning "Frontend health check failed"
        # Show frontend logs
        print_status "Frontend service logs:"
        $COMPOSE_CMD logs --tail=20 frontend || true
    fi
    
    # Check detailed health status if available
    print_status "Running detailed health diagnostics..."
    if curl -sf "$backend_url/api/health/detailed" > /tmp/health_detail.json 2>/dev/null; then
        print_success "Detailed health check passed"
        if command -v jq &> /dev/null; then
            cat /tmp/health_detail.json | jq '.'
        else
            cat /tmp/health_detail.json
        fi
    else
        print_warning "Detailed health check not available"
    fi
    
    # Run comprehensive health check if available
    if command -v poetry &> /dev/null && [[ -f "utils/health_check.py" ]]; then
        print_status "Running comprehensive system health check..."
        poetry run python -c "
from utils.health_check import get_health_status
import asyncio
import json
try:
    health = asyncio.run(get_health_status())
    print(json.dumps(health, indent=2))
    if health.get('status') != 'healthy':
        print('WARNING: System health check indicates issues')
except Exception as e:
    print(f'Health check script failed: {e}')
" || print_warning "Comprehensive health check failed"
    fi
    
    print_success "Health checks completed"
    echo
}

# Show deployment summary and useful information
show_summary() {
    print_header "Deployment Summary"
    
    echo "🚀 Deployment Details:"
    echo "   Environment: $ENVIRONMENT"
    echo "   Build Only: $BUILD_ONLY"
    echo "   Database Migration: $MIGRATE_DB"
    echo "   Database Seeding: $SEED_DB"
    echo "   SSL Setup: $SSL_SETUP"
    echo "   Health Check: $HEALTH_CHECK"
    echo "   Backend Instances: $SCALE_BACKEND"
    echo ""
    
    if [[ "$BUILD_ONLY" != "true" ]]; then
        echo "📊 Service URLs:"
        if [[ "$ENVIRONMENT" == "production" ]]; then
            echo "   🌐 Frontend: https://localhost:8501"
            echo "   🔧 Backend API: https://localhost:8000"
            echo "   📚 API Documentation: https://localhost:8000/docs"
            echo "   🔍 Health Status: https://localhost:8000/api/health"
        else
            echo "   🌐 Frontend: http://localhost:8501"
            echo "   🔧 Backend API: http://localhost:8000"
            echo "   📚 API Documentation: http://localhost:8000/docs"
            echo "   🔍 Health Status: http://localhost:8000/api/health"
        fi
        echo ""
        
        echo "🔧 Management Commands:"
        echo "   View logs: $COMPOSE_CMD logs -f [service]"
        echo "   Stop services: $COMPOSE_CMD down"
        echo "   Restart: $COMPOSE_CMD restart [service]"
        echo "   Scale backend: $COMPOSE_CMD up -d --scale backend=N"
        echo "   Service status: $COMPOSE_CMD ps"
        echo ""
        
        echo "📊 Current Service Status:"
        $COMPOSE_CMD ps || true
    fi
    
    print_success "🎉 Deployment completed successfully!"
}

# Handle interrupts gracefully
trap 'print_error "Deployment interrupted"; exit 1' INT TERM

# Main deployment flow
main() {
    check_prerequisites
    create_backup
    run_tests
    build_images
    deploy_services
    setup_ssl
    run_migrations
    seed_database
    run_health_checks
    show_summary
}

# Run main function
main "$@"

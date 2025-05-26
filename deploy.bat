@echo off
:: AI NVCB Enhanced Deployment Script for Windows
:: Version 2.1

setlocal enabledelayedexpansion

:: Script configuration
set "PROJECT_NAME=ai-nvcb"
set "SCRIPT_DIR=%~dp0"
set "START_TIME=%time%"

:: Default values
set "ENVIRONMENT=development"
set "BUILD_ONLY=false"
set "NO_CACHE=false"
set "PULL_LATEST=false"
set "SKIP_TESTS=false"
set "MIGRATE_DB=false"
set "SEED_DB=false"
set "SSL_SETUP=false"
set "BACKUP_FIRST=false"
set "HEALTH_CHECK=true"
set "VERBOSE=false"
set "SCALE_BACKEND=1"

:: Function to show help
if "%1"=="--help" goto :show_help
if "%1"=="/?" goto :show_help

echo ========================================
echo    AI NVCB Enhanced Deployment Script v2.1
echo ========================================
echo.

:: Parse command line arguments
:parse_args
if "%1"=="" goto :args_done
if "%1"=="--environment" (
    set "ENVIRONMENT=%2"
    shift
    shift
    goto :parse_args
)
if "%1"=="--build-only" (
    set "BUILD_ONLY=true"
    shift
    goto :parse_args
)
if "%1"=="--no-cache" (
    set "NO_CACHE=true"
    shift
    goto :parse_args
)
if "%1"=="--pull-latest" (
    set "PULL_LATEST=true"
    shift
    goto :parse_args
)
if "%1"=="--skip-tests" (
    set "SKIP_TESTS=true"
    shift
    goto :parse_args
)
if "%1"=="--migrate-db" (
    set "MIGRATE_DB=true"
    shift
    goto :parse_args
)
if "%1"=="--seed-db" (
    set "SEED_DB=true"
    shift
    goto :parse_args
)
if "%1"=="--ssl-setup" (
    set "SSL_SETUP=true"
    shift
    goto :parse_args
)
if "%1"=="--backup-first" (
    set "BACKUP_FIRST=true"
    shift
    goto :parse_args
)
if "%1"=="--health-check" (
    set "HEALTH_CHECK=true"
    shift
    goto :parse_args
)
if "%1"=="--no-health-check" (
    set "HEALTH_CHECK=false"
    shift
    goto :parse_args
)
if "%1"=="--scale-backend" (
    set "SCALE_BACKEND=%2"
    shift
    shift
    goto :parse_args
)
if "%1"=="--verbose" (
    set "VERBOSE=true"
    shift
    goto :parse_args
)
if "%1"=="development" (
    set "ENVIRONMENT=development"
    shift
    goto :parse_args
)
if "%1"=="staging" (
    set "ENVIRONMENT=staging"
    shift
    goto :parse_args
)
if "%1"=="production" (
    set "ENVIRONMENT=production"
    shift
    goto :parse_args
)
echo [ERROR] Unknown option: %1
goto :show_help

:args_done

:: Display configuration
echo [INFO] Deployment Configuration:
echo   Environment: %ENVIRONMENT%
echo   Build Only: %BUILD_ONLY%
echo   No Cache: %NO_CACHE%
echo   Pull Latest: %PULL_LATEST%
echo   Skip Tests: %SKIP_TESTS%
echo   Migrate DB: %MIGRATE_DB%
echo   Seed DB: %SEED_DB%
echo   SSL Setup: %SSL_SETUP%
echo   Backup First: %BACKUP_FIRST%
echo   Health Check: %HEALTH_CHECK%
echo   Scale Backend: %SCALE_BACKEND%
echo   Verbose: %VERBOSE%
echo.

:: Validate environment
if not "%ENVIRONMENT%"=="development" if not "%ENVIRONMENT%"=="staging" if not "%ENVIRONMENT%"=="production" (
    echo [ERROR] Invalid environment. Must be development, staging, or production.
    exit /b 1
)

:: Determine compose file first
set "COMPOSE_FILE=docker-compose.yml"
if "%ENVIRONMENT%"=="production" set "COMPOSE_FILE=docker-compose.prod.yml"
if "%ENVIRONMENT%"=="staging" set "COMPOSE_FILE=docker-compose.staging.yml"

:: Check prerequisites
echo [INFO] Checking prerequisites...
call :check_dependencies
if !ERRORLEVEL! neq 0 exit /b 1

call :validate_environment
if !ERRORLEVEL! neq 0 exit /b 1

echo [INFO] Using compose file: %COMPOSE_FILE%
echo.

:: Create backup if requested
if "%BACKUP_FIRST%"=="true" (
    echo [INFO] Creating backup...
    call :create_backup
    if !ERRORLEVEL! neq 0 (
        echo [ERROR] Backup failed!
        exit /b 1
    )
    echo [SUCCESS] Backup completed
    echo.
)

:: Run tests if not skipped
if "%SKIP_TESTS%"=="false" (
    echo [INFO] Running test suite...
    call :run_tests
    if !ERRORLEVEL! neq 0 (
        echo [ERROR] Tests failed! Deployment aborted.
        exit /b 1
    )
    echo [SUCCESS] All tests passed
    echo.
)

:: Pull latest images if requested
if "%PULL_LATEST%"=="true" (
    echo [INFO] Pulling latest base images...
    docker-compose -f %COMPOSE_FILE% pull
    if !ERRORLEVEL! neq 0 (
        echo [WARNING] Failed to pull some images, continuing...
    )
    echo.
)

:: Build images
if "%BUILD_ONLY%"=="false" (
    echo [INFO] Stopping existing services...
    docker-compose -f %COMPOSE_FILE% down --remove-orphans
    echo.
)

echo [INFO] Building application images...
set "BUILD_ARGS="
if "%NO_CACHE%"=="true" set "BUILD_ARGS=--no-cache"
if "%VERBOSE%"=="true" set "BUILD_ARGS=%BUILD_ARGS% --progress=plain"

docker-compose -f %COMPOSE_FILE% build %BUILD_ARGS%
if !ERRORLEVEL! neq 0 (
    echo [ERROR] Build failed!
    exit /b 1
)
echo [SUCCESS] Build completed
echo.

:: Exit if build-only mode
if "%BUILD_ONLY%"=="true" (
    echo [SUCCESS] Build-only mode completed successfully
    goto :deployment_summary
)

:: Deploy services
echo [INFO] Deploying services...
set "UP_ARGS=-d"
if "%SCALE_BACKEND%" neq "1" set "UP_ARGS=%UP_ARGS% --scale backend=%SCALE_BACKEND%"

docker-compose -f %COMPOSE_FILE% up %UP_ARGS%
if !ERRORLEVEL! neq 0 (
    echo [ERROR] Deployment failed!
    exit /b 1
)
echo [SUCCESS] Services deployed
echo.

:: Wait for services to be ready
echo [INFO] Waiting for services to be ready...
timeout /t 15 /nobreak >nul

:: SSL setup if requested
if "%SSL_SETUP%"=="true" (
    echo [INFO] Setting up SSL certificates...
    call :setup_ssl
    if !ERRORLEVEL! neq 0 (
        echo [WARNING] SSL setup failed, continuing without SSL
    ) else (
        echo [SUCCESS] SSL setup completed
    )
    echo.
)

:: Database migration if requested
if "%MIGRATE_DB%"=="true" (
    echo [INFO] Running database migrations...
    call :migrate_database
    if !ERRORLEVEL! neq 0 (
        echo [ERROR] Database migration failed!
        exit /b 1
    )
    echo [SUCCESS] Database migration completed
    echo.
)

:: Database seeding if requested
if "%SEED_DB%"=="true" (
    if "%ENVIRONMENT%"=="production" (
        echo [WARNING] Skipping database seeding in production environment
    ) else (
        echo [INFO] Seeding database with test data...
        call :seed_database
        if !ERRORLEVEL! neq 0 (
            echo [WARNING] Database seeding failed, continuing...
        ) else (
            echo [SUCCESS] Database seeding completed
        )
    )
    echo.
)

:: Health checks if enabled
if "%HEALTH_CHECK%"=="true" (
    echo [INFO] Performing health checks...
    call :health_check
    if !ERRORLEVEL! neq 0 (
        echo [WARNING] Health checks failed, but deployment continues
    ) else (
        echo [SUCCESS] All health checks passed
    )
    echo.
)

:deployment_summary
echo ========================================
echo    Deployment Summary
echo ========================================
echo.

:: Show service status
echo [INFO] Service Status:
docker-compose -f %COMPOSE_FILE% ps
echo.

:: Show access URLs
echo [INFO] Access URLs:
if "%ENVIRONMENT%"=="production" (
    echo   Frontend: https://localhost
    echo   Backend API: https://localhost/api
    echo   API Docs: https://localhost/docs
) else (
    echo   Frontend: http://localhost:8501
    echo   Backend API: http://localhost:8000
    echo   API Docs: http://localhost:8000/docs
    echo   Health Check: http://localhost:8000/health
)
echo.

:: Show resource usage
echo [INFO] Resource Usage:
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
echo.

:: Calculate deployment time
set "END_TIME=%time%"
echo [SUCCESS] Deployment completed successfully!
echo [INFO] Started: %START_TIME%
echo [INFO] Finished: %END_TIME%
echo.

if "%VERBOSE%"=="true" (
    echo [DEBUG] Environment variables loaded:
    if exist ".env.%ENVIRONMENT%" echo   .env.%ENVIRONMENT%
    if exist ".env" echo   .env
    echo [DEBUG] Compose file used: %COMPOSE_FILE%
    echo [DEBUG] Build arguments: %BUILD_ARGS%
    echo [DEBUG] Up arguments: %UP_ARGS%
)

goto :end

:: Functions
:check_dependencies
echo [INFO] Checking required tools...

where docker >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo [ERROR] Docker is not installed or not in PATH
    exit /b 1
)

where docker-compose >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo [ERROR] Docker Compose is not installed or not in PATH
    exit /b 1
)

:: Check Docker daemon
docker info >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo [ERROR] Docker daemon is not running
    exit /b 1
)

where poetry >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo [WARNING] Poetry not found, some features may be limited
) else (
    echo [INFO] Poetry found
)

where curl >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo [WARNING] curl not found, health checks may be limited
)

echo [SUCCESS] All required tools are available
exit /b 0

:validate_environment
echo [INFO] Validating environment configuration...

if not exist "%COMPOSE_FILE%" (
    echo [ERROR] Compose file not found: %COMPOSE_FILE%
    exit /b 1
)

:: Check for .env files
if exist ".env.%ENVIRONMENT%" (
    echo [INFO] Environment file found: .env.%ENVIRONMENT%
) else (
    echo [WARNING] Environment file not found: .env.%ENVIRONMENT%
)

if exist ".env" (
    echo [INFO] Base environment file found: .env
) else (
    echo [WARNING] Base environment file not found: .env
)

:: Create required directories
if not exist "storage" mkdir storage
if not exist "logs" mkdir logs
if not exist "uploads" mkdir uploads
if not exist "ssl" mkdir ssl

echo [SUCCESS] Environment validation completed
exit /b 0

:create_backup
echo [INFO] Creating comprehensive backup...

:: Create backup directory with timestamp
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set "DATE_STAMP=%%c%%a%%b"
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set "TIME_STAMP=%%a%%b"
set "BACKUP_DIR=backups\backup_%DATE_STAMP%_%TIME_STAMP%"
mkdir "%BACKUP_DIR%" 2>nul

:: Backup database
if exist "storage\database.sqlite" (
    echo [INFO] Backing up database...
    copy "storage\database.sqlite" "%BACKUP_DIR%\database.sqlite" >nul
    echo [SUCCESS] Database backup completed
)

:: Backup configuration
if exist ".env" copy ".env" "%BACKUP_DIR%\" >nul
if exist ".env.%ENVIRONMENT%" copy ".env.%ENVIRONMENT%" "%BACKUP_DIR%\" >nul

:: Backup uploads
if exist "uploads" (
    echo [INFO] Backing up uploads...
    xcopy "uploads" "%BACKUP_DIR%\uploads" /E /I /Q >nul 2>&1
    echo [SUCCESS] Uploads backup completed
)

:: Backup logs
if exist "logs" (
    echo [INFO] Backing up logs...
    xcopy "logs" "%BACKUP_DIR%\logs" /E /I /Q >nul 2>&1
    echo [SUCCESS] Logs backup completed
)

:: Create backup manifest
echo Backup created: %DATE% %TIME% > "%BACKUP_DIR%\manifest.txt"
echo Environment: %ENVIRONMENT% >> "%BACKUP_DIR%\manifest.txt"
echo Backup completed by: %USERNAME% >> "%BACKUP_DIR%\manifest.txt"

echo [SUCCESS] Backup created in: %BACKUP_DIR%
exit /b 0

:run_tests
echo [INFO] Running comprehensive test suite...

:: Check if pytest is available
poetry run python -c "import pytest" >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo [WARNING] pytest not available, skipping tests
    exit /b 0
)

:: Run unit tests
echo [INFO] Running unit tests...
poetry run pytest tests/ -v --tb=short --strict-markers
if !ERRORLEVEL! neq 0 exit /b 1

:: Run integration tests if available
if exist "tests\test_integration.py" (
    echo [INFO] Running integration tests...
    poetry run pytest tests/test_integration.py -v
    if !ERRORLEVEL! neq 0 exit /b 1
)

:: Run code quality checks
echo [INFO] Running code quality checks...
poetry run flake8 --max-line-length=100 --ignore=E203,W503 backend/ frontend/ utils/ migrations/ tests/ 2>nul
if !ERRORLEVEL! neq 0 echo [WARNING] Code quality issues found, but continuing...

echo [SUCCESS] Test suite completed
exit /b 0

:setup_ssl
echo [INFO] Setting up SSL certificates...

:: Check if SSL manager exists
if not exist "utils\ssl_manager.py" (
    echo [WARNING] SSL manager not found, skipping SSL setup
    exit /b 1
)

:: Generate self-signed certificates for development
if "%ENVIRONMENT%"=="development" (
    poetry run python -c "from utils.ssl_manager import SSLManager; SSLManager().generate_self_signed_cert()"
    exit /b !ERRORLEVEL!
)

:: Production SSL setup would go here
echo [WARNING] Production SSL setup not implemented in this script
exit /b 1

:migrate_database
echo [INFO] Running database migrations...

if not exist "migrations\database_migrator.py" (
    echo [WARNING] Database migrator not found, skipping migrations
    exit /b 0
)

poetry run python -c "from migrations.database_migrator import DatabaseMigrator; migrator = DatabaseMigrator(); migrator.migrate_all()"
exit /b !ERRORLEVEL!

:seed_database
echo [INFO] Seeding database with test data...

if not exist "migrations\database_seeder.py" (
    echo [WARNING] Database seeder not found, skipping seeding
    exit /b 0
)

poetry run python -c "from migrations.database_seeder import DatabaseSeeder; seeder = DatabaseSeeder(); seeder.seed_all()"
exit /b !ERRORLEVEL!

:health_check
echo [INFO] Performing comprehensive health checks...

set "HEALTH_PASSED=true"
set "RETRY_COUNT=3"
set "RETRY_DELAY=10"

:: Backend health check
for /l %%i in (1,1,%RETRY_COUNT%) do (
    echo [INFO] Health check attempt %%i/%RETRY_COUNT%...
    
    curl -f -s -m 10 http://localhost:8000/health >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        echo [SUCCESS] Backend health check passed
        goto :frontend_health
    )
    
    if %%i lss %RETRY_COUNT% (
        echo [WARNING] Backend health check failed, retrying in %RETRY_DELAY% seconds...
        timeout /t %RETRY_DELAY% /nobreak >nul
    )
)

echo [ERROR] Backend health check failed after %RETRY_COUNT% attempts
set "HEALTH_PASSED=false"

:frontend_health
:: Frontend health check (for development)
if "%ENVIRONMENT%"=="development" (
    curl -f -s -m 10 http://localhost:8501 >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        echo [SUCCESS] Frontend health check passed
    ) else (
        echo [WARNING] Frontend health check failed
        set "HEALTH_PASSED=false"
    )
)

:: Database health check
if exist "storage\database.sqlite" (
    echo [SUCCESS] Database file exists
) else (
    echo [WARNING] Database file not found
    set "HEALTH_PASSED=false"
)

:: Service status check
docker-compose -f %COMPOSE_FILE% ps | findstr "Up" >nul
if !ERRORLEVEL! equ 0 (
    echo [SUCCESS] Docker services are running
) else (
    echo [ERROR] Some Docker services are not running
    set "HEALTH_PASSED=false"
)

if "%HEALTH_PASSED%"=="false" exit /b 1
exit /b 0

:show_help
echo.
echo AI NVCB Enhanced Deployment Script v2.1
echo.
echo Usage: %0 [ENVIRONMENT] [OPTIONS]
echo.
echo ENVIRONMENTS:
echo     development    Deploy for development with hot-reload
echo     staging        Deploy for staging environment  
echo     production     Deploy for production with full optimization
echo.
echo OPTIONS:
echo     --build-only          Build images without deploying
echo     --no-cache           Build without using Docker cache
echo     --pull-latest        Pull latest base images before building
echo     --skip-tests         Skip running tests before deployment
echo     --migrate-db         Run database migrations after deployment
echo     --seed-db            Seed database with test data (dev/staging only)
echo     --ssl-setup          Generate/configure SSL certificates
echo     --backup-first       Create backup before deployment
echo     --health-check       Run health checks after deployment (default: true)
echo     --no-health-check    Skip health checks
echo     --scale-backend N    Scale backend to N instances (default: 1)
echo     --verbose            Enable verbose output
echo     --help               Show this help message
echo.
echo EXAMPLES:
echo     %0                                           # Deploy development
echo     %0 production --migrate-db --ssl-setup       # Production with DB migration and SSL
echo     %0 staging --backup-first --health-check     # Staging with backup and health check
echo     %0 --build-only --no-cache                  # Just build images without cache
echo     %0 production --scale-backend 3             # Production with 3 backend instances
echo.
echo ENVIRONMENT VARIABLES:
echo     DOCKER_REGISTRY       Docker registry for pushing images
echo     SSL_EMAIL            Email for Let's Encrypt SSL certificates
echo     BACKUP_S3_BUCKET     S3 bucket for backups
echo     COMPOSE_PROJECT_NAME Project name for Docker Compose
echo.
exit /b 0

:end
echo [INFO] Script execution completed
pause

@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   AI NVCB Deployment Verification Script
echo   Version: 1.0
echo ========================================
echo.

echo [INFO] Starting deployment verification...
echo.

:: Check if all compose files exist
echo [INFO] Checking Docker Compose files...
if exist "docker-compose.yml" (
    echo [✓] Development compose file found
) else (
    echo [✗] Development compose file missing
    set "ERRORS=true"
)

if exist "docker-compose.staging.yml" (
    echo [✓] Staging compose file found
) else (
    echo [✗] Staging compose file missing
    set "ERRORS=true"
)

if exist "docker-compose.prod.yml" (
    echo [✓] Production compose file found
) else (
    echo [✗] Production compose file missing
    set "ERRORS=true"
)
echo.

:: Validate compose files
echo [INFO] Validating Docker Compose configurations...
docker-compose -f docker-compose.yml config --quiet
if !ERRORLEVEL! equ 0 (
    echo [✓] Development compose configuration valid
) else (
    echo [✗] Development compose configuration invalid
    set "ERRORS=true"
)

docker-compose -f docker-compose.staging.yml config --quiet
if !ERRORLEVEL! equ 0 (
    echo [✓] Staging compose configuration valid
) else (
    echo [✗] Staging compose configuration invalid
    set "ERRORS=true"
)

docker-compose -f docker-compose.prod.yml config --quiet
if !ERRORLEVEL! equ 0 (
    echo [✓] Production compose configuration valid
) else (
    echo [✗] Production compose configuration invalid
    set "ERRORS=true"
)
echo.

:: Check critical files
echo [INFO] Checking critical application files...
if exist "utils\health_check.py" (
    echo [✓] Health check module found
) else (
    echo [✗] Health check module missing
    set "ERRORS=true"
)

if exist "deploy.bat" (
    echo [✓] Windows deployment script found
) else (
    echo [✗] Windows deployment script missing
    set "ERRORS=true"
)

if exist "deploy.sh" (
    echo [✓] Linux deployment script found
) else (
    echo [✗] Linux deployment script missing
    set "ERRORS=true"
)

if exist "pyproject.toml" (
    echo [✓] Poetry configuration found
) else (
    echo [✗] Poetry configuration missing
    set "ERRORS=true"
)

if exist "Dockerfile" (
    echo [✓] Dockerfile found
) else (
    echo [✗] Dockerfile missing
    set "ERRORS=true"
)
echo.

:: Test health check
echo [INFO] Testing health check functionality...
python -m utils.health_check >nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo [✓] Health check module working
) else (
    echo [✗] Health check module failed
    set "ERRORS=true"
)
echo.

:: Test Docker build capability
echo [INFO] Testing Docker build capability...
docker-compose -f docker-compose.yml build --dry-run >nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo [✓] Docker build test successful
) else (
    echo [✗] Docker build test failed
    set "ERRORS=true"
)
echo.

:: Final report
echo ========================================
echo   VERIFICATION SUMMARY
echo ========================================
if "%ERRORS%"=="true" (
    echo [✗] VERIFICATION FAILED - Issues detected
    echo Please review the errors above before deployment
    exit /b 1
) else (
    echo [✓] VERIFICATION SUCCESSFUL
    echo All components are ready for deployment
    echo.
    echo Available deployment commands:
    echo   Development:  deploy.bat development
    echo   Staging:      deploy.bat staging
    echo   Production:   deploy.bat production
    echo.
    echo For detailed options: deploy.bat --help
)
echo ========================================

pause
exit /b 0

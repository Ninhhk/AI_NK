@echo off
:: Script to update, install dependencies, and run the AI NVCB application
echo AI NVCB - Update and Run Script

:: Store process IDs
set BACKEND_PID=
set FRONTEND_PID=

:: Function to clean up processes on exit
:cleanup
    echo.
    echo ==== Shutting down servers ====
    
    if defined BACKEND_PID (
        echo Terminating backend server
        taskkill /PID %BACKEND_PID% /F > nul 2>&1
    )
    
    if defined FRONTEND_PID (
        echo Terminating frontend server
        taskkill /PID %FRONTEND_PID% /F > nul 2>&1
    )
    
    echo All processes terminated.
    exit /b 0

:: Function to run a command and handle errors
:run_command
    echo [Running] %~1
    %~1
    if %ERRORLEVEL% neq 0 (
        echo [Error] Command failed: %~1
        exit /b 1
    ) else (
        echo [Success] %~1
        exit /b 0
    )

:: Step 1: Update git repository if it exists
echo.
echo ==== Checking repository ====
if exist .git (
    echo Updating repository with git pull...
    git pull
    if %ERRORLEVEL% neq 0 (
        echo [Warning] Repository update failed, continuing with local version.
    )
) else (
    echo [Warning] Not a git repository, skipping update.
)

:: Step 2: Update dependencies
echo.
echo ==== Updating dependencies ====
if not exist pyproject.toml (
    echo [Error] pyproject.toml not found. Cannot update dependencies.
    goto :exit
)

echo Updating Poetry lock file...
poetry lock
if %ERRORLEVEL% neq 0 (
    echo [Error] Failed to update Poetry lock file.
    goto :exit
)

echo Installing dependencies...
poetry install
if %ERRORLEVEL% neq 0 (
    echo [Error] Failed to install dependencies.
    goto :exit
)

:: Step 3: Start the backend server
echo.
echo ==== Starting backend server ====
start /B "" python run_backend.py
for /f "tokens=2" %%a in ('tasklist /NH /FI "IMAGENAME eq python.exe" ^| find "python"') do set BACKEND_PID=%%a
echo Backend server started

:: Wait for backend to initialize
echo Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

:: Step 4: Start the frontend server
echo.
echo ==== Starting frontend server ====
start /B "" streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0
for /f "tokens=2" %%a in ('tasklist /NH /FI "IMAGENAME eq streamlit.exe" ^| find "streamlit"') do set FRONTEND_PID=%%a
echo Frontend server started

echo.
echo ==== Application started successfully ====
echo Backend server running at: http://localhost:8000
echo Frontend available at: http://localhost:8501
echo Press Ctrl+C to stop all servers, or close this window.

echo.
echo The application is now running. This window must remain open.
echo Press any key to stop all servers and exit.
pause > nul

:exit
call :cleanup
exit /b 
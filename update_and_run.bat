@echo off
:: Script to update, install dependencies, and run the AI NVCB application
echo AI NVCB - Update and Run Script

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

:: Step 3: Start the backend server in a new terminal window
echo.
echo ==== Starting backend server in new terminal ====
start "Backend Server" cmd /k "python run_backend.py"
echo Backend server started in new terminal window.

:: Wait for backend to initialize
echo Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

:: Step 4: Start the frontend server in a new terminal window
echo.
echo ==== Starting frontend server in new terminal ====
start "Frontend Server" cmd /k "streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0"
echo Frontend server started in new terminal window.

echo.
echo ==== Application started successfully ====
echo Backend API server running at: http://localhost:8000
echo Available API endpoints:
echo  - http://localhost:8000/api/documents/analyze (POST)
echo  - http://localhost:8000/api/documents/chat-history/{document_id} (GET)
echo  - http://localhost:8000/api/documents/generate-quiz (POST)
echo  - http://localhost:8000/api/documents/health (GET)
echo.
echo Frontend UI available at: http://localhost:8501
echo.
echo NOTE: The backend doesn't serve a web page at the root URL (http://localhost:8000/).
echo       You should see "404 Not Found" if you access that URL directly - this is normal.
echo       The backend health check at http://localhost:8000/api/documents/health should return {"status": "healthy"}.
echo.
echo The application is now running in separate terminal windows.
echo You can close each window individually to stop the services.
echo.
echo Press any key to exit this launcher...
pause > nul

:exit
exit /b 
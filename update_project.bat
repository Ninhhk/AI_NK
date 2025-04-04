@echo off
echo ======================================
echo  AI NVCB Project Update Helper
echo ======================================
echo.

REM Check which Python command is available (python or python3)
set PYTHON_CMD=python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    where python3 >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo Python is not found in PATH! Please install Python or add it to your PATH.
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
)

REM Check if Git is available
where git >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Git is not found in PATH! Please install Git or add it to your PATH.
    exit /b 1
)

REM Check if Poetry is available
where poetry >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Poetry is not found in PATH! Please install Poetry or add it to your PATH.
    exit /b 1
)

echo All required tools are available.
echo Using Python command: %PYTHON_CMD%
echo.
echo Running update and dependency check script...
echo.

REM Run the Python script
%PYTHON_CMD% update_and_test.py %*

if %ERRORLEVEL% neq 0 (
    echo.
    echo There were errors during the update process.
    echo Please check the output above for details.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Update completed successfully!
echo.
pause 
@echo off
setlocal enabledelayedexpansion

:: Measure Docker image size and build time (Windows)
set RESULT_DIR=%~dp0results
if not exist "%RESULT_DIR%" mkdir "%RESULT_DIR%"
set LOG_FILE=%RESULT_DIR%\image_size_eval.log
set CSV_FILE=%RESULT_DIR%\image_size_eval.csv

:: Timestamp
for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command "(Get-Date).ToUniversalTime().ToString('s')"`) do set TS=%%i

:: Record git state if available
for /f "usebackq tokens=*" %%i in (`git rev-parse --short HEAD 2^>NUL`) do set GIT_SHA=%%i

:: Start timer
for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command "[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()"`) do set START_MS=%%i

echo [%TS%] Building Docker image... > "%LOG_FILE%"
docker build -t ai_nvcb:bench ..
if errorlevel 1 (
    echo Build failed >> "%LOG_FILE%"
    exit /b 1
)

for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command "[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()"`) do set END_MS=%%i
set /a DURATION_MS=%END_MS%-%START_MS%

echo Build duration (ms): %DURATION_MS% >> "%LOG_FILE%"

echo Image sizes: >> "%LOG_FILE%"
docker images ai_nvcb:bench --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" >> "%LOG_FILE%"

:: CSV output
if not exist "%CSV_FILE%" (
    echo timestamp_ms,git_sha,duration_ms,image_tag,image_size > "%CSV_FILE%"
)
for /f "skip=1" %%a in ('docker images ai_nvcb:bench --format "{{.Size}}"') do (
    echo %END_MS%,%GIT_SHA%,%DURATION_MS%,ai_nvcb:bench,%%a >> "%CSV_FILE%"
    goto :after
)
:after
echo Wrote logs to %LOG_FILE%
endlocal

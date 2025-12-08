@echo off
echo ============================================================
echo Testing My Devs AI Agent Team Setup
echo ============================================================
echo.

REM Activate venv
call venv\Scripts\activate

echo [1/5] Cleaning up old database (if exists)...
if exist "data\database\pm_system.db" (
    del /F "data\database\pm_system.db"
    echo      Deleted old database
)
echo      Done!
echo.

echo [2/5] Initializing database...
python scripts\init_db.py
if %errorlevel% neq 0 (
    echo      ERROR: Database initialization failed!
    pause
    exit /b 1
)
echo      Done!
echo.

echo [3/5] Seeding example data...
python scripts\seed_data.py
if %errorlevel% neq 0 (
    echo      ERROR: Seeding failed!
    pause
    exit /b 1
)
echo      Done!
echo.

echo [4/5] Testing CLI commands...
echo.
echo ---- Listing projects ----
python -m src.cli.main projects
echo.

echo ---- Getting status (This will call OpenAI API!) ----
python -m src.cli.main status "Example Project"
echo.

echo ---- Listing tasks ----
python -m src.cli.main tasks "Example Project"
echo.

echo [5/5] Checking costs...
python -m src.cli.main costs today
echo.

echo ============================================================
echo Setup test COMPLETE!
echo ============================================================
echo.
echo If you see this message, everything works!
echo.
echo Next steps:
echo   1. Check cost logs: type data\logs\costs\*.json
echo   2. Create your own task: python -m src.cli.main create "Example Project" "Your task"
echo   3. Explore the CLI: python -m src.cli.main --help
echo.
pause

@echo off
REM Quick start script for Milestone 1

echo ============================================================
echo My Devs AI Agent Team - Quick Start
echo ============================================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo [1/5] Creating virtual environment...
    python -m venv venv
    echo      Done!
    echo.
) else (
    echo [1/5] Virtual environment already exists
    echo.
)

REM Activate venv
echo [2/5] Activating virtual environment...
call venv\Scripts\activate
echo      Done!
echo.

REM Install dependencies
echo [3/5] Installing dependencies...
pip install -q -r requirements.txt
echo      Done!
echo.

REM Check if .env exists
if not exist ".env" (
    echo [4/5] Creating .env file...
    copy .env.example .env
    echo      Please edit .env and add your OPENAI_API_KEY!
    echo.
    pause
) else (
    echo [4/5] .env file already exists
    echo.
)

REM Check if database exists
if not exist "data\database\pm_system.db" (
    echo [5/5] Initializing database and seeding data...
    python scripts\init_db.py
    python scripts\seed_data.py
    echo      Done!
) else (
    echo [5/5] Database already initialized
)

echo.
echo ============================================================
echo Setup complete! Try these commands:
echo ============================================================
echo.
echo   python -m src.cli.main status "Example Project"
echo   python -m src.cli.main tasks "Example Project"
echo   python -m src.cli.main costs today
echo.
pause

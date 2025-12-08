# Quick Command Reference

## PowerShell Commands (Windows)

### View Cost Logs
```powershell
# List cost log files
Get-ChildItem data\logs\costs\

# View today's cost log
Get-Content data\logs\costs\2025-12-07.json | ConvertFrom-Json | ConvertTo-Json -Depth 10

# Or simply:
type data\logs\costs\2025-12-07.json

# View all cost files
Get-ChildItem data\logs\costs\*.json | ForEach-Object { type $_.FullName }
```

### View Agent Context
```powershell
# PM Agent context for Example Project
type data\agent_context\pm_agent\example_project\2025-12-07.json
```

### View Database
```powershell
# Install sqlite if needed: choco install sqlite
sqlite3 data\database\pm_system.db

# Then in sqlite:
.tables
SELECT * FROM projects;
SELECT * FROM tasks;
.exit
```

## CLI Commands

### Basic Usage
```bash
# Activate venv first
venv\Scripts\activate

# Get help
python -m src.cli.main --help

# Get command-specific help
python -m src.cli.main status --help
python -m src.cli.main create --help
```

### Project Management
```bash
# List all projects
python -m src.cli.main projects

# Get project status (calls OpenAI API - costs ~$0.00015)
python -m src.cli.main status "Example Project"

# Show warnings
python -m src.cli.main warnings "Example Project"
```

### Task Management
```bash
# List all tasks
python -m src.cli.main tasks "Example Project"

# List only TODO tasks
python -m src.cli.main tasks "Example Project" --status todo

# List only blocked tasks
python -m src.cli.main tasks "Example Project" --status blocked

# Create a new task
python -m src.cli.main create "Example Project" "My new task"

# Create with priority
python -m src.cli.main create "Example Project" "Urgent task" --priority critical

# Create with description
python -m src.cli.main create "Example Project" "Task title" -d "Task description" -p high
```

### Cost Tracking
```bash
# View today's costs
python -m src.cli.main costs today

# View monthly summary
python -m src.cli.main costs month
```

### Lead Dev (Technical Guidance)
```bash
# Ask Lead Dev for technical advice (calls OpenAI API)
python -m src.cli.main ask-dev "Example Project" "How should I handle API rate limiting?"

# Get architecture review for a new requirement (calls OpenAI API)
python -m src.cli.main review-arch "Example Project" "Add real-time data streaming"

# Track a technical decision (no API call - just logs to context)
python -m src.cli.main track-decision "Example Project" "Use SQLite instead of PostgreSQL" "Budget-friendly, local-first architecture"

# View Lead Dev's technical context for a project
python -m src.cli.main dev-context "Example Project"

# View specific time period
python -m src.cli.main dev-context "Example Project" --days 7
```

### Other
```bash
# Show version
python -m src.cli.main version
```

## Common Workflows

### Morning Standup
```bash
# Check all projects
python -m src.cli.main projects

# Get status for each active project
python -m src.cli.main status "Example Project"

# Check warnings
python -m src.cli.main warnings "Example Project"

# Review costs
python -m src.cli.main costs today
```

### Creating Tasks from Ideas
```bash
# Quick task
python -m src.cli.main create "Example Project" "Research Binance API endpoints"

# Detailed task
python -m src.cli.main create "Example Project" "Implement rate limiting" -d "Add exponential backoff for API calls" -p high
```

### Weekly Review
```bash
# Get status for all projects
python -m src.cli.main projects

# Monthly cost analysis
python -m src.cli.main costs month

# Export costs to CSV (in Python)
python
>>> from src.core.cost_tracker import CostTracker
>>> ct = CostTracker()
>>> csv_path = ct.export_to_csv(days=30)
>>> print(f"Exported to: {csv_path}")
>>> exit()
```

### Working with Lead Dev (Technical Sessions)
```bash
# 1. Ask for technical advice on a problem
python -m src.cli.main ask-dev "Example Project" "Best way to implement caching for API responses?"

# 2. Track the decision you made based on that advice
python -m src.cli.main track-decision "Example Project" "Use Redis for API caching" "Low latency, easy integration, popular"

# 3. Later, review architecture for a new feature
python -m src.cli.main review-arch "Example Project" "Add user authentication with JWT"

# 4. Check what Lead Dev remembers about the project
python -m src.cli.main dev-context "Example Project" --days 14
```

## Troubleshooting

### "Module not found" errors
```bash
# Make sure venv is activated
venv\Scripts\activate

# Verify you're in project root
cd "C:\Users\Christian Orquera\My_Devs_AI_Agent_team"

# Check Python is from venv
where python
# Should show: C:\Users\...\venv\Scripts\python.exe
```

### "Project not found" errors
```bash
# List projects to see exact names
python -m src.cli.main projects

# Names are case-sensitive!
python -m src.cli.main status "Example Project"  # ✓ Correct
python -m src.cli.main status "example project"  # ✗ Wrong
```

### OpenAI API errors
```bash
# Check .env file exists
type .env

# Verify API key is set
# Should show: OPENAI_API_KEY=sk-...

# Test OpenAI connection (in Python)
python
>>> import os
>>> from dotenv import load_dotenv
>>> load_dotenv()
>>> print("API Key:", os.getenv("OPENAI_API_KEY")[:10] + "...")
>>> exit()
```

## Useful PowerShell Aliases

Add to your PowerShell profile (`$PROFILE`):

```powershell
# Activate venv
function va { & "C:\Users\Christian Orquera\My_Devs_AI_Agent_team\venv\Scripts\Activate.ps1" }

# Quick PM commands
function pm-status { python -m src.cli.main status "Example Project" }
function pm-tasks { python -m src.cli.main tasks "Example Project" }
function pm-costs { python -m src.cli.main costs today }

# Quick navigation
function goto-pm { cd "C:\Users\Christian Orquera\My_Devs_AI_Agent_team" }
```

Then use:
```powershell
goto-pm
va
pm-status
```

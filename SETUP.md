# Setup Guide - Milestone 1

## Prerequisites
- Python 3.13+ installed
- OpenAI API key

## Step-by-Step Setup

### 1. Navigate to Project Directory
```bash
cd "C:\Users\Christian Orquera\My_Devs_AI_Agent_team"
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate
```

You should see `(venv)` in your command prompt.

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- CrewAI (multi-agent framework)
- OpenAI SDK
- SQLAlchemy (database)
- Rich (CLI formatting)
- All other dependencies

### 5. Configure API Keys

Create `.env` file from template:
```bash
copy .env.example .env
```

Edit `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-key-here
```

**Important:** Never commit your `.env` file to git!

### 6. Initialize Database
```bash
python scripts/init_db.py
```

This creates:
- Database schema (5 tables)
- Data directories
- Log directories

### 7. Seed Example Data
```bash
python scripts/seed_data.py
```

This creates:
- "Example Project"
- PM Agent and Lead Dev Agent
- 6 sample tasks

### 8. Test the System

#### View project status:
```bash
python -m src.cli.main status "Example Project"
```

This will:
- Call PM Agent
- Query OpenAI API
- Generate status report
- Log costs transparently

#### List all tasks:
```bash
python -m src.cli.main tasks "Example Project"
```

#### Create a new task:
```bash
python -m src.cli.main create "Example Project" "Test the PM Agent"
```

#### View today's costs:
```bash
python -m src.cli.main costs today
```

This shows:
- Number of API calls
- Total tokens used
- Cost breakdown by agent/project
- Budget status

#### View all projects:
```bash
python -m src.cli.main projects
```

#### Check warnings:
```bash
python -m src.cli.main warnings "Example Project"
```

### 9. Verify Everything Works

Run this complete test sequence:

```bash
# 1. Check version
python -m src.cli.main version

# 2. List projects
python -m src.cli.main projects

# 3. Get status (this calls OpenAI - costs ~$0.0001)
python -m src.cli.main status "Example Project"

# 4. List tasks
python -m src.cli.main tasks "Example Project"

# 5. Create a new task
python -m src.cli.main create "Example Project" "Verify Milestone 1 complete" -p high

# 6. Check costs
python -m src.cli.main costs today

# 7. Check warnings
python -m src.cli.main warnings "Example Project"
```

Expected result: All commands work without errors!

## Troubleshooting

### Error: "OPENAI_API_KEY not set"
- Make sure you created `.env` file
- Check that your API key is correct
- Verify `.env` is in the project root directory

### Error: "No module named 'src'"
- Make sure you run commands from project root
- Activate virtual environment first

### Error: "Project not found"
- Run `python scripts/seed_data.py` first
- Check project name is exactly "Example Project" (case-sensitive)

### Database errors
- Delete `data/database/pm_system.db`
- Run `python scripts/init_db.py` again
- Run `python scripts/seed_data.py` again

## What's Next?

### Milestone 1 Complete! ✅

You now have:
- ✅ Full database with 5 tables
- ✅ PM Agent with OpenAI integration
- ✅ Cost tracking (transparent logging)
- ✅ Context preservation (JSON logs)
- ✅ CLI interface
- ✅ Example project with tasks

### Explore Cost Tracking

Check detailed cost logs:
```bash
# View today's costs
python -m src.cli.main costs today

# View monthly summary
python -m src.cli.main costs month

# Check raw JSON logs
type data\logs\costs\2025-12-07.json

# Export to CSV for analysis
python -c "from src.core.cost_tracker import CostTracker; ct = CostTracker(); print(ct.export_to_csv())"
```

### Create Your Real Project

```bash
# Using Python
python
>>> from src.core.database import get_session, Project
>>> session = get_session()
>>> binance = Project(name="Binance Trading", description="Crypto trading project", status="active", priority=8)
>>> session.add(binance)
>>> session.commit()
>>> exit()

# Then use it
python -m src.cli.main create "Binance Trading" "Research Binance API endpoints"
python -m src.cli.main status "Binance Trading"
```

### Milestone 2: Telegram Bot

Once you're happy with Milestone 1, we'll add:
- Telegram bot interface
- Mobile access
- Real-time notifications

## Cost Expectations

Based on testing:
- **Status check**: ~450 input tokens + 150 output tokens = $0.00015
- **Daily usage (20 commands)**: ~$0.10
- **Monthly (typical)**: $1-3

All costs are logged in `data/logs/costs/` with full transparency!

## Need Help?

Contact Lead Dev (Claude) through this interface or check the architecture plan in `.claude/plans/`.

# Dev Agent Setup Guide

## Overview

This guide shows you how to set up and use the **StreamUI-based Dev Agent** for automatic code execution.

### Architecture

```
Albedo (PM Agent) ──HTTP──> Dev Agent Service ──Tools──> Code Files + GitHub
     ↑                           ↑                              ↓
  Telegram                  StreamUI/Claude              Task Database
```

- **Albedo**: Python-based PM agent (Telegram bot)
- **Dev Agent**: Node.js-based code writer (StreamUI + Claude/GPT)
- **Communication**: HTTP REST API between services

## Quick Start

### 1. Install Dependencies

**Dev Agent Service (Node.js):**
```bash
cd dev-agent-service
npm install
```

**Python dependencies** (if not installed):
```bash
pip install requests
```

### 2. Configure Environment

Create `dev-agent-service/.env`:

```bash
# Copy example
cd dev-agent-service
cp .env.example .env
```

Edit `.env`:

```bash
# AI Provider (use Claude for best code generation)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Or use OpenAI
OPENAI_API_KEY=sk-your-key-here

# Database (Python backend)
DATABASE_PATH=../data/database/pm_system.db

# Workspace for generated code
WORKSPACE_DIR=../workspace

# GitHub (optional, for auto-commit)
GITHUB_TOKEN=ghp_your-token
GITHUB_USER=your-username

# Server port
PORT=3001
```

### 3. Create Workspace Directory

```bash
# From project root
mkdir workspace
cd workspace
git init
```

### 4. Start Both Services

**Terminal 1 - Python Backend (Telegram bot):**
```bash
# From project root
python src/telegram/bot.py
```

**Terminal 2 - Dev Agent Service:**
```bash
cd dev-agent-service
npm run dev
```

You should see:
```
🚀 Dev Agent Service running on http://localhost:3001
   Health check: http://localhost:3001/health
   Execute task: POST http://localhost:3001/execute-task

   Waiting for task execution requests from Albedo...
```

## Usage

### Via Telegram

1. **List tasks:**
   ```
   /tasks "Reporting Analytics Dashboards"
   ```

2. **Execute a task with Dev Agent:**
   ```
   /execute 9
   ```

   Or via conversation:
   ```
   "Albedo, have the dev agent work on task 9"
   ```

3. **Watch progress** in Dev Agent terminal - you'll see:
   ```
   🤖 Dev Agent executing Task #9: Base Prototype Deployment
      Project: Reporting Analytics Dashboards

     → write_file: { path: "index.html", ... }
     ✓ Created index.html (45 lines written)

     → write_file: { path: "styles.css", ... }
     ✓ Created styles.css (120 lines written)

     → git_commit: { message: "feat: Add reporting dashboard" }
     ✓ Committed: "feat: Add reporting dashboard"

     → update_task: { task_id: 9, status: "review" }
     ✓ Task #9 → review

   ✓ Task #9 completed by Dev Agent
   ```

4. **Check results:**
   ```bash
   ls workspace/
   # index.html  styles.css  app.js

   cd workspace && git log
   # commit abc123... feat: Add reporting dashboard prototype
   ```

### Via Direct API Call

```bash
curl -X POST http://localhost:3001/execute-task \
  -H "Content-Type: application/json" \
  -d '{"task_id": 9}'
```

## What Tasks Can Dev Agent Execute?

Dev Agent can build:

- ✅ **Web frontends** (HTML/CSS/JavaScript)
- ✅ **Python backends** (Flask/FastAPI)
- ✅ **React/Vue apps** (with proper task description)
- ✅ **API integrations**
- ✅ **Data dashboards**

### Example Task Descriptions That Work Well

**Good task descriptions:**
```
Title: Build Reporting Dashboard Prototype
Description: Create HTML/CSS/JS dashboard with:
- Bootstrap 5 for styling
- Chart.js for analytics graphs
- 3 cards showing KPIs (Revenue, Users, Growth)
- Responsive design for mobile
- Modern glassmorphism UI
```

**What Dev Agent Will Do:**
1. Create `index.html` with structure
2. Create `styles.css` with custom styling
3. Create `app.js` with Chart.js integration
4. Include CDN links for Bootstrap and Chart.js
5. Add sample data for demonstration
6. Commit all files to git
7. Update task status to 'review'

## Troubleshooting

### "Cannot connect to Dev Agent Service"

**Problem:** Python can't reach Node.js service

**Solution:**
```bash
# Check if service is running
curl http://localhost:3001/health

# If not, start it:
cd dev-agent-service
npm run dev
```

### "Task execution timeout"

**Problem:** Task took longer than 5 minutes

**Solution:**
- Task is probably complex, check Dev Agent terminal for progress
- Increase timeout in `src/telegram/handlers.py` line 434:
  ```python
  timeout=600  # 10 minutes
  ```

### "Database not found"

**Problem:** `DATABASE_PATH` is incorrect

**Solution:**
```bash
# Check path exists
ls data/database/pm_system.db

# Update .env if needed
DATABASE_PATH=../data/database/pm_system.db
```

### "Write file failed"

**Problem:** Workspace directory doesn't exist

**Solution:**
```bash
mkdir -p workspace
```

### Dev Agent generates poor code

**Problem:** Task description is vague

**Solution:** Provide detailed task descriptions with:
- Technologies to use (Bootstrap, React, Flask, etc.)
- Specific features needed
- Design requirements
- File structure hints

## Advanced: Integrating with Albedo's Conversation

Currently, you use `/execute 9` command. To make Albedo understand natural language assignment:

**Add to Albedo's function schemas** (`src/agents/tools/function_schemas.py`):

```python
{
    "type": "function",
    "function": {
        "name": "execute_task_with_dev_agent",
        "description": "Assign a task to the Dev Agent for code execution",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "number",
                    "description": "Task ID to execute"
                }
            },
            "required": ["task_id"]
        }
    }
}
```

Then Albedo can respond to:
- "Have the dev agent work on task 9"
- "Execute task 9 with dev agent"
- "Assign task 9 to dev agent"

## Performance Benchmarks

Based on StreamUI benchmarks compared to LangGraph:

| Metric | Value |
|--------|-------|
| Average latency | 2.39s (76% faster than LangGraph) |
| Token usage | 1,591 (66% less than Agno 2.0) |
| Cost per execution | ~$0.02-0.05 (depending on code complexity) |

## Next Steps

1. **Test with Task #9:**
   ```
   /execute 9
   ```

2. **Review generated code** in `workspace/` directory

3. **Push to GitHub:**
   ```bash
   cd workspace
   git remote add origin https://github.com/Weche/reporting-analytics.git
   git push -u origin main
   ```

4. **Create more tasks** for Dev Agent to execute!

## Support

If you encounter issues:

1. Check both terminal outputs (Python bot + Dev Agent service)
2. Verify `.env` configuration
3. Ensure workspace directory exists
4. Check task status with `/tasks` command

Happy coding with your Dev Agent! 🤖

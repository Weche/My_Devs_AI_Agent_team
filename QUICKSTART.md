# Quick Start Guide

## First-Time Setup (Do Once)

### Step 1: Create .env files for each agent

You need to create `.env` files from the `.env.example` templates and add your OpenAI API key.

**Option A - Manual (Recommended):**

```bash
# Frontend Agent
cd dev-agents/frontend-agent
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY=sk-...

# Backend Agent
cd ../backend-agent
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY=sk-...

# Database Agent
cd ../database-agent
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY=sk-...
```

**Option B - PowerShell Script:**

```powershell
# Copy all .env.example files
Copy-Item dev-agents\frontend-agent\.env.example dev-agents\frontend-agent\.env
Copy-Item dev-agents\backend-agent\.env.example dev-agents\backend-agent\.env
Copy-Item dev-agents\database-agent\.env.example dev-agents\database-agent\.env

# Then edit each .env file to add your API key
```

### Step 2: Add your OpenAI API Key

Edit each `.env` file and replace `your_openai_api_key_here` with your actual key:

```env
OPENAI_API_KEY=sk-proj-your_actual_key_here
```

**IMPORTANT:** Each agent `.env` already has the correct PORT set:
- frontend-agent/.env → `PORT=3001`
- backend-agent/.env → `PORT=3002`
- database-agent/.env → `PORT=3003`

Don't change these!

---

## Running the System (Every Time)

### Terminal 1 - Dev Agents

```bash
cd C:\Users\Christian Orquera\My_Devs_AI_Agent_team\dev-agents
npm start
```

Wait until you see:
```
✅ All agents started!
🚀 Dev Agent Service running on http://localhost:3001
🚀 Dev Agent Service running on http://localhost:3002
🚀 Dev Agent Service running on http://localhost:3003
```

### Terminal 2 - Albedo (Telegram Bot)

```bash
cd C:\Users\Christian Orquera\My_Devs_AI_Agent_team
python src/telegram/bot.py
```

Wait until you see:
```
Bot started! Send /start to begin.
Proactive updates scheduler started
```

---

## Testing

Open Telegram and message your bot:

```
/start
```

Then try:

```
Check all agent status
```

You should see:
```
🟢 Frontend Agent (Port 3001) - Online
🟢 Backend Agent (Port 3002) - Online
🟢 Database Agent (Port 3003) - Online
```

If all green, you're ready! 🚀

---

## Troubleshooting

### Problem: "Cannot find package 'cors'"
**Solution:** Run setup script:
```bash
cd dev-agents
setup-agents.bat  # Installs all dependencies
```

### Problem: "EADDRINUSE: address already in use"
**Solution:** Check that each .env file has the correct PORT:
- frontend-agent/.env → PORT=3001
- backend-agent/.env → PORT=3002
- database-agent/.env → PORT=3003

### Problem: "Dev Agent initialized but no port message"
**Solution:** Check that `.env` files exist (not just `.env.example`) and contain your OPENAI_API_KEY

### Problem: Agents start but crash immediately
**Solution:** Verify OPENAI_API_KEY is valid and not expired

---

## What's Next?

See [RUNNING_AGENTS.md](RUNNING_AGENTS.md) for:
- Full testing guide
- Creating new specialized agents
- Advanced features

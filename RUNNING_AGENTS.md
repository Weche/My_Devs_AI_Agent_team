# Running the Dev Agent Team

You now have **3 specialized Dev Agents** working for Albedo, and **3 ways to run them**!

## Option 1: Single Terminal (Recommended)

Run all 3 agents from one terminal using the orchestrator:

```bash
cd dev-agents
npm install  # First time only
npm start
```

**Output:** Color-coded logs from all 3 agents in one terminal
- 🔵 **Cyan** = Frontend Agent (Port 3001)
- 🟡 **Yellow** = Backend Agent (Port 3002)
- 🟣 **Magenta** = Database Agent (Port 3003)

**Shutdown:** Press `Ctrl+C` to stop all agents gracefully

---

## Option 2: Separate Windows (Windows Only)

Run each agent in its own window using the batch script:

```bash
start-agents.bat
```

**Result:** 3 separate cmd windows, one for each agent

---

## Option 3: Manual (3 Terminals)

Run each agent individually:

**Terminal 1 - Frontend Agent:**
```bash
cd dev-agents/frontend-agent
npm run dev
```

**Terminal 2 - Backend Agent:**
```bash
cd dev-agents/backend-agent
npm run dev
```

**Terminal 3 - Database Agent:**
```bash
cd dev-agents/database-agent
npm run dev
```

---

## Full System Startup

### 2-Terminal Setup (Recommended)

**Terminal 1:** Run all 3 Dev Agents
```bash
cd dev-agents
npm start
```

**Terminal 2:** Run Albedo's Telegram bot
```bash
cd C:\Users\Christian Orquera\My_Devs_AI_Agent_team
python src/telegram/bot.py
```

---

## Dynamic Agent Creation

Albedo can now **create new specialized agents** with your approval!

### How It Works:

1. **Albedo Notices Patterns:** If you create 5+ tasks of the same type (testing, devops, security, mobile), Albedo will suggest creating a specialized agent

2. **Approval Request:** Albedo will ask:
   ```
   Master Christian, I'd like to create a new specialized agent:

   **Agent Details:**
   - Name: Testing Agent
   - Specialty: testing
   - Port: 3004
   - Keywords: test, pytest, unittest, jest, qa
   - Description: Automated testing expert

   Please confirm if I should create this agent by saying:
   "Yes, create the Testing Agent"
   ```

3. **You Approve:** Just say "Yes, create the Testing Agent"

4. **Albedo Creates It:** She'll auto-generate:
   - Agent directory structure (`dev-agents/testing-agent/`)
   - Configuration files (`.env.example`, `package.json`)
   - Specialized prompts for the agent
   - Auto-registration in agent config

5. **Start the New Agent:**
   ```bash
   cd dev-agents/testing-agent
   cp .env.example .env
   # Add your OPENAI_API_KEY to .env
   npm install
   npm run dev
   ```

### Suggested Agents:

| Agent Type | Port | Keywords | Specialty |
|------------|------|----------|-----------|
| Testing Agent | 3004 | test, pytest, unittest, jest, qa, e2e | Automated testing expert |
| DevOps Agent | 3005 | docker, kubernetes, ci/cd, deploy, terraform | Infrastructure & deployment |
| Security Agent | 3006 | security, auth, encryption, vulnerability, owasp | Security & authentication |
| Mobile Agent | 3007 | mobile, react-native, flutter, ios, android, app | Mobile app development |

---

## Agent Status

Check which agents are online:

**Via Telegram:**
```
/status
```

**Or ask Albedo:**
```
"Check agent status"
```

**Example Response:**
```
🟢 Frontend Agent (Port 3001) - Online
🟢 Backend Agent (Port 3002) - Online
🟢 Database Agent (Port 3003) - Online
🔴 Testing Agent (Port 3004) - Offline
```

---

## Troubleshooting

**Problem:** Agents won't start
**Solution:** Make sure ports 3001-3003 aren't already in use
```bash
netstat -ano | findstr :3001
netstat -ano | findstr :3002
netstat -ano | findstr :3003
```

**Problem:** Database errors
**Solution:** Verify database paths in `.env` files point to `../../data/database/pm_system.db`

**Problem:** Orchestrator won't start
**Solution:** Run `npm install` in `dev-agents/` directory first

---

## What's Next?

1. **Start the agents** using Option 1 (orchestrator)
2. **Test Albedo** via Telegram: `python src/telegram/bot.py`
3. **Create some tasks** and watch Albedo auto-assign to specialists
4. **Try creating a new agent** by giving Albedo 5+ testing tasks

Enjoy your AI dev team! 🚀

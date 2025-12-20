# Configuration Approach - Centralized vs Per-Agent

## ✅ Recommended: Centralized Configuration (What We Implemented)

### **Single Root `.env` File**

All agents now share the **root `.env`** file at:
```
C:\Users\Christian Orquera\My_Devs_AI_Agent_team\.env
```

**Benefits:**
- ✅ Single source of truth for API keys
- ✅ No duplication of sensitive credentials
- ✅ Easier to update (change key in one place)
- ✅ More secure (fewer files with secrets)
- ✅ Follows DRY principle (Don't Repeat Yourself)

### **How It Works**

1. **Shared Environment Loader** ([dev-agents/shared-env.js](dev-agents/shared-env.js))
   - Loads environment variables from root `.env`
   - Validates required keys (OPENAI_API_KEY)
   - Exports variables for all agents to use

2. **Each Agent Imports Shared Env**
   ```typescript
   // frontend-agent/src/index.ts
   import sharedEnv from '../../shared-env.js';
   const PORT = 3001; // Hardcoded per agent
   ```

3. **Port Assignment**
   - Frontend Agent: `PORT = 3001` (hardcoded in index.ts)
   - Backend Agent: `PORT = 3002` (hardcoded in index.ts)
   - Database Agent: `PORT = 3003` (hardcoded in index.ts)

4. **Agent Configuration** ([config/agents.yaml](config/agents.yaml))
   - Defines agent metadata (role, specialty, keywords)
   - References ports and endpoints
   - Used by Albedo for intelligent routing

### **Root `.env` Contains:**

```env
# API Keys (shared by all agents)
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_TOKEN=ghp_...

# Telegram Bot
TELEGRAM_BOT_TOKEN=...
TELEGRAM_USER_ID=...

# Database
DATABASE_URL=sqlite:///data/database/pm_system.db

# Budget Tracking
DAILY_BUDGET_ALERT=1.00
MONTHLY_BUDGET_LIMIT=20.00
```

### **No Need for Per-Agent `.env` Files!**

You do **NOT** need to create:
- ❌ `dev-agents/frontend-agent/.env`
- ❌ `dev-agents/backend-agent/.env`
- ❌ `dev-agents/database-agent/.env`

All agents automatically load from the root `.env` via `shared-env.js`.

---

## Alternative: Per-Agent `.env` Files (Not Recommended)

If you really wanted separate `.env` files for each agent:

### **Pros:**
- Each agent is fully independent
- Can use different API keys per agent (if needed)
- Agent directories are self-contained

### **Cons:**
- ❌ Duplicates API keys in 3+ files
- ❌ Must update keys in multiple places
- ❌ More files to .gitignore
- ❌ Harder to maintain consistency
- ❌ Security risk (more copies of secrets)

### **When to Use:**
- Each agent needs different credentials (rare)
- Agents deployed separately on different servers
- Testing different API providers per agent

---

## Configuration File Hierarchy

```
My_Devs_AI_Agent_team/
├── .env                          # ✅ ROOT .env (all API keys here)
├── config/
│   └── agents.yaml               # ✅ Agent metadata and routing rules
├── dev-agents/
│   ├── shared-env.js             # ✅ Loads root .env for all agents
│   ├── frontend-agent/
│   │   ├── .env.example          # Template (for reference only)
│   │   └── src/
│   │       └── index.ts          # PORT=3001, imports shared-env
│   ├── backend-agent/
│   │   ├── .env.example          # Template (for reference only)
│   │   └── src/
│   │       └── index.ts          # PORT=3002, imports shared-env
│   └── database-agent/
│       ├── .env.example          # Template (for reference only)
│       └── src/
│           └── index.ts          # PORT=3003, imports shared-env
```

---

## Quick Start (With Centralized Config)

### 1. Verify Root `.env` Exists

```bash
# Check that root .env has your API keys
cat .env | grep OPENAI_API_KEY
cat .env | grep ANTHROPIC_API_KEY
cat .env | grep GITHUB_TOKEN
```

Should show:
```env
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_TOKEN=ghp_...
```

✅ **If keys are present, you're done!** No need to create per-agent .env files.

### 2. Start All Agents

```bash
cd dev-agents
npm start
```

Expected output:
```
✅ Environment loaded from root .env
   OpenAI API Key: sk-proj-qrO1JHAzBm_...
   Anthropic API Key: sk-ant-api03-S5gGt1...
   GitHub Token: ghp_9SnAknvW1eu...

🚀 Dev Agent Service running on http://localhost:3001
🚀 Dev Agent Service running on http://localhost:3002
🚀 Dev Agent Service running on http://localhost:3003
```

### 3. Start Albedo

```bash
python src/telegram/bot.py
```

---

## Agent Configuration (agents.yaml)

The `config/agents.yaml` file defines **metadata** for routing and capabilities:

```yaml
agents:
  frontend_agent:
    port: 3001
    endpoint: "http://localhost:3001/execute-task"
    specialty: "HTML/CSS/JS/React/UI/UX"
    keywords:
      - frontend
      - ui
      - react
      - component
    # ... etc
```

**What it does:**
- Albedo reads this to know which agent handles which tasks
- Routes tasks based on keywords (e.g., "react" → frontend_agent)
- Shows agent capabilities in `/status` command

**What it does NOT do:**
- ❌ Does NOT configure API keys
- ❌ Does NOT set PORT (that's in index.ts)
- ❌ Does NOT load environment variables

---

## Summary: Why Centralized is Better

| Aspect | Centralized (✅ Recommended) | Per-Agent (❌ Not Recommended) |
|--------|---------------------------|-------------------------------|
| **API Key Management** | Single file (root `.env`) | 3+ files (duplicated) |
| **Updating Keys** | Change once | Change in 3+ files |
| **Security** | Fewer secret files | More files to secure |
| **Maintenance** | Simple | Complex |
| **DRY Principle** | ✅ Follows | ❌ Violates |
| **Best Practice** | ✅ Industry standard | ❌ Anti-pattern |

---

## Next Steps

**You're all set!** The system now uses:
1. ✅ Root `.env` for all API keys
2. ✅ `shared-env.js` to load variables
3. ✅ Hardcoded ports in each `index.ts`
4. ✅ `agents.yaml` for metadata and routing

Just run:
```bash
cd dev-agents && npm start
```

No need to create or edit per-agent `.env` files! 🎉

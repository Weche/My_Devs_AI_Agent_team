# Deployment Guide - My_Devs_AI_Agent_team on Fly.io

## 🎯 Current Project Overview

Based on your GitHub repos, you have experience with:
- **langserve-basic-example** - Python app deployed to Fly.io
- **agent-farmacia-chile** - Python API agent
- **rag_agentic** - HTML/Python app

This project is more complex - it's a **multi-service architecture**:
- 1 Python backend (Albedo PM Agent + Telegram Bot)
- 3 Node.js services (Frontend/Backend/Database Dev Agents)
- 1 SQLite database
- Shared file storage (workspaces/)

---

## 📊 What We Have Deployed (Check First)

### **Step 1: Install Fly CLI**

```powershell
# Install Fly CLI on Windows
iwr https://fly.io/install.ps1 -useb | iex
```

### **Step 2: Login and Check Current Apps**

```powershell
# Login to Fly.io
fly auth login

# List all your current apps
fly apps list

# Check status of specific apps
fly status -a <app-name>
```

### **Step 3: Check Existing Deployments**

Look for these potential apps:
- `langserve-basic-example` (from your GitHub)
- `agent-farmacia-chile` (from your GitHub)
- Any other agent projects you've deployed

---

## 🏗️ Deployment Architecture Options

### **Option 1: Monolithic (Simplest)**

**Single Fly App with Multiple Processes:**
- Deploy all services in one container
- Use a process manager (PM2 or supervisor)
- Share SQLite database via volume

**Pros:**
- ✅ Easiest to deploy
- ✅ Lowest cost (1 machine)
- ✅ Shared filesystem works naturally

**Cons:**
- ❌ All services restart together
- ❌ Can't scale agents independently
- ❌ Single point of failure

**Cost:** ~$5-10/month (shared-cpu-1x)

---

### **Option 2: Multi-App (Recommended)**

**Separate Fly Apps for Each Service:**
- `albedo-pm-agent` (Python + Telegram Bot)
- `dev-agents-cluster` (3 Node.js agents in one app)

**Pros:**
- ✅ Independent scaling
- ✅ Isolated failures
- ✅ Better monitoring

**Cons:**
- ❌ More complex setup
- ❌ Need shared database solution
- ❌ Higher cost

**Cost:** ~$15-25/month (2 apps)

---

### **Option 3: Full Microservices (Advanced)**

**5 Separate Fly Apps:**
- `albedo-pm-agent` (Python)
- `frontend-dev-agent` (Node.js)
- `backend-dev-agent` (Node.js)
- `database-dev-agent` (Node.js)
- `shared-database` (Postgres or LiteFS)

**Pros:**
- ✅ Maximum flexibility
- ✅ True microservices
- ✅ Can use Fly.io autoscaling

**Cons:**
- ❌ Complex networking
- ❌ Highest cost
- ❌ SQLite won't work (need Postgres)

**Cost:** ~$40-60/month (5 apps)

---

## 🚀 Recommended Deployment: Option 2 (Multi-App)

**Two Fly Apps:**

### **App 1: `albedo-pm-agent`** (Python Backend)

**What it runs:**
- Telegram bot (`src/telegram/bot.py`)
- Albedo PM Agent (`src/agents/pm_agent.py`)
- Scheduler for proactive updates
- SQLite database (via Fly volume)

**Resources:**
- Shared CPU 1x (256MB RAM)
- 1GB persistent volume for database
- Region: Santiago (closest to you)

**Estimated Cost:** $5-8/month

---

### **App 2: `dev-agents-cluster`** (Node.js Services)

**What it runs:**
- Frontend Agent (Port 3001)
- Backend Agent (Port 3002)
- Database Agent (Port 3003)
- Orchestrator to manage all 3

**Resources:**
- Shared CPU 1x (512MB RAM)
- Shared volume with albedo-pm-agent for workspaces
- Region: Santiago

**Estimated Cost:** $8-12/month

---

## 📋 Pre-Deployment Checklist

### **1. Install Fly CLI**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
fly version
```

### **2. Login to Fly.io**
```powershell
fly auth login
```

### **3. Check Current Apps**
```powershell
fly apps list
fly status -a langserve-basic-example  # If it exists
```

### **4. Prepare Environment Variables**

Create `.env.production`:
```env
# API Keys
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_TOKEN=ghp_...

# Telegram
TELEGRAM_BOT_TOKEN=8099019281:AAGl3b0M_x4KPfvsEf8gyC6csYzVzGLV61o
TELEGRAM_USER_ID=814615401

# Database (on Fly volume)
DATABASE_URL=sqlite:////data/pm_system.db

# Budget
DAILY_BUDGET_ALERT=1.00
MONTHLY_BUDGET_LIMIT=20.00
```

### **5. Create Dockerfiles**

#### **Dockerfile.albedo** (Python Backend)
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory for SQLite
RUN mkdir -p /data/database

# Expose port (internal only, Telegram uses webhooks)
EXPOSE 8080

# Run bot
CMD ["python", "src/telegram/bot.py"]
```

#### **Dockerfile.agents** (Node.js Dev Agents)
```dockerfile
FROM node:24-slim

WORKDIR /app

# Copy orchestrator and shared env
COPY dev-agents/package.json dev-agents/orchestrator.js dev-agents/shared-env.js ./

# Copy all 3 agents
COPY dev-agents/frontend-agent ./frontend-agent
COPY dev-agents/backend-agent ./backend-agent
COPY dev-agents/database-agent ./database-agent

# Install dependencies
RUN npm install
RUN cd frontend-agent && npm install
RUN cd backend-agent && npm install
RUN cd database-agent && npm install

# Copy root .env to container
COPY .env .env

# Expose ports
EXPOSE 3001 3002 3003

# Run orchestrator
CMD ["npm", "start"]
```

### **6. Create fly.toml Files**

#### **fly.albedo.toml**
```toml
app = "albedo-pm-agent"
primary_region = "scl"  # Santiago, Chile

[build]
  dockerfile = "Dockerfile.albedo"

[env]
  PORT = "8080"
  PYTHON_VERSION = "3.13"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = "suspend"
  auto_start_machines = true
  min_machines_running = 1
  processes = ["app"]

[[vm]]
  memory = "512mb"
  cpu_kind = "shared"
  cpus = 1

[mounts]
  source = "albedo_data"
  destination = "/data"
  initial_size = "1gb"
```

#### **fly.agents.toml**
```toml
app = "dev-agents-cluster"
primary_region = "scl"  # Santiago, Chile

[build]
  dockerfile = "Dockerfile.agents"

[env]
  NODE_VERSION = "24"

[[services]]
  internal_port = 3001
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]
    force_https = true

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

[[services]]
  internal_port = 3002
  protocol = "tcp"

[[services]]
  internal_port = 3003
  protocol = "tcp"

[[vm]]
  memory = "1gb"
  cpu_kind = "shared"
  cpus = 1

[mounts]
  source = "dev_workspaces"
  destination = "/app/workspaces"
  initial_size = "2gb"
```

---

## 🚀 Deployment Steps

### **Deploy Albedo PM Agent (Python)**

```powershell
cd C:\Users\Christian Orquera\My_Devs_AI_Agent_team

# Create Fly app
fly apps create albedo-pm-agent --org personal

# Create volume for database
fly volumes create albedo_data --size 1 --region scl -a albedo-pm-agent

# Set secrets (don't commit these!)
fly secrets set OPENAI_API_KEY=sk-proj-... -a albedo-pm-agent
fly secrets set ANTHROPIC_API_KEY=sk-ant-... -a albedo-pm-agent
fly secrets set TELEGRAM_BOT_TOKEN=8099019281:AAGl3b0M_x4KPfvsEf8gyC6csYzVzGLV61o -a albedo-pm-agent
fly secrets set TELEGRAM_USER_ID=814615401 -a albedo-pm-agent
fly secrets set GITHUB_TOKEN=ghp_... -a albedo-pm-agent

# Deploy
fly deploy -c fly.albedo.toml -a albedo-pm-agent

# Check status
fly status -a albedo-pm-agent
fly logs -a albedo-pm-agent
```

### **Deploy Dev Agents Cluster (Node.js)**

```powershell
# Create Fly app
fly apps create dev-agents-cluster --org personal

# Create volume for workspaces
fly volumes create dev_workspaces --size 2 --region scl -a dev-agents-cluster

# Set secrets
fly secrets set OPENAI_API_KEY=sk-proj-... -a dev-agents-cluster
fly secrets set GITHUB_TOKEN=ghp_... -a dev-agents-cluster

# Deploy
fly deploy -c fly.agents.toml -a dev-agents-cluster

# Check status
fly status -a dev-agents-cluster
fly logs -a dev-agents-cluster
```

---

## 🔍 Post-Deployment Verification

### **1. Check Both Apps Are Running**
```powershell
fly apps list
fly status -a albedo-pm-agent
fly status -a dev-agents-cluster
```

### **2. Check Logs**
```powershell
# Albedo logs
fly logs -a albedo-pm-agent

# Dev Agents logs
fly logs -a dev-agents-cluster
```

### **3. Test Telegram Bot**
```
Open Telegram → Message your bot
"Hello Albedo"
"Check all agent status"
```

### **4. Check Agent Health**
```powershell
# Test Frontend Agent
fly ssh console -a dev-agents-cluster
curl http://localhost:3001/health

# Test Backend Agent
curl http://localhost:3002/health

# Test Database Agent
curl http://localhost:3003/health
```

---

## 💰 Cost Estimation

| Service | Resources | Cost/Month |
|---------|-----------|------------|
| albedo-pm-agent | Shared CPU 1x, 512MB RAM | $5-8 |
| dev-agents-cluster | Shared CPU 1x, 1GB RAM | $8-12 |
| albedo_data volume | 1GB | $0.15 |
| dev_workspaces volume | 2GB | $0.30 |
| **Total** | | **$13-20/month** |

**Free Tier:** Fly.io gives $5/month credit, so actual cost is ~$8-15/month

---

## 🔧 Environment-Specific Configuration

### **Development (Local)**
- Use root `.env` file
- Run orchestrator locally: `npm start`
- Run bot locally: `python src/telegram/bot.py`

### **Production (Fly.io)**
- Use Fly secrets for API keys
- Volumes for persistent data
- Internal networking between apps

---

## 🚨 Troubleshooting

### **Problem: Bot not responding on Telegram**
```powershell
fly logs -a albedo-pm-agent --follow
# Check for errors connecting to Telegram API
```

### **Problem: Agents can't connect to database**
```powershell
fly ssh console -a dev-agents-cluster
ls -la /data/database/
# Verify pm_system.db exists
```

### **Problem: Out of memory**
```powershell
fly scale memory 1024 -a dev-agents-cluster
# Upgrade to 1GB RAM
```

---

## 📌 Next Steps

1. **Install Fly CLI:** `iwr https://fly.io/install.ps1 -useb | iex`
2. **Check existing apps:** `fly apps list`
3. **Review deployment option** (recommend Option 2)
4. **Create Dockerfiles** (provided above)
5. **Deploy step-by-step** (follow deployment steps)

Would you like me to:
- Create the Dockerfiles now?
- Set up the fly.toml configuration files?
- Help you choose the best deployment architecture?

Let me know and we'll get this deployed! 🚀

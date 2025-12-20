# Multi-Agent Dev Team

This directory contains 3 specialized Dev Agents powered by StreamUI (Vercel AI SDK) for parallel task execution.

## Architecture

```
┌─────────────────────────────────────────┐
│  Albedo (PM Agent)                      │
│  - Coordinates all agents               │
│  - Assigns tasks intelligently          │
└──────────┬──────────────────────────────┘
           │
    ┌──────┴──────┬──────────┬────────────┐
    ▼             ▼          ▼            ▼
┌────────┐  ┌────────┐  ┌────────┐  ┌──────────┐
│Frontend│  │Backend │  │Database│  │Lead Dev  │
│Agent   │  │Agent   │  │Agent   │  │(Claude)  │
│Port    │  │Port    │  │Port    │  │          │
│3001    │  │3002    │  │3003    │  │          │
└────────┘  └────────┘  └────────┘  └──────────┘
```

## Agents

### 1. Frontend Agent (Port 3001)
**Specialty:** HTML, CSS, JavaScript, React, UI/UX

**Expertise:**
- Responsive web design (mobile-first)
- Modern CSS (Flexbox, Grid, Tailwind)
- Component-based architecture (React, Vue, Angular)
- Accessibility (ARIA, semantic HTML)
- User experience and visual polish

**Assigns when task contains:**
- frontend, ui, ux, html, css, javascript, react, vue, angular
- component, interface, layout, styling, responsive

### 2. Backend Agent (Port 3002)
**Specialty:** Python, Node.js, APIs, Server Architecture

**Expertise:**
- RESTful APIs and GraphQL
- Python (FastAPI, Flask, Django)
- Node.js (Express, NestJS)
- Authentication & authorization
- Security best practices

**Assigns when task contains:**
- backend, api, server, endpoint, python, nodejs, express
- fastapi, flask, django, rest, graphql, microservice

### 3. Database Agent (Port 3003)
**Specialty:** SQL, PostgreSQL, MongoDB, Data Architecture

**Expertise:**
- Database schema design
- SQL (PostgreSQL, MySQL, SQLite)
- NoSQL (MongoDB, Redis)
- Migrations and seeding
- Query optimization and indexing

**Assigns when task contains:**
- database, sql, postgresql, mysql, mongodb, schema
- migration, query, orm, data, storage

## Setup

### 1. Install Dependencies

```bash
cd dev-agents/frontend-agent
npm install

cd ../backend-agent
npm install

cd ../database-agent
npm install
```

### 2. Configure Environment

Create `.env` files for each agent (copy from `.env.example`):

```bash
# Frontend Agent (.env)
cp frontend-agent/.env.example frontend-agent/.env

# Backend Agent (.env)
cp backend-agent/.env.example backend-agent/.env

# Database Agent (.env)
cp database-agent/.env.example database-agent/.env
```

Edit each `.env` file and add your API keys:

```env
# Use the same OpenAI API key for all agents
OPENAI_API_KEY=your_openai_key_here

# Or use Claude (requires Anthropic API)
# USE_ANTHROPIC=true
# ANTHROPIC_API_KEY=your_anthropic_key_here

# GitHub credentials (for git push)
GITHUB_USER=your_github_username
GITHUB_TOKEN=your_github_token
```

### 3. Run All Agents

**Option A: Run individually**

```bash
# Terminal 1: Frontend Agent
cd dev-agents/frontend-agent
npm run dev

# Terminal 2: Backend Agent
cd dev-agents/backend-agent
npm run dev

# Terminal 3: Database Agent
cd dev-agents/database-agent
npm run dev
```

**Option B: Run with parallel script (future enhancement)**

```bash
npm run dev:all
```

## How Albedo Uses Multiple Agents

Albedo intelligently routes tasks to the appropriate specialist:

### Automatic Assignment

```python
# Albedo's auto_assign_task() analyzes task content
Task: "Create user login form"
→ Frontend Agent (UI component)

Task: "Build authentication API endpoints"
→ Backend Agent (API development)

Task: "Design user schema and migrations"
→ Database Agent (schema design)
```

### Batch Assignment

```python
# Albedo can assign multiple tasks in parallel
Master: "Assign all TODO tasks to our agents"

Albedo:
✅ Task #10 → Frontend Agent (executing...)
✅ Task #11 → Backend Agent (executing...)
✅ Task #12 → Database Agent (executing...)
```

## Performance Benefits

- **3x Parallel Execution:** Work on 3 tasks simultaneously
- **Specialist Expertise:** Each agent optimized for their domain
- **76% Faster:** StreamUI vs LangGraph (per agent)
- **66% Fewer Tokens:** Cost-effective AI usage

## Monitoring

Check agent health:

```bash
curl http://localhost:3001/health  # Frontend
curl http://localhost:3002/health  # Backend
curl http://localhost:3003/health  # Database
```

Expected response:

```json
{
  "status": "healthy",
  "service": "Frontend Dev Agent",
  "version": "1.0.0",
  "timestamp": "2025-12-20T10:30:00.000Z"
}
```

## Troubleshooting

### Agent not responding
1. Check if agent is running: `curl http://localhost:300X/health`
2. Check logs in terminal window
3. Verify `.env` file has correct API keys

### Task assignment errors
1. Ensure database path is correct in `.env`
2. Check that `WORKSPACE_DIR` points to correct location
3. Verify GitHub token has correct permissions (if pushing)

### Port conflicts
If port 3001/3002/3003 already in use, change `PORT` in `.env`:

```env
PORT=3004  # Use different port
```

## Files

```
dev-agents/
├── README.md                    # This file
├── frontend-agent/
│   ├── package.json            # Dependencies
│   ├── tsconfig.json           # TypeScript config
│   ├── .env.example            # Environment template
│   └── src/
│       ├── index.ts            # Express server (port 3001)
│       ├── agent.ts            # Frontend specialist agent
│       ├── types.ts            # TypeScript types
│       └── tools/              # StreamUI tools (file-writer, git, task-updater)
├── backend-agent/              # Same structure (port 3002)
└── database-agent/             # Same structure (port 3003)
```

## Next Steps

1. Run all 3 agents in separate terminals
2. Test with Telegram bot: "Assign all tasks to our agents"
3. Watch parallel execution in agent terminals
4. Check workspaces/[project-slug]/ for generated code

---

**Powered by:**
- StreamUI (Vercel AI SDK) - 76% faster than LangGraph
- GPT-4o - Primary model
- Claude Sonnet 4.5 - Optional (set USE_ANTHROPIC=true)

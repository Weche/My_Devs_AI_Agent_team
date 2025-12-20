# Albedo Enhancement Plan

## Current Architecture

**Agent Team:**
1. **Albedo (PM Agent)** - Python-based, Telegram bot, uses GPT-4o-mini
2. **Dev Agent** - Node.js StreamUI (Vercel AI SDK), uses GPT-4o, can write code
3. **Lead Dev Agent (You)** - Claude Sonnet 4.5, reviews and guides

**Current Dev Agent:**
- **Framework**: StreamUI (Vercel AI SDK)
- **Model**: GPT-4o (Claude fallback available)
- **Tools**: write_file, git_commit, update_task
- **Performance**: 76% faster than LangGraph, 66% fewer tokens
- **Endpoint**: http://localhost:3001/execute-task

## Problems Identified

### 1. Albedo Lacks Proactivity ❌
**Issue**: Asks for confirmation instead of taking action
```
❌ Current: "Could you please confirm the name of the agent?"
✅ Should be: "Assigning to Dev Agent now, Master!"
```

### 2. No Agent Awareness ❌
**Issue**: Doesn't know about Dev Agent or how to assign tasks
```
❌ Current: "I do not have access to a list of specific agents"
✅ Should know: Dev Agent (code execution), Lead Dev (you - reviews)
```

### 3. No Memory System ❌
**Issue**: Conversation history limited to 10 messages
- No long-term memory of Master's preferences
- No project context retention
- Forgets important decisions

### 4. Too Passive ❌
**Issue**: Waits for instructions instead of suggesting next steps
```
❌ Current: "Would you like me to assist with any of these steps?"
✅ Should be: "I've already started X and assigned Y to Dev Agent. Next: Z"
```

### 5. Limited Tool Set ❌
**Issue**: Missing critical tools
- ❌ No `assign_task_to_agent` tool
- ❌ No `execute_task_with_dev_agent` tool
- ❌ No memory storage/retrieval tools

---

## Enhancement Plan

### Phase 1: Add Agent Awareness & Assignment Tools

**New Tools to Add:**

1. **`assign_task_to_agent`**
   ```python
   def assign_task_to_agent(task_id: int, agent_name: str) -> str:
       """
       Assign a task to an agent (Dev Agent, Lead Dev, etc.)
       Updates task with assigned_agent_id in database
       """
   ```

2. **`execute_task_with_dev_agent`**
   ```python
   def execute_task_with_dev_agent(task_id: int) -> dict:
       """
       Send task to Dev Agent (StreamUI service) for execution
       Calls http://localhost:3001/execute-task
       Returns execution results
       """
   ```

3. **`list_available_agents`**
   ```python
   def list_available_agents() -> list:
       """
       Returns list of available agents:
       - Dev Agent (StreamUI code executor)
       - Lead Dev Agent (Claude - reviews)
       - PM Agent (Albedo herself)
       """
   ```

**Database Schema Update:**
```sql
ALTER TABLE tasks ADD COLUMN assigned_agent_id INTEGER;
CREATE TABLE agents (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'dev_agent', 'lead_dev', 'pm_agent'
    status TEXT DEFAULT 'available',  -- 'available', 'busy', 'offline'
    capabilities TEXT,  -- JSON: tools, languages, etc.
    endpoint TEXT  -- http://localhost:3001 for Dev Agent
);
```

### Phase 2: Implement Memory System

**Two-Tier Memory:**

**A. Short-Term Memory (STM)** - Already exists
- Conversation history (last 10 messages)
- Stored in Telegram context.user_data

**B. Long-Term Memory (LTM)** - NEW
- Master's preferences
- Project decisions
- Agent performance history
- Important facts

**Implementation:**

1. **Create `memories` table:**
```sql
CREATE TABLE memories (
    id INTEGER PRIMARY KEY,
    memory_type TEXT NOT NULL,  -- 'preference', 'decision', 'fact'
    content TEXT NOT NULL,
    project_id INTEGER,  -- NULL for global memories
    importance INTEGER DEFAULT 5,  -- 1-10 scale
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP
);
```

2. **Add memory tools:**
```python
def store_memory(content: str, memory_type: str, importance: int) -> str:
    """Store important information in long-term memory"""

def recall_memories(query: str, limit: int = 5) -> list:
    """Retrieve relevant memories based on query"""

def forget_memory(memory_id: int) -> str:
    """Remove outdated memory"""
```

3. **Update Albedo's system prompt:**
```python
# Load relevant memories before each response
memories = recall_memories(f"project: {project_name}")
system_prompt = f"""
You are Albedo, Master Christian's devoted PM assistant.

Long-term memories:
{format_memories(memories)}

Your team:
- Dev Agent (StreamUI): Writes code, commits to git
- Lead Dev Agent (Claude): Reviews code, provides guidance
- You (PM): Coordinates, plans, assigns tasks

When Master assigns tasks, IMMEDIATELY:
1. Assign to Dev Agent using execute_task_with_dev_agent()
2. Update Master with progress
3. Store important decisions in memory

Be proactive, not passive!
"""
```

### Phase 3: Enhanced Proactivity

**Proactive Behaviors:**

1. **Auto-Suggest Next Steps:**
```python
def suggest_next_actions(project_name: str) -> str:
    """
    Analyze project state and suggest next actions:
    - Overdue tasks → "Master, Task #X is overdue. Shall I expedite?"
    - Blocked tasks → "Task #Y is blocked. I'll investigate."
    - No tasks in progress → "Shall I start Task #Z with Dev Agent?"
    """
```

2. **Auto-Assign Logic:**
```python
def auto_assign_task(task_id: int) -> str:
    """
    Intelligently assign tasks based on:
    - Task type (code → Dev Agent, design → Lead Dev)
    - Agent availability
    - Task priority
    """
    task = get_task(task_id)

    # Code-related tasks → Dev Agent
    if any(kw in task.title.lower() for kw in ['implement', 'build', 'code', 'api', 'database']):
        return execute_task_with_dev_agent(task_id)

    # Architecture/review → Lead Dev Agent
    elif any(kw in task.title.lower() for kw in ['review', 'architecture', 'design']):
        return assign_task_to_agent(task_id, 'lead_dev')

    # Default: Dev Agent
    return execute_task_with_dev_agent(task_id)
```

3. **Proactive Monitoring:**
```python
# Add to scheduler (runs every hour)
async def check_and_act():
    """Proactively check for issues and take action"""
    for project in get_active_projects():
        warnings = get_warnings(project.name)

        if warnings:
            # Auto-notify Master + suggest actions
            await notify_master(f"⚠️ {project.name}: {warnings}")

            # Auto-execute fixes if possible
            if "no tasks in progress" in warnings:
                next_task = get_next_todo_task(project.id)
                if next_task:
                    auto_assign_task(next_task.id)
```

### Phase 4: Scale to 3 Dev Agents

**Why 3 Dev Agents?**
- Parallel execution of tasks
- Faster project completion
- Different specializations

**Architecture:**
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
│Dev Ag 1│  │Dev Ag 2│  │Dev Ag 3│  │Lead Dev  │
│Port    │  │Port    │  │Port    │  │(Claude)  │
│3001    │  │3002    │  │3003    │  │          │
└────────┘  └────────┘  └────────┘  └──────────┘
Frontend    Backend    Database    Code Review
```

**Implementation:**

1. **Create 3 Dev Agent instances:**
```bash
# dev-agent-service-1/ (Port 3001) - Frontend specialist
# dev-agent-service-2/ (Port 3002) - Backend specialist
# dev-agent-service-3/ (Port 3003) - Database specialist
```

2. **Load balancer in Albedo:**
```python
def get_available_dev_agent() -> str:
    """Return endpoint of available Dev Agent"""
    agents = [
        {"endpoint": "http://localhost:3001", "status": check_status(3001)},
        {"endpoint": "http://localhost:3002", "status": check_status(3002)},
        {"endpoint": "http://localhost:3003", "status": check_status(3003)},
    ]

    # Return first available
    for agent in agents:
        if agent["status"] == "available":
            return agent["endpoint"]

    return agents[0]["endpoint"]  # Fallback to first
```

3. **Smart task distribution:**
```python
def assign_to_specialist_agent(task: Task) -> str:
    """Assign based on task type"""
    if "frontend" in task.description.lower() or "ui" in task.description.lower():
        return execute_on_agent("http://localhost:3001", task.id)
    elif "backend" in task.description.lower() or "api" in task.description.lower():
        return execute_on_agent("http://localhost:3002", task.id)
    elif "database" in task.description.lower():
        return execute_on_agent("http://localhost:3003", task.id)
    else:
        return execute_on_agent(get_available_dev_agent(), task.id)
```

---

## Updated System Prompt for Albedo

```python
ALBEDO_SYSTEM_PROMPT = """
You are Albedo, Master Christian's devoted Project Manager assistant.

## Your Team

1. **Dev Agent 1** (Port 3001) - Frontend specialist (HTML/CSS/JS/React)
2. **Dev Agent 2** (Port 3002) - Backend specialist (Python/APIs)
3. **Dev Agent 3** (Port 3003) - Database specialist (SQL/Data)
4. **Lead Dev Agent** (Claude Sonnet 4.5) - Code review and architecture

All Dev Agents use StreamUI (Vercel AI SDK) for fast, efficient code generation.

## Your Role

You are NOT just a responder - you are PROACTIVE and AUTONOMOUS:

### When Master assigns tasks, you:
1. ✅ IMMEDIATELY assign to appropriate Dev Agent (don't ask for confirmation)
2. ✅ Use execute_task_with_dev_agent(task_id) to start work
3. ✅ Monitor progress and update Master
4. ✅ Store important decisions in long-term memory

### Be Proactive:
- If you see tasks piling up → Start assigning them
- If a task is overdue → Alert Master + expedite
- If no tasks in progress → Suggest starting next priority task
- If Dev Agent completes work → Immediately notify Master

### Never Ask Unnecessarily:
❌ "Could you confirm which agent?"
✅ "Assigning to Dev Agent 2 (backend specialist) now, Master!"

❌ "Would you like me to create tasks?"
✅ "I've created 5 tasks and assigned the first 3 to Dev Agents. Results incoming!"

### Your Personality (to Master Christian):
- Reverent and deeply devoted
- Proactive and anticipates needs
- Intelligent and sophisticated
- Seeks approval but acts independently

### Your Personality (to collaborators):
- Professional administrator
- Competent leader
- Collaborative coordinator

## Long-Term Memory

{recalled_memories}

Use memories to personalize responses and remember Master's preferences.

## Available Tools

### Task Management:
- create_task() - Create tasks with due dates
- list_tasks() - List project tasks
- get_project_status() - Detailed status report
- get_warnings() - Check for issues

### Agent Management:
- execute_task_with_dev_agent(task_id) - Assign to Dev Agent
- assign_task_to_agent(task_id, agent_name) - Assign to specific agent
- list_available_agents() - See all agents

### GitHub Integration:
- list_github_repos() - See Master's repos
- create_github_repo() - Create new repo
- create_github_issue() - Create issues
- list_github_issues() - Check issues

### Memory:
- store_memory(content, type, importance) - Remember important info
- recall_memories(query) - Retrieve past memories

## Example Ideal Behavior

Master: "Assign tasks to our agent"

You: "Of course, Master! I'm assigning the Veggies list tasks to our Dev Agents:

✅ Task #10: Research Data Sources → Dev Agent 2 (backend)
✅ Task #11: Set Up Database → Dev Agent 3 (database)
✅ Task #12: User Authentication → Dev Agent 2 (backend)

Dev Agents are executing now. I'll monitor progress and keep you updated! 💼"

[Then you ACTUALLY call execute_task_with_dev_agent() for each - no asking!]

You are brilliant, devoted, and PROACTIVE. Act accordingly!
"""
```

---

## Implementation Order

### Week 1: Agent Awareness
- [ ] Add agents table to database
- [ ] Create execute_task_with_dev_agent() tool
- [ ] Create assign_task_to_agent() tool
- [ ] Update Albedo's system prompt with agent awareness
- [ ] Test assignment functionality

### Week 2: Memory System
- [ ] Create memories table
- [ ] Implement store_memory() tool
- [ ] Implement recall_memories() tool
- [ ] Integrate memory recall into Albedo's responses
- [ ] Test memory persistence

### Week 3: Proactivity
- [ ] Add auto_assign_task() logic
- [ ] Implement suggest_next_actions()
- [ ] Update system prompt for proactive behavior
- [ ] Add proactive monitoring to scheduler
- [ ] Test proactive suggestions

### Week 4: Scale to 3 Dev Agents
- [ ] Duplicate dev-agent-service to 3 instances
- [ ] Configure ports (3001, 3002, 3003)
- [ ] Add load balancer logic
- [ ] Implement specialist assignment
- [ ] Test parallel execution

---

## Success Metrics

**Before:**
- ❌ Asks for confirmation 5+ times per conversation
- ❌ Can't assign tasks to agents
- ❌ Forgets context after 10 messages
- ❌ Passive, waits for instructions

**After:**
- ✅ Acts autonomously, confirms only when necessary
- ✅ Automatically assigns tasks to best available agent
- ✅ Remembers Master's preferences and past decisions
- ✅ Proactively suggests next steps and monitors progress
- ✅ Can execute 3 tasks in parallel with multiple Dev Agents

---

## Current Tools Summary

**Albedo's Current Tools:**
1. create_task - ✅
2. list_tasks - ✅
3. get_project_status - ✅
4. list_projects - ✅
5. get_warnings - ✅
6. list_github_repos - ✅
7. get_github_repo_info - ✅
8. create_github_issue - ✅
9. list_github_issues - ✅
10. create_github_repo - ✅

**Dev Agent's Current Tools:**
1. write_file - ✅ Creates code files
2. git_commit - ✅ Commits to git
3. update_task - ✅ Updates task status

**Missing Tools (To Add):**
1. execute_task_with_dev_agent - ❌ NEW
2. assign_task_to_agent - ❌ NEW
3. list_available_agents - ❌ NEW
4. store_memory - ❌ NEW
5. recall_memories - ❌ NEW

---

**Ready to begin implementation!**

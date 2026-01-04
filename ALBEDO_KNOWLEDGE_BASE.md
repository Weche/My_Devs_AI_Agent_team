# Albedo's Knowledge Base - What Your PM Agent Knows

## 🎯 Overview

Albedo (your PM Agent) has been updated with complete knowledge of the GitHub-backed storage architecture and automatic push workflow.

---

## 📚 What Albedo Knows

### **1. Storage Architecture**

Albedo understands the three-tier storage system:

```
├── Database (Persistent)
│   └── /data/database/pm_system.db (1GB Fly.io volume - $0.15/month)
│
├── Workspaces (Ephemeral)
│   └── /tmp/workspaces/ (cleared on restart, FREE)
│
└── Code Storage (Permanent)
    └── GitHub repos (unlimited, FREE)
```

### **2. Dev Agent Workflow**

Albedo knows that when Dev Agents complete tasks, they **AUTOMATICALLY**:

1. ✅ Generate code in `/tmp/workspaces/project-name/`
2. ✅ Commit with descriptive message (`git commit -m "Task #X: ..."`)
3. ✅ **Push to GitHub** (default: `push=true`) ← AUTOMATIC!
4. ✅ Update task status to 'review'
5. ✅ Code persists in GitHub forever

### **3. Cost Savings Knowledge**

Albedo understands the cost optimization:

- **Old approach**: 3GB volume = $0.45/month
- **New approach**: 1GB volume + GitHub = **$0.15/month**
- **Savings**: $0.30/month ($3.60/year)

### **4. Environment Configuration**

Albedo knows the environment setup:

```bash
WORKSPACE_DIR=/tmp/workspaces        # Ephemeral
DATABASE_PATH=/data/database/pm_system.db  # Persistent
GITHUB_TOKEN=ghp_...                 # Encrypted in Fly secrets
GITHUB_USER=Weche                    # Your GitHub username
```

### **5. What Albedo Will Tell You**

When tasks are assigned and completed, Albedo will proactively inform you:

- ✅ "Code is automatically pushed to GitHub at: `github.com/Weche/[project-name]`"
- ✅ "You can clone locally anytime: `git clone https://github.com/Weche/[project-name]`"
- ✅ "All task commits are tracked with full version history"

---

## 🤖 Example Conversation

**You (Master):** "Albedo, assign task #29 to the frontend agent"

**Albedo:** "Of course, Master! Assigning Task #29 to Frontend Dev Agent now...

✅ Task #29 → Frontend Agent (executing...)

The agent will generate the login page and automatically push the code to GitHub at: `github.com/Weche/yohga-init`

You can view the progress in real-time, and all commits will be tracked with full version history! 💼"

---

## 🎓 What This Means for You

### **Albedo is Now Fully Aware:**

1. **Storage Architecture**: Knows exactly where data lives and why
2. **Auto-Push Workflow**: Understands that all code auto-pushes to GitHub
3. **Cost Efficiency**: Aware of the 66% cost savings
4. **GitHub Integration**: Will provide GitHub URLs and cloning instructions
5. **Zero Data Loss**: Knows that code is safe even if containers restart

### **You Can Ask Albedo:**

- "Where is the code stored?"
- "How much does our infrastructure cost?"
- "Can I access the code locally?"
- "What happens if the container restarts?"

Albedo will answer accurately with full knowledge of the GitHub-backed architecture!

---

## 🚀 Deployment Ready

Albedo's system prompt has been updated in:
- ✅ [src/agents/pm_agent.py](src/agents/pm_agent.py) (lines 302-336)

When you deploy to Fly.io, Albedo will have this knowledge immediately!

---

## 📝 Summary

**Albedo now knows:**
- ✅ GitHub-backed storage architecture
- ✅ Automatic push workflow (push=true by default)
- ✅ Cost savings ($0.15/month vs $0.45/month)
- ✅ Environment configuration
- ✅ How to inform you about GitHub URLs and cloning

**Your PM Agent is ready to intelligently manage the team with full infrastructure awareness!** 🎉

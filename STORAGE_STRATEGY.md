# Storage Strategy - GitHub-Backed Workspaces

## 💡 Smart Architecture

Instead of storing all code in expensive Fly.io volumes, we use **GitHub as permanent storage** and **ephemeral workspaces** for code generation.

---

## 📁 Storage Breakdown

### **Fly.io Volume (1GB, persistent)** - $0.15/month
```
/data/
└── database/
    └── pm_system.db (~50-100MB)
        ├── Projects
        ├── Tasks
        ├── GitHub data
        └── Conversation memory
```

**Why persistent?** Database must survive container restarts.

---

### **Container Temp Space (/tmp, ephemeral)** - FREE
```
/tmp/workspaces/
├── yohga-init/          ← Generated here
│   ├── src/
│   ├── components/
│   └── package.json
├── veggies-list/        ← Generated here
│   ├── backend/
│   └── frontend/
└── [cleared on restart]
```

**Why ephemeral?** Code is immediately pushed to GitHub, no need to persist.

---

### **GitHub Repos (unlimited, permanent)** - FREE
```
github.com/Weche/
├── yohga-init           ← Permanent storage
├── veggies-list         ← Permanent storage
└── other-projects       ← Permanent storage
```

**Why GitHub?** Unlimited storage, version control, backup, collaboration.

---

## 🔄 Workflow

### **When Dev Agent Executes a Task:**

1. **Generate code** in `/tmp/workspaces/project-name/`
2. **Git commit** with task details
3. **Git push** to GitHub repo
4. **Update task** status in database
5. **Clean up** temp workspace (optional)

### **Example:**
```
Task #29: "Build login page with React"

1. Frontend Agent creates: /tmp/workspaces/yohga-init/src/Login.tsx
2. Commits: "Task #29: Add React login page component"
3. Pushes: github.com/Weche/yohga-init
4. Updates database: Task #29 = done
5. Result: Code safe in GitHub, database updated
```

---

## 💰 Cost Comparison

| Storage Type | Size | Cost/Month | Use Case |
|--------------|------|------------|----------|
| **Fly.io Volume** | 1GB | $0.15 | Database only |
| **Container /tmp** | ~10GB | $0.00 | Temp workspaces |
| **GitHub Repos** | Unlimited | $0.00 | Permanent code |
| **Total** | Unlimited | **$0.15** | Everything! |

**Previous (3GB volume):** $0.45/month
**New (1GB + GitHub):** $0.15/month
**Savings:** $0.30/month ($3.60/year) 💰

---

## ✅ Benefits

### **1. Cost Savings**
- 66% cheaper storage ($0.15 vs $0.45/month)
- Unlimited code storage via GitHub

### **2. Better Backup**
- Every task = Git commit
- Full version history
- Can clone repos locally
- Disaster recovery built-in

### **3. Collaboration**
- You can work locally: `git clone github.com/Weche/yohga-init`
- Multiple devs can contribute
- Pull requests, code reviews

### **4. No Space Limits**
- GitHub repos: Unlimited
- Can have 100+ projects
- No "disk full" errors

### **5. Better Development**
- Full Git history per project
- Can revert to any commit
- Track progress over time

---

## 🔧 Implementation Details

### **Git Operations Already Built-In**

The Dev Agents already have `git-operations.ts`:

```typescript
// Auto-pushes to GitHub when push=true
await gitCommitAction({
  message: "Task #29: Build login page",
  push: true  // ← Pushes to GitHub!
});
```

### **Environment Variables**

Set in Fly secrets:
```bash
GITHUB_TOKEN=ghp_...          # Your GitHub token
GITHUB_USER=Weche             # Your GitHub username
WORKSPACE_DIR=/tmp/workspaces # Ephemeral workspace
```

### **Auto-Repository Creation**

When task assigned to project:
1. Check if GitHub repo exists
2. If not, create via GitHub API
3. Clone to `/tmp/workspaces/`
4. Generate code
5. Commit and push

---

## 🚀 Deployment Configuration

### **fly.toml**
```toml
[env]
  DATABASE_PATH = "/data/database/pm_system.db"
  WORKSPACE_DIR = "/tmp/workspaces"  # ← Ephemeral!

[mounts]
  source = "albedo_data"
  destination = "/data"
  initial_size = "1gb"  # ← Just database!
```

### **Dockerfile**
```dockerfile
# Create directories
RUN mkdir -p /data/database /tmp/workspaces

# /data will be mounted (persistent)
# /tmp will be ephemeral (cleared on restart)
```

---

## 🎯 Example Scenarios

### **Scenario 1: Fresh Container Start**

```
Container starts:
├── /data/database/pm_system.db (from volume, persistent)
└── /tmp/workspaces/ (empty, ephemeral)

Agent receives Task #30:
1. Clones github.com/Weche/yohga-init to /tmp/
2. Makes changes
3. Commits and pushes to GitHub
4. Workspace cleaned after push

Container restarts:
├── /data/database/pm_system.db (still there!)
└── /tmp/workspaces/ (cleared, but code is in GitHub!)
```

### **Scenario 2: You Want to Work Locally**

```bash
# Clone any project to your local machine
git clone https://github.com/Weche/yohga-init.git
cd yohga-init

# All task commits are there!
git log
# Task #29: Build login page
# Task #28: Add navigation
# Task #27: Setup project structure
```

---

## 📊 Storage Metrics

### **Database Growth:**
- Initial: ~10MB
- After 100 tasks: ~50MB
- After 1000 tasks: ~100MB
- 1GB volume = ~10,000 tasks worth of data

### **Code in GitHub:**
- Yohga project: ~50MB
- Veggies list: ~30MB
- 10 projects: ~500MB
- All FREE on GitHub!

---

## 🔒 Security

- ✅ GitHub token stored in Fly secrets (encrypted)
- ✅ Repos can be private or public
- ✅ Database encrypted at rest
- ✅ No API keys in code repositories

---

## 🎓 Summary

**Old Way (3GB volume):**
- Database + workspaces in Fly volume
- $0.45/month
- Limited to 3GB

**New Way (1GB + GitHub):**
- Database in 1GB Fly volume ($0.15/month)
- Workspaces in /tmp (FREE)
- Code in GitHub (FREE, unlimited)
- **Total: $0.15/month for unlimited projects!**

This is how modern cloud apps work - use expensive storage only for databases, use cheap/free storage (GitHub, S3) for files. 🚀

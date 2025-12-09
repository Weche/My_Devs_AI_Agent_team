# Dev Agent Service

StreamUI-based code execution agent built with Vercel AI SDK.

## Overview

This service provides a **Dev Agent** that can execute tasks by writing actual code:
- ✅ Writes HTML/CSS/JS/Python files
- ✅ Commits to Git
- ✅ Updates task status in database
- ✅ 76% faster than LangGraph (StreamUI benchmarks)
- ✅ 66% fewer tokens than Agno 2.0

## Architecture

```
Albedo (Python/Telegram)
    ↓ HTTP POST
Dev Agent Service (Node.js/StreamUI)
    ↓
[write_file, git_commit, update_task tools]
    ↓
Workspace directory + Git + SQLite DB
```

## Installation

```bash
cd dev-agent-service
npm install
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Choose AI provider (Claude recommended for code generation)
ANTHROPIC_API_KEY=sk-ant-...
# or
OPENAI_API_KEY=sk-...

# Database path (Python backend)
DATABASE_PATH=../data/database/pm_system.db

# Workspace for generated code
WORKSPACE_DIR=../workspace

# GitHub
GITHUB_TOKEN=ghp_...
GITHUB_USER=your-username
```

## Usage

### Start the service

```bash
# Development mode (with auto-reload)
npm run dev

# Production mode
npm run build
npm start
```

Service runs on http://localhost:3001

### Execute a task via API

```bash
curl -X POST http://localhost:3001/execute-task \
  -H "Content-Type: application/json" \
  -d '{"task_id": 9}'
```

### From Python (Albedo integration)

```python
import requests

response = requests.post(
    "http://localhost:3001/execute-task",
    json={"task_id": 9}
)

result = response.json()
print(result["message"])
```

## Tools Available

### 1. write_file

Writes code files to workspace.

```typescript
await write_file({
  path: "index.html",
  content: "<h1>Hello World</h1>",
  description: "Main landing page"
});
```

### 2. git_commit

Commits changes to git.

```typescript
await git_commit({
  message: "feat: Add reporting dashboard prototype",
  files: ["index.html", "styles.css"],
  push: false
});
```

### 3. update_task

Updates task status in database.

```typescript
await update_task({
  task_id: 9,
  status: "review",
  progress_note: "Created HTML/CSS prototype"
});
```

## How It Works

1. Albedo (PM Agent) assigns task to Dev Agent
2. Python backend sends HTTP POST to `/execute-task`
3. Dev Agent:
   - Reads task from SQLite database
   - Sets status to `in_progress`
   - Uses StreamUI with Claude/GPT to generate code
   - Calls tools (write_file, git_commit, update_task)
   - Returns results
4. Python backend receives completion notification
5. Albedo notifies Christian on Telegram

## Example Execution

```
🤖 Dev Agent executing Task #9: Base Prototype Deployment
   Project: Reporting Analytics Dashboards
   Description: Create HTML/CSS/JS prototype for reporting

  → write_file: { path: "index.html", content: "..." }
  ✓ Created index.html (45 lines written)

  → write_file: { path: "styles.css", content: "..." }
  ✓ Created styles.css (120 lines written)

  → git_commit: { message: "feat: Add reporting dashboard prototype" }
  ✓ Committed: "feat: Add reporting dashboard prototype"
    Files changed: 2
    Insertions: +165
    Deletions: -0

  → update_task: { task_id: 9, status: "review" }
  ✓ Task #9 → review

✓ Task #9 completed by Dev Agent
```

## Performance

Based on StreamUI benchmarks:

| Metric | StreamUI | LangGraph | Improvement |
|--------|----------|-----------|-------------|
| Latency | 2.39s | 4.30s | **76% faster** |
| Tokens | 1,591 | 5,340 | **66% fewer** |
| Cost | Lowest | 3.5x more | **3.5x cheaper** |

## Integration with Albedo

Albedo can assign tasks via conversation:

```
Christian: "Albedo, have the dev agent work on Task #9"

Albedo: "Yes, Master! I'm assigning Task #9 to the Dev Agent now..."
        [Calls /execute-task endpoint]
        "Dev Agent has started working on the Reporting Analytics prototype!"

[5 minutes later]

Albedo: "Master, Dev Agent has completed Task #9!
        Created: index.html, styles.css, app.js
        Committed to GitHub
        Ready for your review ✨"
```

## Development

### File Structure

```
dev-agent-service/
├── src/
│   ├── index.ts          # Express server
│   ├── agent.ts          # StreamUI Dev Agent
│   ├── types.ts          # TypeScript types
│   └── tools/
│       ├── file-writer.ts
│       ├── git-operations.ts
│       └── task-updater.ts
├── package.json
├── tsconfig.json
└── README.md
```

### Adding New Tools

```typescript
// src/tools/my-tool.ts
export const myToolSchema = z.object({
  param: z.string().describe('Parameter description'),
});

export async function myToolAction(params) {
  // Tool implementation
  return "Tool result";
}

// src/agent.ts
import { myToolSchema, myToolAction } from './tools/my-tool.js';

tools: {
  my_tool: tool({
    description: 'My tool description',
    parameters: myToolSchema,
    execute: myToolAction,
  }),
}
```

## Troubleshooting

### "Module not found" errors

Ensure you're using ESM:
- `"type": "module"` in package.json
- `.js` extensions in imports
- `tsx` for development

### Database connection failed

Check `DATABASE_PATH` points to correct SQLite file:
```bash
ls ../data/database/pm_system.db
```

### Git operations fail

Ensure workspace is initialized:
```bash
cd ../workspace
git init
```

## License

MIT

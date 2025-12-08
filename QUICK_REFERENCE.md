# Quick Reference Card

One-page reference for the most common commands.

## Activation
```bash
cd "C:\Users\Christian Orquera\My_Devs_AI_Agent_team"
venv\Scripts\activate
```

## PM Agent (Task Management)

```bash
# Status update (calls OpenAI - $0.00015)
python -m src.cli.main status "Example Project"

# List tasks
python -m src.cli.main tasks "Example Project"
python -m src.cli.main tasks "Example Project" --status todo

# Create task
python -m src.cli.main create "Example Project" "Task title" -p high

# Warnings
python -m src.cli.main warnings "Example Project"
```

## Lead Dev Agent (Technical Guidance)

```bash
# Ask for advice (calls OpenAI - $0.00021)
python -m src.cli.main ask-dev "Example Project" "Your technical question?"

# Architecture review (calls OpenAI - $0.00027)
python -m src.cli.main review-arch "Example Project" "Feature to implement"

# Track decision (FREE - no API call)
python -m src.cli.main track-decision "Example Project" "Decision made" "Reasoning"

# View context (FREE)
python -m src.cli.main dev-context "Example Project"
```

## General

```bash
# List projects
python -m src.cli.main projects

# View costs
python -m src.cli.main costs today
python -m src.cli.main costs month

# Help
python -m src.cli.main --help
```

## Daily Routine

```bash
# 1. Check projects
python -m src.cli.main projects

# 2. Get status
python -m src.cli.main status "Your Project"

# 3. Check warnings
python -m src.cli.main warnings "Your Project"

# 4. Review costs
python -m src.cli.main costs today
```

## When to Use Which Agent

**PM Agent** - Use for:
- Task creation and updates
- Project status
- Blockers and warnings
- Day-to-day management

**Lead Dev Agent** - Use for:
- Technical questions
- Architecture decisions
- Implementation guidance
- Technical documentation

## Files Created

```
data/
├── database/
│   └── pm_system.db                    # SQLite database
├── agent_context/
│   ├── pm_agent/{project}/{date}.json  # PM conversations
│   └── lead_technical_dev/{project}/{date}.json  # Lead Dev conversations
└── logs/
    └── costs/{date}.json               # Daily cost logs
```

## Cost Reference

| Command | Cost | When |
|---------|------|------|
| `status` | $0.00015 | Every status check |
| `ask-dev` | $0.00021 | Technical questions |
| `review-arch` | $0.00027 | Architecture reviews |
| Everything else | FREE | Always |

**Daily budget:** ~$0.002 (20 commands)
**Monthly budget:** ~$0.06

## Quick Links

- Full Commands: [COMMANDS.md](COMMANDS.md)
- Lead Dev Guide: [LEAD_DEV.md](LEAD_DEV.md)
- Examples: [EXAMPLES.md](EXAMPLES.md)
- Setup: [SETUP.md](SETUP.md)

---

**Save this file for quick reference!** Print it or keep it open while working.

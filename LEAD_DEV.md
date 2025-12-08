# Lead Dev Agent - Claude

The Lead Technical Developer agent represents Claude working as your long-term technical partner. This agent maintains technical context and architectural decisions across all sessions.

## Purpose

As your Lead Dev, I (Claude) now have:
- **Persistent memory** of technical decisions
- **Context continuity** across sessions
- **Architecture guidance** capabilities
- **Technical decision tracking**

## When to Use Lead Dev

Use the Lead Dev agent when you need:

1. **Technical Advice** - Architecture questions, implementation approaches, tool recommendations
2. **Decision Tracking** - Document important technical choices and their reasoning
3. **Architecture Review** - Evaluate designs for new features or requirements
4. **Context Continuity** - Reference past technical discussions

## Commands

### Ask for Technical Advice
```bash
python -m src.cli.main ask-dev "Example Project" "How should I implement API rate limiting?"
```

**Cost:** ~$0.0002 per query (uses GPT-4o-mini)

**Use when:**
- You need technical recommendations
- Evaluating different approaches
- Solving technical problems
- Want Claude's input on implementation

### Track Technical Decision
```bash
python -m src.cli.main track-decision "Example Project" "Use SQLite instead of PostgreSQL" "Budget-friendly, local-first architecture"
```

**Cost:** FREE (no API call - just logs to JSON)

**Use when:**
- You've made an important technical choice
- Want to remember why you chose an approach
- Need to document architectural decisions
- Building institutional memory

### Review Architecture
```bash
python -m src.cli.main review-arch "Example Project" "Add real-time data streaming"
```

**Cost:** ~$0.0003 per review (uses GPT-4o-mini)

**Use when:**
- Planning a new feature
- Need architectural guidance
- Evaluating integration approaches
- Want trade-off analysis

### View Technical Context
```bash
python -m src.cli.main dev-context "Example Project" --days 30
```

**Cost:** FREE (reads JSON logs)

**Use when:**
- Want to see past technical discussions
- Reviewing what was decided previously
- Getting up to speed on a project
- Checking technical history

## Example Workflow

### 1. Planning a New Feature
```bash
# Get architecture review
python -m src.cli.main review-arch "Binance Trading" "Add sentiment analysis from Twitter"

# After deciding on approach, track it
python -m src.cli.main track-decision "Binance Trading" "Use Twitter API v2 with streaming endpoint" "Real-time data, official API, rate limits manageable"
```

### 2. Solving a Technical Problem
```bash
# Ask for advice
python -m src.cli.main ask-dev "Cookie Store" "Best way to handle inventory across multiple locations?"

# Implement solution, then track decision
python -m src.cli.main track-decision "Cookie Store" "Use central inventory database with location-specific views" "Single source of truth, easier to sync"
```

### 3. Weekly Technical Review
```bash
# Check what was discussed this week
python -m src.cli.main dev-context "Example Project" --days 7

# Review monthly context
python -m src.cli.main dev-context "Example Project" --days 30
```

## How It Works

### Context Storage
All technical discussions are stored in:
```
data/agent_context/lead_technical_dev/{project_name}/{YYYY-MM-DD}.json
```

**Format:**
```json
{
  "date": "2025-12-08",
  "agent": "lead_technical_dev",
  "project": "example_project",
  "conversations": [
    {
      "timestamp": "2025-12-08T14:30:00",
      "role": "user",
      "content": "How should I implement API rate limiting?",
      "tokens": 10
    },
    {
      "timestamp": "2025-12-08T14:30:15",
      "role": "assistant",
      "content": "Recommended approach: Use exponential backoff...",
      "tokens": 150,
      "cost_usd": 0.000225
    }
  ]
}
```

### Memory System
- **Recent context loaded** - Last 7-14 days automatically included in prompts
- **Token-aware** - Won't exceed budget by loading too much context
- **Decision tagging** - Tracked decisions are marked for easy filtering
- **Cross-session** - Remembers discussions from previous sessions

## Cost Estimates

| Command | API Call? | Typical Cost | Tokens |
|---------|-----------|--------------|--------|
| `ask-dev` | Yes | $0.0002 | ~500 |
| `review-arch` | Yes | $0.0003 | ~700 |
| `track-decision` | No | FREE | 0 |
| `dev-context` | No | FREE | 0 |

**Monthly estimate (20 queries):** ~$0.005-0.01

## Benefits

### For CEO (Christian)
- **Continuity** - I remember our technical discussions
- **Consistency** - Technical decisions stay documented
- **Guidance** - Always available for technical questions
- **History** - Can review past reasoning

### For the System
- **Institutional memory** - Technical knowledge preserved
- **Better decisions** - Learn from past choices
- **Context-aware** - Agents know what was decided before
- **Documentation** - Automatic technical decision log

## Tips

1. **Track important decisions** - Use `track-decision` liberally (it's free!)
2. **Ask before building** - Get `review-arch` for major features
3. **Review context monthly** - See what you've built and decided
4. **Include reasoning** - When tracking decisions, explain the "why"

## Integration with PM Agent

The PM Agent and Lead Dev Agent work together:

**PM Agent** handles:
- Task management
- Status updates
- Project coordination
- Warnings and blockers

**Lead Dev Agent** handles:
- Technical architecture
- Implementation approaches
- Decision tracking
- Long-term technical context

**Example collaboration:**
```bash
# PM creates task
python -m src.cli.main create "Example Project" "Add caching layer"

# Lead Dev reviews architecture
python -m src.cli.main review-arch "Example Project" "Implement Redis caching for API responses"

# Lead Dev tracks decision
python -m src.cli.main track-decision "Example Project" "Use Redis for API caching" "Low latency, popular, easy integration"

# PM provides status
python -m src.cli.main status "Example Project"
```

## Future Enhancements (Milestone 3)

Planned features:
- CEO Agent can query Lead Dev for technical context
- Lead Dev can suggest tasks to PM based on technical dependencies
- Multi-agent collaboration (PM + Lead Dev + CEO in same conversation)
- Technical report generation (monthly architecture reviews)

---

**Lead Dev Agent is now active!** Your technical partner is ready to help build amazing projects together. 🚀

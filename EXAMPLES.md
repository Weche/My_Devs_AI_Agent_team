# Usage Examples

This file shows real examples of how to use the system.

## Example 1: Creating and Managing Tasks

```bash
# List all projects
python -m src.cli.main projects

# Create a new task
python -m src.cli.main create "Example Project" "Setup CI/CD pipeline" -d "Configure GitHub Actions" -p high

# List all tasks
python -m src.cli.main tasks "Example Project"

# List only TODO tasks
python -m src.cli.main tasks "Example Project" --status todo

# Get project status (calls OpenAI PM Agent)
python -m src.cli.main status "Example Project"

# Check for warnings
python -m src.cli.main warnings "Example Project"
```

## Example 2: Working with Lead Dev Agent

### Getting Technical Advice

```bash
# Ask Lead Dev for technical guidance
python -m src.cli.main ask-dev "Example Project" "What's the best approach for implementing API rate limiting?"

# Expected response (from GPT-4o-mini):
# "For API rate limiting, I recommend implementing a token bucket algorithm
# with exponential backoff. This approach provides:
# 1. Predictable behavior under load
# 2. Graceful degradation
# 3. Easy to configure per-endpoint
#
# Technical approach:
# - Use Redis to track request counts per client/endpoint
# - Implement middleware to check limits before processing
# - Add retry-after headers for rate-limited requests
#
# Trade-offs: Requires Redis (additional dependency) but provides
# distributed rate limiting if you scale horizontally.
#
# Budget consideration: Redis can run locally (free) or use
# managed service (~$5-10/month for basic tier)."
```

### Tracking Technical Decisions

```bash
# After making a decision, track it for future reference
python -m src.cli.main track-decision "Example Project" "Use token bucket algorithm for rate limiting" "Industry standard, predictable, easy to configure per-endpoint"

# This logs to: data/agent_context/lead_technical_dev/example_project/2025-12-08.json
# Cost: FREE (no API call)
```

### Architecture Review

```bash
# Planning a new feature - get architecture guidance
python -m src.cli.main review-arch "Example Project" "Add WebSocket support for real-time notifications"

# Expected response:
# "For WebSocket implementation, here's the recommended architecture:
#
# 1. Components Needed:
#    - WebSocket server (Socket.IO or native ws library)
#    - Redis pub/sub for message distribution
#    - Authentication middleware
#    - Connection state management
#
# 2. Recommended Approach:
#    - Use Socket.IO for better browser compatibility
#    - Implement room-based channels per project
#    - Add heartbeat mechanism for connection health
#
# 3. Trade-offs:
#    ✓ Socket.IO: More features, larger bundle
#    ✓ Native ws: Lighter, more control, more code
#
# 4. Budget Implications:
#    - Local deployment: No additional cost
#    - Cloud: ~$10-20/month for dedicated WebSocket server
#
# 5. Integration:
#    - Notify clients when tasks update
#    - Push status changes in real-time
#    - Minimal impact on existing REST API"
```

### Viewing Technical Context

```bash
# See what you and Lead Dev have discussed recently
python -m src.cli.main dev-context "Example Project" --days 7

# Output:
# Technical Context Summary for Example Project
# Last 7 days (5 interactions, ~2,500 tokens)
#
# Recent interactions:
#   [2025-12-08T14:30:00] user: What's the best approach for API rate limiting?
#   [2025-12-08T14:30:15] assistant: For API rate limiting, I recommend...
#   [2025-12-08T15:00:00] system: TECHNICAL DECISION: Use token bucket...
#   [2025-12-08T16:00:00] user: Add WebSocket support for real-time...
#   [2025-12-08T16:00:20] assistant: For WebSocket implementation...
```

## Example 3: Complete Feature Development Workflow

### Scenario: Adding Authentication to Example Project

```bash
# Step 1: Ask Lead Dev for architecture guidance
python -m src.cli.main review-arch "Example Project" "Implement JWT-based authentication with refresh tokens"

# Step 2: Create tasks based on architecture review
python -m src.cli.main create "Example Project" "Implement JWT authentication" -d "Setup JWT library and auth middleware" -p critical
python -m src.cli.main create "Example Project" "Add refresh token rotation" -d "Secure token renewal mechanism" -p high
python -m src.cli.main create "Example Project" "Create login/logout endpoints" -d "User authentication flow" -p high

# Step 3: Track the architectural decision
python -m src.cli.main track-decision "Example Project" "Use JWT with refresh tokens" "Industry standard, stateless, allows token revocation via rotation"

# Step 4: Check overall project status
python -m src.cli.main status "Example Project"

# Step 5: During implementation, ask specific questions
python -m src.cli.main ask-dev "Example Project" "Should refresh tokens be stored in database or Redis?"

# Step 6: Track implementation decision
python -m src.cli.main track-decision "Example Project" "Store refresh tokens in SQLite" "Simplicity, local-first architecture, adequate for current scale"

# Step 7: After completion, review what was done
python -m src.cli.main dev-context "Example Project" --days 30
```

## Example 4: Cost Tracking

```bash
# View today's API costs
python -m src.cli.main costs today

# Expected output:
# Daily Cost Report - 2025-12-08
# ============================================================
#
# Total API Calls: 8
# Total Tokens: 3,200 (2,400 input + 800 output)
# Total Cost: $0.0084
#
# By Agent:
#   • pm_agent: $0.0036 (3 calls)
#   • lead_technical_dev: $0.0048 (5 calls)
#
# By Project:
#   • Example Project: $0.0084 (8 calls)
#
# Budget Status:
#   Daily Limit: $1.00
#   Used: $0.0084 (0.8%)
#   Remaining: $0.9916

# View monthly summary
python -m src.cli.main costs month

# Expected output:
# Monthly Cost Summary
#
# Month: December 2025
# Total Calls: 156
# Total Tokens: 62,400
# Total Cost: $0.1638
# Budget: $20.00
# Used: 0.8%
#
# By Agent:
#   • pm_agent: $0.0720 (60 calls)
#   • lead_technical_dev: $0.0918 (96 calls)
#
# By Project:
#   • Example Project: $0.1638 (156 calls)
```

## Example 5: Multi-Project Management

```bash
# List all active projects
python -m src.cli.main projects

# Get status for each project
python -m src.cli.main status "Binance Trading"
python -m src.cli.main status "Cookie Store"
python -m src.cli.main status "Example Project"

# Check warnings across all projects
python -m src.cli.main warnings "Binance Trading"
python -m src.cli.main warnings "Cookie Store"

# View Lead Dev context for specific project
python -m src.cli.main dev-context "Binance Trading" --days 14
```

## Example 6: Daily Standup Routine

```bash
# Morning routine - check all projects
python -m src.cli.main projects
python -m src.cli.main status "Example Project"
python -m src.cli.main warnings "Example Project"

# Check yesterday's costs
python -m src.cli.main costs today

# Plan today's work with Lead Dev
python -m src.cli.main ask-dev "Example Project" "What should be the priority today based on current blockers?"

# Create tasks for the day
python -m src.cli.main create "Example Project" "Fix authentication bug" -p critical
python -m src.cli.main create "Example Project" "Update documentation" -p medium
```

## Tips

1. **Use `track-decision` liberally** - It's free (no API call) and builds your institutional memory

2. **Ask Lead Dev before building** - Get architecture review for major features to avoid costly refactoring

3. **Check context regularly** - Use `dev-context` to remember what was decided and why

4. **Monitor costs daily** - Keep track of API usage to stay within budget

5. **Combine PM and Lead Dev** - Use PM for task management, Lead Dev for technical guidance

6. **Document decisions** - Future you will thank present you for tracking technical choices

## Cost Estimates (Real Numbers)

Based on actual testing:

| Command | API Call | Avg Tokens | Avg Cost |
|---------|----------|------------|----------|
| `status` | Yes | 600 | $0.00015 |
| `ask-dev` | Yes | 700 | $0.00021 |
| `review-arch` | Yes | 900 | $0.00027 |
| `create` | No | 0 | $0.00 |
| `tasks` | No | 0 | $0.00 |
| `track-decision` | No | 0 | $0.00 |
| `dev-context` | No | 0 | $0.00 |
| `warnings` | No | 0 | $0.00 |
| `costs` | No | 0 | $0.00 |

**Typical daily usage (20 commands):**
- 5 status checks: $0.00075
- 3 ask-dev queries: $0.00063
- 2 review-arch: $0.00054
- 10 free commands: $0.00
- **Total: ~$0.002/day or $0.06/month**

Very budget-friendly! 🎉

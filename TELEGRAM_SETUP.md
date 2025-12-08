# Telegram Bot Setup - Milestone 2

Complete guide to setting up and using the Telegram bot for mobile project management.

## Prerequisites

- Telegram account
- Telegram bot token (from @BotFather)
- Your Telegram user ID (for security)
- Python environment with dependencies installed

## Step 1: Create Your Telegram Bot

### 1.1 Talk to @BotFather

1. Open Telegram and search for `@BotFather`
2. Start a conversation: `/start`
3. Create a new bot: `/newbot`
4. Choose a name for your bot (e.g., "My Devs PM Bot")
5. Choose a username (must end in 'bot', e.g., "mydevs_pm_bot")
6. **BotFather will give you a token** - SAVE THIS!

Example token: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### 1.2 Get Your Telegram User ID

1. Search for `@userinfobot` on Telegram
2. Start a conversation: `/start`
3. The bot will show your user ID (e.g., `123456789`)
4. **Save this number** - this is your authorization ID

## Step 2: Configure Environment

### 2.1 Add Credentials to .env

Edit your `.env` file and add:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_USER_ID=123456789
```

**Important:**
- Replace with your actual bot token from @BotFather
- Replace with your actual user ID from @userinfobot
- Multiple users: Separate IDs with commas: `123,456,789`

### 2.2 Verify .env File

Your complete `.env` should look like:

```env
# OpenAI API (for PM Agent)
OPENAI_API_KEY=sk-your-key-here

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-bot-token-here
TELEGRAM_USER_ID=your-user-id-here

# Database
DATABASE_URL=sqlite:///data/database/pm_system.db

# Cost tracking
DAILY_BUDGET_ALERT=1.00
MONTHLY_BUDGET_LIMIT=20.00
```

## Step 3: Start the Bot

### 3.1 Activate Virtual Environment

```bash
cd "C:\Users\Christian Orquera\My_Devs_AI_Agent_team"
venv\Scripts\activate
```

### 3.2 Run the Bot

```bash
python src/telegram/bot.py
```

You should see:

```
INFO - Starting My Devs AI Agent Team bot...
INFO - Authorized users: [123456789]
INFO - Bot started! Send /start to begin.
INFO - Press Ctrl+C to stop the bot
```

### 3.3 Test the Bot

1. Open Telegram
2. Search for your bot (username you chose)
3. Start a conversation
4. Send: `/start`

You should receive a welcome message with all available commands!

## Available Commands

### Project Management

#### /projects
List all active projects.

Example:
```
/projects
```

Response:
```
Active Projects:

- Example Project (Priority: 5)
- Yohga - init (Priority: 6)
- Veggies list (Priority: 5)
- Reporting Analytics Dashboards (Priority: 7)
```

#### /status <project>
Get current status of a project (calls PM Agent).

Example:
```
/status Example Project
```

Response:
```
Status: Example Project

Overall Progress: 4/6 tasks completed (67%)

Critical Issues:
- None

Next Actions:
1. Write documentation
2. Add cost tracking visualization
3. Test PM Agent with real project
```

#### /tasks <project>
List all tasks for a project.

Example:
```
/tasks Yohga - init
```

Response:
```
Tasks: Yohga - init

[TODO] #7 Define project requirements
[TODO] #8 Setup development environment [!]
[IN PROGRESS] #9 Research architecture options
```

#### /create <project> <title>
Create a new task.

Examples:
```
/create "Example Project" Fix authentication bug
/create "Yohga - init" Setup database schema
```

Use quotes if project name has spaces!

#### /warnings <project>
Show warnings (overdue tasks, blockers, etc.).

Example:
```
/warnings Example Project
```

### Cost Tracking

#### /costs
View today's API usage and costs.

Example:
```
/costs
```

Response:
```
Today's Costs

Total Calls: 5
Total Tokens: 2,400
Total Cost: $0.0036

By Agent:
- pm_agent: $0.0036

Budget: 0.4% of $1.00
```

### Help

#### /help
Show all available commands.

```
/help
```

## Usage Examples

### Morning Standup

```
/projects
/status Example Project
/status "Yohga - init"
/warnings Example Project
/costs
```

### Create Tasks on the Go

```
/create "Veggies list" Research inventory management solutions
/create "Reporting Analytics Dashboards" Define key metrics
/create Example Project Update documentation
```

### Check Task Progress

```
/tasks Example Project
/tasks "Yohga - init"
/tasks "Veggies list"
```

## Security Features

### Authorization

- Only users with IDs in `TELEGRAM_USER_ID` can use the bot
- Unauthorized users get "Unauthorized" message
- Add multiple users: `TELEGRAM_USER_ID=123,456,789`

### Best Practices

1. **Never share your bot token** - treat it like a password
2. **Keep your .env file private** - it's in .gitignore
3. **Regenerate token if compromised** - use @BotFather's `/token` command
4. **Add only trusted users** - verify their Telegram IDs

## Troubleshooting

### Bot doesn't respond

**Check:**
1. Is the bot running? (python src/telegram/bot.py)
2. Is your user ID in .env?
3. Did you start the conversation with /start?

**Solution:**
```bash
# Restart the bot
Ctrl+C
python src/telegram/bot.py
```

### "Unauthorized" message

**Problem:** Your Telegram user ID is not in .env

**Solution:**
1. Get your ID from @userinfobot
2. Add to .env: `TELEGRAM_USER_ID=your-id-here`
3. Restart bot

### Bot token error

**Problem:** Invalid or missing bot token

**Solution:**
1. Check .env has `TELEGRAM_BOT_TOKEN=...`
2. Verify token from @BotFather (use /token command)
3. No spaces or quotes around token

### API errors in /status

**Problem:** OpenAI API key missing or invalid

**Solution:**
1. Check .env has `OPENAI_API_KEY=sk-...`
2. Verify key is valid
3. Check internet connection

## Running Bot 24/7

### Option 1: Keep Terminal Open (Simple)

```bash
# Run in dedicated terminal
venv\Scripts\activate
python src/telegram/bot.py

# Leave terminal open
```

**Pros:** Simple, immediate
**Cons:** Stops when PC sleeps/restarts

### Option 2: Windows Service (Advanced)

Use NSSM (Non-Sucking Service Manager):

```bash
# Install NSSM
choco install nssm

# Create service
nssm install TelegramPMBot "C:\...\venv\Scripts\python.exe" "C:\...\src\telegram\bot.py"
nssm start TelegramPMBot
```

**Pros:** Runs automatically on startup
**Cons:** More complex setup

### Option 3: Cloud Deployment (Future)

Deploy to free tier cloud service:
- Railway.app
- Render.com
- Heroku

**Pros:** Always running, no PC needed
**Cons:** Requires cloud setup (Milestone 3)

## Cost Estimates

Based on typical usage:

| Command | API Call? | Avg Cost |
|---------|-----------|----------|
| /projects | No | FREE |
| /tasks | No | FREE |
| /create | No | FREE |
| /costs | No | FREE |
| /status | Yes | $0.00015 |
| /warnings | No | FREE |

**Daily estimate (20 commands):**
- 15 free commands: $0.00
- 5 status checks: $0.00075
- **Total: ~$0.001/day or $0.03/month**

Very affordable! 🎉

## Next Steps

1. ✅ Set up bot token and user ID
2. ✅ Start bot: `python src/telegram/bot.py`
3. ✅ Send /start to your bot
4. ✅ Try /projects
5. ✅ Try /status "Example Project"
6. ✅ Create tasks from your phone!

## Advanced Features (Optional)

### Custom Bot Commands

Edit `src/telegram/handlers.py` to add new commands.

Example:
```python
async def custom_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Your custom logic
    await update.message.reply_text("Custom response")

# Register in bot.py:
application.add_handler(CommandHandler("custom", custom_handler))
```

### Notifications (Future)

Add proactive notifications:
- Daily standup reminders
- Overdue task alerts
- Budget warnings

Will implement in Milestone 3!

---

**Telegram Bot is ready!** You can now manage your projects from anywhere. 📱🚀

Need help? Check [COMMANDS.md](COMMANDS.md) for CLI commands or [LEAD_DEV.md](LEAD_DEV.md) for technical guidance.

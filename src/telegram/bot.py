"""Telegram bot main file"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from src.telegram.handlers import (
    start_handler,
    help_handler,
    status_handler,
    tasks_handler,
    create_handler,
    warnings_handler,
    projects_handler,
    costs_handler,
    message_handler,
)
from src.telegram.scheduler import setup_scheduler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    """Start the Telegram bot"""
    # Get bot token from environment
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in .env file!")
        logger.error("Please add your bot token to .env")
        logger.error("Get a token from @BotFather on Telegram")
        sys.exit(1)

    # Get authorized user IDs
    authorized_users_str = os.getenv("TELEGRAM_USER_ID", "")
    authorized_users = [
        int(uid.strip()) for uid in authorized_users_str.split(",") if uid.strip()
    ]

    if not authorized_users:
        logger.warning("No TELEGRAM_USER_ID set in .env - bot will respond to anyone!")
        logger.warning("Add your Telegram user ID to .env for security")

    logger.info("Starting My Devs AI Agent Team bot...")
    logger.info(f"Authorized users: {authorized_users if authorized_users else 'ALL (not secure!)'}")

    # Create application
    application = Application.builder().token(token).build()

    # Store authorized users in bot_data for handlers to access
    application.bot_data["authorized_users"] = authorized_users

    # Register command handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("status", status_handler))
    application.add_handler(CommandHandler("tasks", tasks_handler))
    application.add_handler(CommandHandler("create", create_handler))
    application.add_handler(CommandHandler("warnings", warnings_handler))
    application.add_handler(CommandHandler("projects", projects_handler))
    application.add_handler(CommandHandler("costs", costs_handler))

    # Register message handler for natural language (must be last)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Setup proactive updates scheduler (deferred to post_init)
    async def post_init(application: Application) -> None:
        """Initialize scheduler after event loop is running"""
        if authorized_users:
            scheduler = setup_scheduler(application.bot, authorized_users[0])
            application.bot_data["scheduler"] = scheduler
            logger.info("Proactive updates scheduler started")
            logger.info("Daily standup: 9:00 AM Santiago time")
            logger.info("Weekly review: Mondays 9:00 AM Santiago time")
            logger.info("Due task reminders: Every hour")
            logger.info("GitHub updates: Every 30 minutes")

    application.post_init = post_init

    # Start bot
    logger.info("Bot started! Send /start to begin.")
    logger.info("Press Ctrl+C to stop the bot")

    # Run the bot until Ctrl+C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

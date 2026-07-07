# config.py
# Bot Configuration

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use environment variable for API token (NEVER hardcode in production)
API_TOKEN = os.getenv("BOT_API_TOKEN", "YOUR_TOKEN_HERE")

# Admin IDs - can also be stored in environment
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "5662658550").split(",")]

# Mock test settings
MOCK_TOTAL_QUESTIONS = 20
MOCK_TIME_PER_QUESTION = 60  # seconds

# Daily question settings
DAILY_QUESTIONS_COUNT = 3

# Database name
DB_NAME = "sat_bot.db"

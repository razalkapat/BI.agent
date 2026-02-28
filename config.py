import os
from dotenv import load_dotenv

load_dotenv()

MONDAY_API_KEY = os.getenv("MONDAY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WORK_ORDERS_BOARD_ID = os.getenv("WORK_ORDERS_BOARD_ID")
DEALS_BOARD_ID = os.getenv("DEALS_BOARD_ID")

# Validate all keys are present
def validate_config():
    missing = []
    if not MONDAY_API_KEY:
        missing.append("MONDAY_API_KEY")
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEy")
    if not WORK_ORDERS_BOARD_ID:
        missing.append("WORK_ORDERS_BOARD_ID")
    if not DEALS_BOARD_ID:
        missing.append("DEALS_BOARD_ID")
    return missing
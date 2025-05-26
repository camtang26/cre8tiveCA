import os
from dotenv import load_dotenv
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent # This should point to cal_com_mcp_server directory
ENV_FILE_PATH = BASE_DIR / '.env'

# Load environment variables from .env file
load_dotenv(dotenv_path=ENV_FILE_PATH) # For local development, Render will use its own env var system

CAL_COM_API_KEY = os.getenv("CAL_COM_API_KEY")
CAL_COM_API_BASE_URL = os.getenv("CAL_COM_API_BASE_URL", "https://api.cal.com/v2")
DEFAULT_EVENT_TYPE_ID_STR = os.getenv("DEFAULT_EVENT_TYPE_ID", "1837761")
DEFAULT_EVENT_DURATION_MINUTES_STR = os.getenv("DEFAULT_EVENT_DURATION_MINUTES", "30")

try:
    DEFAULT_EVENT_TYPE_ID = int(DEFAULT_EVENT_TYPE_ID_STR)
except ValueError:
    print(f"CRITICAL: Invalid DEFAULT_EVENT_TYPE_ID value: {DEFAULT_EVENT_TYPE_ID_STR}. Must be an integer.")
    DEFAULT_EVENT_TYPE_ID = 1837761 # Fallback to a known default

try:
    DEFAULT_EVENT_DURATION_MINUTES = int(DEFAULT_EVENT_DURATION_MINUTES_STR)
except ValueError:
    print(f"CRITICAL: Invalid DEFAULT_EVENT_DURATION_MINUTES value: {DEFAULT_EVENT_DURATION_MINUTES_STR}. Must be an integer.")
    DEFAULT_EVENT_DURATION_MINUTES = 30 # Fallback to a known default

# It's good practice to validate that critical config is loaded
if not CAL_COM_API_KEY:
    # In a real app, you might raise an error or log a critical warning
    print("CRITICAL: CAL_COM_API_KEY is not set in environment variables or .env file.")
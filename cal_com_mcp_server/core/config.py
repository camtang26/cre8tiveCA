import os
from dotenv import load_dotenv
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent # This should point to cal_com_mcp_server directory
ENV_FILE_PATH = BASE_DIR / '.env'

# Load environment variables from .env file
load_dotenv(dotenv_path=ENV_FILE_PATH)

CAL_COM_API_KEY = os.getenv("CAL_COM_API_KEY")
CAL_COM_API_BASE_URL = "https://api.cal.com/v2"
DEFAULT_EVENT_TYPE_ID = 1837761
DEFAULT_EVENT_DURATION_MINUTES = 30

# It's good practice to validate that critical config is loaded
if not CAL_COM_API_KEY:
    # In a real app, you might raise an error or log a critical warning
    print("CRITICAL: CAL_COM_API_KEY is not set in environment variables or .env file.")
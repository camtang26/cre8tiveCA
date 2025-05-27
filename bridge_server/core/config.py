import os
from dotenv import load_dotenv
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE_PATH = BASE_DIR / '.env'

load_dotenv(dotenv_path=ENV_FILE_PATH)

# MCP Server URLs (for MCP protocol approach)
CAL_COM_MCP_SERVER_URL = os.getenv("CAL_COM_MCP_SERVER_URL")
OUTLOOK_MCP_SERVER_URL = os.getenv("OUTLOOK_MCP_SERVER_URL")

# Direct API Credentials (for direct integration approach)
# Cal.com API
CAL_COM_API_KEY = os.getenv("CAL_COM_API_KEY")
CAL_COM_API_BASE_URL = os.getenv("CAL_COM_API_BASE_URL", "https://api.cal.com/v2")
DEFAULT_EVENT_TYPE_ID = int(os.getenv("DEFAULT_EVENT_TYPE_ID", "1837761"))
DEFAULT_EVENT_DURATION_MINUTES = int(os.getenv("DEFAULT_EVENT_DURATION_MINUTES", "30"))

# Microsoft Graph API (Outlook)
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
SENDER_UPN = os.getenv("SENDER_UPN")

# Integration mode: "mcp" or "direct"
INTEGRATION_MODE = os.getenv("INTEGRATION_MODE", "direct")

# Default to localhost if not set, useful for local dev
if INTEGRATION_MODE == "mcp":
    if not CAL_COM_MCP_SERVER_URL:
        CAL_COM_MCP_SERVER_URL = "http://localhost:8001/mcp"
        print(f"Warning: CAL_COM_MCP_SERVER_URL not set in .env, defaulting to {CAL_COM_MCP_SERVER_URL}")

    if not OUTLOOK_MCP_SERVER_URL:
        OUTLOOK_MCP_SERVER_URL = "http://localhost:8002/mcp"
        print(f"Warning: OUTLOOK_MCP_SERVER_URL not set in .env, defaulting to {OUTLOOK_MCP_SERVER_URL}")
else:
    # Direct mode - check for required credentials
    if not CAL_COM_API_KEY:
        print("Warning: CAL_COM_API_KEY not set in .env (required for direct mode)")
    
    if not all([AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, SENDER_UPN]):
        print("Warning: Missing Azure/Outlook credentials in .env (required for direct mode)")
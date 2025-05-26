import os
from dotenv import load_dotenv
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent # This should point to outlook_mcp_server directory
ENV_FILE_PATH = BASE_DIR / '.env'

# Load environment variables from .env file
load_dotenv(dotenv_path=ENV_FILE_PATH)

# Azure AD App Registration Details for Microsoft Graph API
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
SENDER_UPN = os.getenv("SENDER_UPN") # User Principal Name of the sender

GRAPH_API_BASE_URL = "https://graph.microsoft.com/v1.0"
GRAPH_API_SCOPES = ["https://graph.microsoft.com/.default"] # For client credentials flow

# Validate critical config
critical_configs = {
    "AZURE_TENANT_ID": AZURE_TENANT_ID,
    "AZURE_CLIENT_ID": AZURE_CLIENT_ID,
    "AZURE_CLIENT_SECRET": AZURE_CLIENT_SECRET,
    "SENDER_UPN": SENDER_UPN,
}

for key, value in critical_configs.items():
    if not value:
        print(f"CRITICAL: {key} is not set in environment variables or .env file for Outlook MCP Server.")
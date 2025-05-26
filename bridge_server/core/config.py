import os
from dotenv import load_dotenv
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE_PATH = BASE_DIR / '.env'

load_dotenv(dotenv_path=ENV_FILE_PATH)

CAL_COM_MCP_SERVER_URL = os.getenv("CAL_COM_MCP_SERVER_URL")
OUTLOOK_MCP_SERVER_URL = os.getenv("OUTLOOK_MCP_SERVER_URL")

# Default to localhost if not set, useful for local dev
if not CAL_COM_MCP_SERVER_URL:
    CAL_COM_MCP_SERVER_URL = "http://localhost:8001/mcp"
    print(f"Warning: CAL_COM_MCP_SERVER_URL not set in .env, defaulting to {CAL_COM_MCP_SERVER_URL}")

if not OUTLOOK_MCP_SERVER_URL:
    OUTLOOK_MCP_SERVER_URL = "http://localhost:8002/mcp"
    print(f"Warning: OUTLOOK_MCP_SERVER_URL not set in .env, defaulting to {OUTLOOK_MCP_SERVER_URL}")
from cal_com_mcp_server.tools.cal_com_tools import cal_com_mcp_instance
# Ensure core.config is loaded if it sets up environment variables needed by cal_com_mcp_instance
# from cal_com_mcp_server.core.config import CAL_COM_API_KEY # etc. if needed

# To run this server:
# 1. Ensure .env file in cal_com_mcp_server/ has CAL_COM_API_KEY
# 2. Ensure requirements.txt includes: mcp[cli], httpx, python-dotenv, pydantic, pytz, email-validator
# 3. From the PARENT directory of cal_com_mcp_server (i.e., your project root):
#    python -m cal_com_mcp_server.main

if __name__ == "__main__":
    print(
        f"Attempting to start Cal.com MCP Server (streamable-http) "
        f"on {cal_com_mcp_instance.settings.host}:{cal_com_mcp_instance.settings.port} "
        f"via mcp.run(transport='streamable-http')..."
    )
    try:
        # This will block and run the server using Uvicorn internally
        cal_com_mcp_instance.run(transport="streamable-http")
    except Exception as e:
        print(f"Failed to start Cal.com MCP server: {e}")
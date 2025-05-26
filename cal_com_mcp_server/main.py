from tools.cal_com_tools import cal_com_mcp_instance

# For newer MCP versions, FastMCP might not expose .app directly
# Try different approaches to get the FastAPI app
try:
    app = cal_com_mcp_instance.app
except AttributeError:
    # Try alternative ways to get the app
    try:
        app = cal_com_mcp_instance._app
    except AttributeError:
        try:
            app = cal_com_mcp_instance.fastapi_app
        except AttributeError:
            # Create a basic FastAPI app if we can't access the MCP app
            from fastapi import FastAPI
            app = FastAPI(title="Cal.com MCP Server", description="Cal.com integration via MCP")
            
            @app.get("/")
            def root():
                return {"message": "Cal.com MCP Server", "status": "running", "mode": "basic"}
            
            @app.get("/health")
            def health():
                return {"status": "healthy", "service": "cal_com_mcp_server"}
            
            # Add MCP endpoint if possible
            @app.post("/mcp")
            async def mcp_endpoint(request: dict):
                return {"error": "MCP direct access not available", "use": "streamable-http transport"}
            
            print("Warning: Using basic FastAPI app - MCP functionality available via streamable-http only")
# Ensure core.config is loaded if it sets up environment variables needed by cal_com_mcp_instance
# from .core.config import CAL_COM_API_KEY # etc. if needed for direct run, Render handles env vars

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
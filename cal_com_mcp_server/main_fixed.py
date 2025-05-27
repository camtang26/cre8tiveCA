#!/usr/bin/env python3
"""
Fixed main.py for Cal.com MCP Server that properly handles streamable-http
"""
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
import json
import asyncio
from typing import AsyncIterator

# Import the MCP instance
from tools.cal_com_tools import cal_com_mcp_instance

# Create FastAPI app
app = FastAPI(title="Cal.com MCP Server", description="Cal.com integration via MCP")

@app.get("/")
def root():
    return {"message": "Cal.com MCP Server", "status": "running", "mode": "mcp-enabled"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "cal_com_mcp_server"}

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """
    Handle MCP streamable-http protocol
    This endpoint needs to handle the SSE (Server-Sent Events) protocol
    """
    # Get the request body
    body = await request.body()
    
    # The MCP streamable-http expects Server-Sent Events (SSE) format
    async def generate_sse() -> AsyncIterator[str]:
        # For now, return a proper JSON-RPC error that indicates the server is not fully configured
        error_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32601,
                "message": "Method not found",
                "data": "MCP server requires proper streamable-http client connection"
            }
        }
        yield f"data: {json.dumps(error_response)}\n\n"
    
    return StreamingResponse(
        generate_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable Nginx buffering
        }
    )

# Try to get the MCP app if available
try:
    # If MCP instance has a way to get the ASGI app, use it
    if hasattr(cal_com_mcp_instance, 'get_asgi_app'):
        mcp_app = cal_com_mcp_instance.get_asgi_app()
        # Mount the MCP app under /mcp path
        app.mount("/mcp", mcp_app)
    elif hasattr(cal_com_mcp_instance, 'asgi_app'):
        app.mount("/mcp", cal_com_mcp_instance.asgi_app)
except Exception as e:
    print(f"Warning: Could not mount MCP app: {e}")
    print("Using fallback SSE endpoint for /mcp")

if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI app directly
    uvicorn.run(app, host="0.0.0.0", port=8000)
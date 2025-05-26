#!/usr/bin/env python3
"""
Fallback FastAPI application for Cal.com MCP Server
Used when MCP dependencies fail to import
"""
from fastapi import FastAPI
import os

app = FastAPI(
    title="Cal.com MCP Server",
    description="Cal.com integration service (fallback mode)",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Cal.com MCP Server running in fallback mode",
        "service": "cal_com_mcp_server",
        "mode": "fallback"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "cal_com_mcp_server",
        "mode": "fallback",
        "environment": {
            "CAL_COM_API_KEY": "***" if os.getenv("CAL_COM_API_KEY") else "not_set",
            "CAL_COM_API_BASE_URL": os.getenv("CAL_COM_API_BASE_URL", "not_set"),
            "DEFAULT_EVENT_TYPE_ID": os.getenv("DEFAULT_EVENT_TYPE_ID", "not_set")
        }
    }

@app.get("/mcp")
def mcp_endpoint():
    return {
        "error": "MCP functionality not available in fallback mode",
        "message": "Please check MCP dependencies",
        "status": "fallback_mode"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
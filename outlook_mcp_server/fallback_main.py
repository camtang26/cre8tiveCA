#!/usr/bin/env python3
"""
Fallback FastAPI application for Outlook MCP Server
Used when MCP dependencies fail to import
"""
from fastapi import FastAPI
import os

app = FastAPI(
    title="Outlook MCP Server",
    description="Outlook integration service (fallback mode)",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Outlook MCP Server running in fallback mode",
        "service": "outlook_mcp_server",
        "mode": "fallback"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "outlook_mcp_server",
        "mode": "fallback",
        "environment": {
            "AZURE_TENANT_ID": "***" if os.getenv("AZURE_TENANT_ID") else "not_set",
            "AZURE_CLIENT_ID": "***" if os.getenv("AZURE_CLIENT_ID") else "not_set",
            "AZURE_CLIENT_SECRET": "***" if os.getenv("AZURE_CLIENT_SECRET") else "not_set",
            "SENDER_UPN": os.getenv("SENDER_UPN", "not_set")
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
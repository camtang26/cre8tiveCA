# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) integration system that bridges ElevenLabs AI agents with Cal.com (scheduling) and Microsoft Outlook (email). It consists of three interconnected servers using the MCP protocol v1.0.1.

## Running the Servers

All servers must be run from the project root directory:

```bash
# Terminal 1: Bridge Server (port 8000)
uvicorn bridge_server.main:app --port 8000 --reload

# Terminal 2: Cal.com MCP Server (port 8001)
python -m cal_com_mcp_server.main

# Terminal 3: Outlook MCP Server (port 8002)
python -m outlook_mcp_server.main
```

## Required Environment Variables

Each server requires a `.env` file in its directory:

**bridge_server/.env**
```
CAL_COM_MCP_SERVER_URL=http://localhost:8001/mcp
OUTLOOK_MCP_SERVER_URL=http://localhost:8002/mcp
```

**cal_com_mcp_server/.env**
```
CAL_COM_API_KEY=<your-api-key>
CAL_COM_API_BASE_URL=https://api.cal.com/v2
DEFAULT_EVENT_TYPE_ID=1837761
DEFAULT_EVENT_DURATION_MINUTES=30
```

**outlook_mcp_server/.env**
```
AZURE_TENANT_ID=<your-tenant-id>
AZURE_CLIENT_ID=<your-client-id>
AZURE_CLIENT_SECRET=<your-client-secret>
SENDER_UPN=<sender-email@domain.com>
```

## Architecture and Communication Flow

1. **ElevenLabs** sends webhooks to → **Bridge Server** (`/webhook/elevenlabs`)
2. **Bridge Server** acts as MCP client and calls → **MCP Servers**
3. **MCP Servers** execute tools and return responses via MCP protocol

### Key Architectural Patterns

- **MCP Tool Implementation**: Tools are defined using `@mcp_instance.tool()` decorator with Pydantic models for input/output validation
- **Error Handling**: All MCP responses include an `isError` flag with detailed error messages
- **Async Operations**: All API calls use async/await pattern with httpx
- **Stateless Design**: No database; servers are completely stateless

### Directory Structure Pattern

Each server follows this structure:
```
server_name/
├── main.py           # Entry point
├── requirements.txt  # Dependencies
├── .env             # Environment variables
├── core/            # Configuration and utilities
├── schemas/         # Pydantic models
└── tools/ or mcp_clients/  # Business logic
```

## Common Development Tasks

### Installing Dependencies
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install all dependencies
pip install -r bridge_server/requirements.txt
pip install -r cal_com_mcp_server/requirements.txt
pip install -r outlook_mcp_server/requirements.txt
```

### Testing MCP Servers
```bash
# Test Cal.com MCP server directly
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "book_cal_com_event", "arguments": {...}}}'

# Test through bridge server webhook
curl -X POST http://localhost:8000/webhook/elevenlabs \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "test123", "outputs": [...]}'
```

## Key Implementation Details

### MCP Client Pattern (Bridge Server)
```python
# MCP clients use streamable-http transport
async with create_mcp_client_streamable_http(server_url) as (read_stream, write_stream):
    client = ClientSession(read_stream, write_stream)
    await client.initialize()
    
    # Call tools
    result = await client.call_tool(tool_name, arguments)
    
    # Check for errors
    if hasattr(result, 'isError') and result.isError:
        # Handle error
```

### MCP Server Pattern
```python
# Tools are defined with decorators
@mcp_instance.tool()
async def tool_name(arg1: str, arg2: int) -> ToolOutput:
    # Implementation
    return ToolOutput(...)
```

### Webhook Processing Flow
1. Receive webhook at bridge server
2. Parse `tool_calls` from payload
3. Route to appropriate MCP server based on tool name
4. Execute tool and return response

## Important Context from Memory Bank

- The system was designed to be modular and extensible
- Each MCP server can be deployed independently
- Bridge server acts as the central coordinator
- All servers use FastAPI for consistency
- MCP protocol allows for future tool additions without breaking changes



# Project: MCP Servers Deployment on Render.com

## Goal:
Successfully deploy three Python-based servers to Render.com:
1. `cal_com_mcp_server` (FastAPI, python-mcp)
2. `outlook_mcp_server` (FastAPI, python-mcp)
3. `bridge_server` (FastAPI, acts as MCP client to the other two)

## Current Core Problem:
The `cal_com_mcp_server` (and potentially `outlook_mcp_server`) fails to deploy on Render.com due to a `ModuleNotFoundError: No module named 'mcp'` (specifically, it seems `mcp.server.fastmcp` cannot be found).
Render's build logs show a warning: `WARNING: python-mcp 1.0.1 does not provide the extra 'server'`.
This indicates that the `[server]` extras for the `python-mcp` package are not being installed correctly in Render's environment, despite attempts to specify `python-mcp[server]==1.0.1` or similar in `requirements.txt`.

## Key Challenge with Render Setup:
Render's build command UI seems to prepend an unremovable directory prefix to the build command (e.g., `cal_com_mcp_server/ $ pip install -r requirements.txt`). This might be causing issues with how `pip` interprets paths or finds the `requirements.txt` file within the specified `Root Directory` for each service.

## Desired Outcome:
1. All three servers deploy successfully on Render.com.
2. The `python-mcp[server]` extras are correctly installed for `cal_com_mcp_server` and `outlook_mcp_server`.
3. The `bridge_server` can successfully communicate with the deployed MCP servers using their live Render URLs.
4. Clear and working `requirements.txt` files and Render deployment configurations (Root Directory, Build Command, Start Command) for each server.
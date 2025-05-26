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



# Render Deployment Journey & Solutions

## Problem Summary (RESOLVED)
Initially encountered `ModuleNotFoundError: No module named 'mcp.server.fastmcp'` and `python-mcp 1.0.1 does not provide the extra 'server'` warnings when deploying MCP servers to Render.com.

## Solutions Implemented

### 1. **Docker Deployment (RECOMMENDED)**
**Status**: ✅ WORKING - Services successfully deploy in fallback mode

**Implementation**:
- Created robust `Dockerfile` for both MCP servers
- Multiple MCP installation strategies with fallbacks
- Proper Python module path handling (`PYTHONPATH=/app`)
- Graceful fallback to basic FastAPI if MCP imports fail

**Key Features**:
- **Multi-strategy MCP installation**: Tries `mcp[server]`, GitHub sources, individual components
- **Diagnostic logging**: Shows exactly which packages are installed/missing
- **Fallback applications**: Basic FastAPI with health endpoints if MCP fails
- **Import error handling**: Try/except blocks for relative imports
- **Startup scripts**: Intelligent service startup with detailed diagnostics

### 2. **Enhanced Build Scripts**
**Files Created**:
- `render_build.sh` - Bash script with multiple installation attempts
- `render_install.py` - Python script with 4 fallback strategies
- `fallback_main.py` - Basic FastAPI app for when MCP imports fail

### 3. **Import Resolution Fixes**
**Problem**: Relative import errors when running in Docker
**Solution**: 
```python
try:
    from ..core.config import CONFIG
except ImportError:
    # Fallback for Docker/main module execution
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.config import CONFIG
```

### 4. **Deployment Configurations**

#### For Docker Deployment on Render:
**cal_com_mcp_server**:
- Environment: **Docker**
- Root Directory: `cal_com_mcp_server`
- Environment Variables:
  ```
  CAL_COM_API_KEY=<your-api-key>
  CAL_COM_API_BASE_URL=https://api.cal.com/v2
  DEFAULT_EVENT_TYPE_ID=1837761
  DEFAULT_EVENT_DURATION_MINUTES=30
  ```

**outlook_mcp_server**:
- Environment: **Docker**
- Root Directory: `outlook_mcp_server`
- Environment Variables:
  ```
  AZURE_TENANT_ID=<your-tenant-id>
  AZURE_CLIENT_ID=<your-client-id>
  AZURE_CLIENT_SECRET=<your-client-secret>
  SENDER_UPN=<sender-email@domain.com>
  ```

**bridge_server**:
- Environment: **Python**
- Root Directory: `bridge_server`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Environment Variables:
  ```
  CAL_COM_MCP_SERVER_URL=https://your-cal-com-service.onrender.com/mcp
  OUTLOOK_MCP_SERVER_URL=https://your-outlook-service.onrender.com/mcp
  ```

## Current Status

### ✅ Deployment Success
- Services deploy successfully on Render.com
- Docker containers start without errors
- Health endpoints accessible (`/health`, `/`)

### ⚠️ MCP Functionality Status
**Current**: Running in fallback mode (basic FastAPI)
**Issue**: MCP SDK not installing correctly, services show:
```
⚠ MCP imports failed, starting fallback application
```

**Working**:
- ✅ Web servers running
- ✅ Health checks passing
- ✅ Basic API endpoints

**Not Working**:
- ❌ Cal.com booking functionality
- ❌ Outlook email functionality  
- ❌ MCP tool endpoints

## Next Steps for Full MCP Functionality

1. **Check diagnostic logs** from latest deployment for detailed MCP package information
2. **Identify specific missing dependencies** from startup diagnostics
3. **Create targeted fix** based on what packages are actually available
4. **Goal**: See `✓ MCP imports successful, starting main application` instead of fallback mode

## Files Modified/Created

### New Files:
- `cal_com_mcp_server/Dockerfile` - Multi-strategy Docker build
- `outlook_mcp_server/Dockerfile` - Multi-strategy Docker build  
- `cal_com_mcp_server/fallback_main.py` - Fallback FastAPI app
- `outlook_mcp_server/fallback_main.py` - Fallback FastAPI app
- `render_build.sh` (both servers) - Enhanced build scripts
- `render_install.py` (both servers) - Python installation scripts
- `test_mcp_import.py` - Testing utility
- `troubleshoot_render.py` - Diagnostic utility

### Updated Files:
- `RENDER_DEPLOYMENT_GUIDE.md` - Comprehensive deployment guide
- `cal_com_mcp_server/tools/cal_com_tools.py` - Fixed imports
- `outlook_mcp_server/tools/outlook_tools.py` - Fixed imports

## Key Lessons Learned

1. **Docker provides more control** than Render's Python environment
2. **Fallback strategies are essential** for reliable deployments
3. **Import path handling** requires special care in containerized environments
4. **Diagnostic logging** is crucial for troubleshooting deployment issues
5. **MCP SDK installation** remains challenging and may require alternative approaches

## Testing Commands

```bash
# Test deployed services
curl https://your-cal-com-service.onrender.com/health
curl https://your-outlook-service.onrender.com/health

# Test MCP functionality (when working)
curl -X POST https://your-cal-com-service.onrender.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "1.0.0"}, "id": 1}'
```
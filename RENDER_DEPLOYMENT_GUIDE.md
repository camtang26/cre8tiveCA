# Render Deployment Guide for MCP Servers

This guide provides multiple approaches to fix the `python-mcp[server]` installation issue on Render.com.

## Problem Summary
Render's build system has issues installing `python-mcp[server]` extras, resulting in:
```
ModuleNotFoundError: No module named 'mcp.server.fastmcp'
```

## Solution Options

### Option 1: Use Modified requirements.txt (Recommended)
The `requirements.txt` files have been updated to use `python-mcp[server]==1.0.1`.

**For each service on Render:**
- Root Directory: `cal_com_mcp_server` or `outlook_mcp_server`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Option 2: Use Build Script
Use the provided `build.sh` scripts:

**For each service on Render:**
- Root Directory: `cal_com_mcp_server` or `outlook_mcp_server`
- Build Command: `./build.sh`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Option 3: Use Python Install Script
Use the `install_deps.py` scripts:

**For each service on Render:**
- Root Directory: `cal_com_mcp_server` or `outlook_mcp_server`
- Build Command: `python install_deps.py`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Option 4: Use Alternative Requirements File
Use `requirements-render.txt` which installs dependencies separately:

**For each service on Render:**
- Root Directory: `cal_com_mcp_server` or `outlook_mcp_server`
- Build Command: `pip install -r requirements-render.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Option 5: Multiple Pip Commands
If Render allows multiple commands separated by `&&`:

**Build Command:**
```bash
pip install -r requirements.txt && pip install --force-reinstall "python-mcp[server]==1.0.1"
```

## Environment Variables Required

### cal_com_mcp_server
```
CAL_COM_API_KEY=<your-api-key>
CAL_COM_API_BASE_URL=https://api.cal.com/v2
DEFAULT_EVENT_TYPE_ID=1837761
DEFAULT_EVENT_DURATION_MINUTES=30
```

### outlook_mcp_server
```
AZURE_TENANT_ID=<your-tenant-id>
AZURE_CLIENT_ID=<your-client-id>
AZURE_CLIENT_SECRET=<your-client-secret>
SENDER_UPN=<sender-email@domain.com>
```

### bridge_server
```
CAL_COM_MCP_SERVER_URL=<deployed-cal-com-server-url>/mcp
OUTLOOK_MCP_SERVER_URL=<deployed-outlook-server-url>/mcp
```

## Verification Steps

1. After deployment, check the Render logs for:
   - "✓ mcp.server.fastmcp module found successfully!" (if using install_deps.py)
   - No import errors when starting the server

2. Test the MCP endpoint:
   ```bash
   curl -X POST https://your-server.onrender.com/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "1.0.0"}, "id": 1}'
   ```

## Troubleshooting

If the deployment still fails:

1. Check if the build command is being executed in the correct directory
2. Try adding `cd $ROOT_DIRECTORY &&` before your build command
3. Use the Render shell to manually test the installation commands
4. Consider using a Dockerfile for more control over the build process

## Docker Alternative (if needed)

Create a `Dockerfile` in each server directory:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir "python-mcp[server]==1.0.1"

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Then use Render's Docker deployment option.
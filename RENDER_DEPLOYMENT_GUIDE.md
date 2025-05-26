# Render Deployment Guide for MCP Servers

This guide provides multiple approaches to fix the `python-mcp[server]` installation issue on Render.com.

## Problem Summary
Render's build system has issues installing `python-mcp[server]` extras, resulting in:
```
ModuleNotFoundError: No module named 'mcp.server.fastmcp'
```

## Solution Options

### Option 0: Use Enhanced Build Script (NEW - RECOMMENDED)
Use the new `render_build.sh` or `render_install.py` scripts that implement multiple fallback strategies:

**For each service on Render:**
- Root Directory: `cal_com_mcp_server` or `outlook_mcp_server`
- Build Command: `./render_build.sh` OR `python render_install.py`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

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

## Docker Alternative (RECOMMENDED if other methods fail)

Dockerfiles have been created in each server directory with robust installation strategies:

**For Docker deployment on Render:**
1. Choose "Docker" as the environment
2. Root Directory: `cal_com_mcp_server` or `outlook_mcp_server`
3. No build command needed (Dockerfile handles everything)
4. The Dockerfile includes:
   - Multi-stage dependency installation
   - Automatic fallback strategies
   - Build-time verification

## Testing and Troubleshooting Scripts

Several helper scripts are now available:

1. **test_mcp_import.py** - Test if python-mcp modules import correctly
   ```bash
   python test_mcp_import.py
   ```

2. **troubleshoot_render.py** - Diagnose installation issues
   ```bash
   python troubleshoot_render.py
   ```

3. **render_install.py** - Robust installation with multiple strategies
   ```bash
   python cal_com_mcp_server/render_install.py
   # or
   python outlook_mcp_server/render_install.py
   ```

4. **render_build.sh** - Enhanced bash build script
   ```bash
   ./cal_com_mcp_server/render_build.sh
   # or
   ./outlook_mcp_server/render_build.sh
   ```
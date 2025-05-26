# Outlook MCP Server Deployment Steps on Render.com

## Prerequisites
- Render.com account
- Azure AD application credentials (Tenant ID, Client ID, Client Secret)
- Sender email address (UPN)

## Step 1: Create New Web Service on Render

1. Log in to Render.com dashboard
2. Click "New +" → "Web Service"
3. Choose "Deploy from a Git repository"
4. Connect your GitHub repository containing the cre8tiveCA project

## Step 2: Configure the Service

### Basic Settings:
- **Name**: `outlook-mcp-server` (or your preferred name)
- **Environment**: **Docker** (IMPORTANT: Select Docker, not Python)
- **Region**: Choose closest to your users
- **Branch**: `main` (or your deployment branch)
- **Root Directory**: `outlook_mcp_server`

### Build & Deploy Settings:
- **Dockerfile Path**: Leave as default (Render will find the Dockerfile)
- **Docker Command**: Leave empty (uses CMD from Dockerfile)

## Step 3: Set Environment Variables

Add the following environment variables in Render dashboard:

```
AZURE_TENANT_ID=<your-azure-tenant-id>
AZURE_CLIENT_ID=<your-azure-client-id>  
AZURE_CLIENT_SECRET=<your-azure-client-secret>
SENDER_UPN=<sender-email@domain.com>
```

**Security Note**: These will be encrypted by Render

## Step 4: Select Instance Type

- For testing: **Free** instance
- For production: **Starter** or higher recommended

## Step 5: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Build the Docker image
   - Install dependencies with fallback strategies
   - Start the service

## Step 6: Monitor Deployment

### Check Build Logs for:
```
✓ mcp module available
✓ Base mcp module imported successfully
✓ FastMCP available
✓ FastMCP imported successfully
✓ Main app imports successful
✓ MCP imports successful, starting main application
```

### Expected Startup Message:
```
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Your service is live 🎉
```

## Step 7: Test Deployment

Once deployed, test the health endpoints:

```bash
# Test root endpoint
curl https://your-outlook-service.onrender.com/
# Expected: {"message": "Outlook MCP Server", "status": "running", ...}

# Test health endpoint
curl https://your-outlook-service.onrender.com/health
# Expected: {"status": "healthy", "service": "outlook_mcp_server"}
```

## Step 8: Note the Service URL

Copy your service URL (e.g., `https://outlook-mcp-server-xxxx.onrender.com`) for use in bridge_server configuration.

## Troubleshooting

### If MCP imports fail:
- Service will run in fallback mode
- Health endpoints will still work
- Check logs for specific error messages

### Common Issues:
1. **Missing environment variables**: Double-check all Azure credentials
2. **Docker build fails**: Check Render build logs
3. **Service crashes**: Check runtime logs in Render dashboard

## Next Steps

After successful deployment:
1. ✅ Outlook MCP server is running
2. Next: Deploy bridge_server
3. Configure bridge_server with:
   - `OUTLOOK_MCP_SERVER_URL=https://your-outlook-service.onrender.com/mcp`
   - `CAL_COM_MCP_SERVER_URL=https://your-cal-com-service.onrender.com/mcp`

## Success Indicators

✅ Service shows as "Live" in Render dashboard
✅ Health endpoints return 200 OK
✅ Logs show "MCP imports successful"
✅ No crash loops or errors in runtime logs
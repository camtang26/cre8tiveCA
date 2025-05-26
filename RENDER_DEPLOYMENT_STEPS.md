# Render Deployment Steps

## Current Status
- ✅ **cal_com_mcp_server**: Successfully deployed and operational
- 🔄 **outlook_mcp_server**: Ready for deployment (Docker files prepared)
- ⏳ **bridge_server**: Needs to be deployed after MCP servers

## Step 1: Deploy outlook_mcp_server

### 1.1 Create New Web Service on Render
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect to your GitHub repository
4. Configure as follows:

**Service Settings:**
- **Name**: `outlook-mcp-server` (or your preferred name)
- **Environment**: Docker
- **Root Directory**: `outlook_mcp_server`
- **Branch**: main (or your branch)
- **Instance Type**: Free (or your preference)

### 1.2 Add Environment Variables
In the Render service settings, add these environment variables:
```
AZURE_TENANT_ID=<your-azure-tenant-id>
AZURE_CLIENT_ID=<your-azure-client-id>
AZURE_CLIENT_SECRET=<your-azure-client-secret>
SENDER_UPN=<your-sender-email@domain.com>
```

### 1.3 Deploy and Verify
1. Click "Create Web Service"
2. Wait for deployment to complete
3. Test the service:
   ```bash
   curl https://outlook-mcp-server-xxxx.onrender.com/
   # Expected: {"message": "Outlook MCP Server", "status": "running"}
   
   curl https://outlook-mcp-server-xxxx.onrender.com/health
   # Expected: {"status": "healthy", "service": "outlook_mcp_server"}
   ```

## Step 2: Deploy bridge_server

### 2.1 Create New Web Service on Render
1. Click "New +" → "Web Service"
2. Connect to your GitHub repository
3. Configure as follows:

**Service Settings:**
- **Name**: `elevenlabs-bridge-server` (or your preferred name)
- **Environment**: Python
- **Root Directory**: `bridge_server`
- **Branch**: main (or your branch)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Instance Type**: Free (or your preference)

### 2.2 Add Environment Variables
**IMPORTANT**: Use the actual deployed URLs from your Render services:
```
CAL_COM_MCP_SERVER_URL=https://[your-cal-com-service].onrender.com/mcp
OUTLOOK_MCP_SERVER_URL=https://[your-outlook-service].onrender.com/mcp
```

Replace `[your-cal-com-service]` and `[your-outlook-service]` with the actual service names from your deployments.

### 2.3 Deploy and Verify
1. Click "Create Web Service"
2. Wait for deployment to complete
3. Test the service:
   ```bash
   curl https://elevenlabs-bridge-server-xxxx.onrender.com/
   # Expected: {"message": "ElevenLabs Bridge Server", "status": "running"}
   
   curl https://elevenlabs-bridge-server-xxxx.onrender.com/health
   # Expected: {"status": "healthy"}
   ```

## Step 3: Configure ElevenLabs Webhook

Once all services are deployed:

1. Get your bridge server URL: `https://elevenlabs-bridge-server-xxxx.onrender.com`
2. In ElevenLabs dashboard, configure the webhook URL:
   ```
   https://elevenlabs-bridge-server-xxxx.onrender.com/webhook/elevenlabs
   ```

## Step 4: Test Full Integration

### 4.1 Test Individual MCP Servers
```bash
# Test Cal.com MCP through bridge
curl -X POST https://elevenlabs-bridge-server-xxxx.onrender.com/test/cal-com \
  -H "Content-Type: application/json" \
  -d '{}'

# Test Outlook MCP through bridge  
curl -X POST https://elevenlabs-bridge-server-xxxx.onrender.com/test/outlook \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 4.2 Test ElevenLabs Webhook
Send a test webhook payload:
```bash
curl -X POST https://elevenlabs-bridge-server-xxxx.onrender.com/webhook/elevenlabs \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test123",
    "outputs": [
      {
        "tool_calls": [
          {
            "id": "test-call-1",
            "name": "book_cal_com_event",
            "parameters": {
              "attendee_name": "Test User",
              "attendee_email": "test@example.com",
              "event_start_date": "2024-05-25",
              "event_start_time": "14:00",
              "event_duration_minutes": 30,
              "meeting_title": "Test Meeting"
            }
          }
        ]
      }
    ]
  }'
```

## Troubleshooting

### If MCP servers show "fallback mode":
- This is OK! The servers will still work via streamable-http transport
- The bridge server connects using the `/mcp` endpoint

### If services fail to start:
1. Check logs in Render dashboard
2. Verify all environment variables are set correctly
3. Ensure GitHub repository is properly connected

### Common Issues:
- **Import errors**: The Docker setup includes fallbacks for this
- **MCP SDK issues**: Multiple installation strategies are attempted
- **Connection errors**: Verify the MCP server URLs in bridge_server env vars

## Next Steps After Deployment

1. Monitor service logs for any errors
2. Set up health check monitoring (optional)
3. Configure custom domains (optional)
4. Set up auto-deploy from GitHub (recommended)

## Service URLs Reference

After deployment, you'll have:
- Cal.com MCP: `https://[cal-com-service].onrender.com`
- Outlook MCP: `https://[outlook-service].onrender.com`
- Bridge Server: `https://[bridge-server].onrender.com`

The bridge server will communicate with MCP servers via:
- `https://[cal-com-service].onrender.com/mcp`
- `https://[outlook-service].onrender.com/mcp`
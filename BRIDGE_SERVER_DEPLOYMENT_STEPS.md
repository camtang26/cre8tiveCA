# Bridge Server Deployment Steps on Render.com

## Prerequisites
- Render.com account  
- Cal.com MCP Server deployed and URL available
- Outlook MCP Server deployed and URL available

## Step 1: Create New Web Service on Render

1. Log in to Render.com dashboard
2. Click "New +" → "Web Service"
3. Choose "Deploy from a Git repository"
4. Connect your GitHub repository containing the cre8tiveCA project

## Step 2: Configure the Service

### Basic Settings:
- **Name**: `elevenlabs-bridge-server` (or your preferred name)
- **Environment**: **Python** (NOT Docker)
- **Region**: Choose closest to your users
- **Branch**: `main` (or your deployment branch)
- **Root Directory**: `bridge_server`

### Build & Deploy Settings:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Step 3: Set Environment Variables

Add the following environment variables in Render dashboard:

```
CAL_COM_MCP_SERVER_URL=https://your-cal-com-service.onrender.com/mcp
OUTLOOK_MCP_SERVER_URL=https://your-outlook-service.onrender.com/mcp
```

**Important**: Replace the URLs with your actual deployed MCP server URLs from previous deployments.

## Step 4: Select Instance Type

- For testing: **Free** instance
- For production: **Starter** or higher recommended for better performance

## Step 5: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Install Python dependencies
   - Start the FastAPI application

## Step 6: Monitor Deployment

### Check Build Logs for:
```
Successfully installed fastapi uvicorn python-mcp httpx ...
Build successful 🎉
```

### Check Service Logs for:
```
Bridge Server starting up...
Cal.com MCP Server URL: https://your-cal-com-service.onrender.com/mcp
Outlook MCP Server URL: https://your-outlook-service.onrender.com/mcp
INFO: Uvicorn running on http://0.0.0.0:10000
INFO: Your service is live 🎉
```

## Step 7: Test Deployment

Once deployed, test the endpoints:

```bash
# Test root endpoint
curl https://your-bridge-server.onrender.com/
# Expected: {"message": "Bridge Server is running. Webhook endpoints at /webhook/cal/schedule_consultation and /webhook/outlook/send_email"}

# Test Cal.com webhook endpoint (with sample data)
curl -X POST https://your-bridge-server.onrender.com/webhook/cal/schedule_consultation \
  -H "Content-Type: application/json" \
  -d '{
    "start_time_utc": "2025-12-10T14:00:00Z",
    "attendee_timezone": "America/New_York",
    "attendee_name": "Test User",
    "attendee_email": "test@example.com",
    "event_type_id": 1837761
  }'

# Test Outlook webhook endpoint (with sample data)
curl -X POST https://your-bridge-server.onrender.com/webhook/outlook/send_email \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "test@example.com",
    "email_subject": "Test Email",
    "email_body_html": "<p>This is a test email</p>",
    "save_to_sent_items": true
  }'
```

## Step 8: Configure ElevenLabs Webhooks

In your ElevenLabs agent configuration, set the webhook URLs:

- **Cal.com Scheduling**: `https://your-bridge-server.onrender.com/webhook/cal/schedule_consultation`
- **Outlook Email**: `https://your-bridge-server.onrender.com/webhook/outlook/send_email`

## Troubleshooting

### Common Issues:

1. **MCP Server URLs not configured**:
   - Check environment variables are set correctly
   - Verify URLs include `/mcp` endpoint

2. **Connection to MCP servers fails**:
   - Ensure MCP servers are deployed and running
   - Check MCP server logs for errors
   - Verify network connectivity between services

3. **Webhook payload errors**:
   - Check ElevenLabs is sending correct payload format
   - Review bridge server logs for parsing errors

### Debugging Commands:

```bash
# View real-time logs
# In Render dashboard: Navigate to your service → Logs

# Test MCP server connectivity from local machine
curl https://your-cal-com-service.onrender.com/health
curl https://your-outlook-service.onrender.com/health
```

## Full System Test

After all three services are deployed:

1. **Test Cal.com Integration**:
   - Send webhook to bridge server
   - Verify booking created in Cal.com
   - Check all service logs

2. **Test Outlook Integration**:
   - Send webhook to bridge server
   - Verify email sent via Outlook
   - Check all service logs

3. **Test ElevenLabs Integration**:
   - Configure ElevenLabs agent with webhook URLs
   - Trigger agent actions
   - Monitor all service logs

## Success Indicators

✅ Bridge server shows as "Live" in Render dashboard
✅ Root endpoint returns expected message
✅ No startup errors in logs
✅ MCP server URLs logged correctly at startup
✅ Webhook endpoints respond to test requests
✅ Full integration test passes with ElevenLabs

## Security Considerations

1. **Webhook Authentication**: Consider adding authentication tokens for webhook endpoints
2. **CORS**: Configure CORS if needed for your use case
3. **Rate Limiting**: Add rate limiting for production use
4. **Error Handling**: Monitor and log all errors for debugging

## Next Steps

With all services deployed:
1. Document the deployment URLs
2. Set up monitoring/alerting
3. Test full end-to-end integration
4. Configure production settings if needed
# Direct API Deployment Guide

This guide explains how to deploy the bridge server with direct API integration, bypassing the MCP protocol layer.

## Overview

The direct API integration allows the bridge server to call Cal.com and Microsoft Graph APIs directly, eliminating the MCP protocol complexity. This approach was implemented after encountering MCP transport protocol issues.

## Architecture

```
ElevenLabs → Bridge Server → Direct API Calls → Cal.com API
                          ↘ Direct API Calls → Microsoft Graph API
```

## Prerequisites

1. **Cal.com API Key**: Obtain from your Cal.com account settings
2. **Azure App Registration**: For Microsoft Graph API access
   - Tenant ID
   - Client ID
   - Client Secret
   - Configured with `Mail.Send` permission

## Configuration

### 1. Update Bridge Server .env

Create or update `bridge_server/.env`:

```env
# Set to "direct" to use direct API integration
INTEGRATION_MODE=direct

# Cal.com API Configuration
CAL_COM_API_KEY=your-cal-com-api-key
CAL_COM_API_BASE_URL=https://api.cal.com/v2
DEFAULT_EVENT_TYPE_ID=1837761
DEFAULT_EVENT_DURATION_MINUTES=30

# Microsoft Graph API Configuration
AZURE_TENANT_ID=your-azure-tenant-id
AZURE_CLIENT_ID=your-azure-client-id
AZURE_CLIENT_SECRET=your-azure-client-secret
SENDER_UPN=sender@yourdomain.com
```

### 2. Local Testing

1. Install dependencies:
   ```bash
   cd bridge_server
   pip install -r requirements.txt
   ```

2. Run the test script:
   ```bash
   python test_direct_api_local.py
   ```

3. Start the bridge server:
   ```bash
   uvicorn bridge_server.main:app --port 8000 --reload
   ```

4. Test the endpoints:
   ```bash
   # Health check
   curl http://localhost:8000/health
   
   # Test Cal.com webhook
   curl -X POST http://localhost:8000/webhook/cal/schedule_consultation \
     -H "Content-Type: application/json" \
     -d '{
       "attendee_name": "John Doe",
       "attendee_email": "john@example.com",
       "attendee_timezone": "America/New_York",
       "start_time_utc": "2025-01-28T15:00:00Z",
       "end_time_utc": "2025-01-28T15:30:00Z",
       "event_type_id": 1837761
     }'
   
   # Test Outlook webhook
   curl -X POST http://localhost:8000/webhook/outlook/send_email \
     -H "Content-Type: application/json" \
     -d '{
       "recipient_email": "recipient@example.com",
       "email_subject": "Test Email",
       "email_body_html": "<p>This is a test email</p>",
       "save_to_sent_items": false
     }'
   ```

## Deployment to Render.com

### Bridge Server Deployment

1. **Create New Web Service** on Render.com

2. **Configure Service**:
   - **Environment**: Python
   - **Root Directory**: `bridge_server`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**:
   ```
   INTEGRATION_MODE=direct
   CAL_COM_API_KEY=<your-cal-com-api-key>
   CAL_COM_API_BASE_URL=https://api.cal.com/v2
   DEFAULT_EVENT_TYPE_ID=1837761
   DEFAULT_EVENT_DURATION_MINUTES=30
   AZURE_TENANT_ID=<your-azure-tenant-id>
   AZURE_CLIENT_ID=<your-azure-client-id>
   AZURE_CLIENT_SECRET=<your-azure-client-secret>
   SENDER_UPN=<sender@yourdomain.com>
   ```

4. **Deploy**: Click "Create Web Service"

### Post-Deployment Testing

Once deployed, test your bridge server:

```bash
# Replace with your Render URL
BRIDGE_URL=https://your-bridge-server.onrender.com

# Health check
curl $BRIDGE_URL/health

# Should return:
# {
#   "status": "healthy",
#   "integration_mode": "direct",
#   "timestamp": "2025-01-27T..."
# }
```

## Advantages of Direct API Integration

1. **Simplicity**: No MCP protocol complexity
2. **Performance**: Direct API calls are faster
3. **Reliability**: Fewer moving parts, fewer points of failure
4. **Debugging**: Easier to troubleshoot API issues
5. **Flexibility**: Can use full API features without MCP limitations

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify API keys and credentials in environment variables
   - Check Azure app permissions for Mail.Send

2. **Timezone Issues**
   - Ensure timezone strings are valid IANA timezone identifiers
   - The bridge server handles UTC to local timezone conversion

3. **Rate Limiting**
   - Both Cal.com and Microsoft Graph have rate limits
   - Implement exponential backoff if needed

### Debug Mode

To enable detailed logging:

```python
# In bridge_server/main.py
logging.basicConfig(level=logging.DEBUG)
```

## Migrating from MCP to Direct

If you have existing MCP servers deployed:

1. Keep them running (no need to delete)
2. Simply change `INTEGRATION_MODE=direct` in bridge server
3. Add the API credentials to environment variables
4. Redeploy the bridge server

The bridge server will automatically use direct API calls instead of MCP.

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **HTTPS**: Always use HTTPS in production
3. **Azure Permissions**: Grant only necessary permissions (Mail.Send)
4. **Input Validation**: The bridge server validates all webhook inputs

## Next Steps

1. Configure ElevenLabs to send webhooks to your deployed bridge server
2. Monitor logs for any errors
3. Set up error alerting (optional)
4. Consider implementing retry logic for failed API calls

## Support

For issues or questions:
- Check the logs in Render.com dashboard
- Review error messages in API responses
- Ensure all environment variables are correctly set
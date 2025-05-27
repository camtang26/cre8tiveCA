# ElevenLabs Integration Bridge - Direct API Implementation

## Overview

This bridge server integrates ElevenLabs AI agents with Cal.com (scheduling) and Microsoft Outlook (email) using direct API calls. This implementation bypasses the MCP protocol layer for improved reliability and simplicity.

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Cre8tiveAI-CA
   ```

2. **Set up environment**
   ```bash
   cd bridge_server
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure credentials**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

4. **Run the server**
   ```bash
   uvicorn main:app --port 8000 --reload
   ```

## API Endpoints

### Health Check
```
GET /health
```

### Cal.com Scheduling Webhook
```
POST /webhook/cal/schedule_consultation
```

**Request Body:**
```json
{
  "attendee_name": "John Doe",
  "attendee_email": "john@example.com",
  "attendee_timezone": "America/New_York",
  "start_time_utc": "2025-01-28T15:00:00Z",
  "end_time_utc": "2025-01-28T15:30:00Z",
  "event_type_id": 1837761,
  "guests": [],
  "metadata": {},
  "language": "en"
}
```

### Outlook Email Webhook
```
POST /webhook/outlook/send_email
```

**Request Body:**
```json
{
  "recipient_email": "recipient@example.com",
  "email_subject": "Meeting Confirmation",
  "email_body_html": "<html><body><p>Your meeting has been scheduled.</p></body></html>",
  "save_to_sent_items": true
}
```

## Configuration

### Required API Credentials

1. **Cal.com API Key**
   - Log in to Cal.com
   - Go to Settings → Developer → API Keys
   - Create a new API key

2. **Microsoft Azure App Registration**
   - Create an app registration in Azure Portal
   - Grant `Mail.Send` permission
   - Create a client secret
   - Note the Tenant ID, Client ID, and Client Secret

### Environment Variables

Create a `.env` file in the `bridge_server` directory:

```env
# Integration mode
INTEGRATION_MODE=direct

# Cal.com API
CAL_COM_API_KEY=your-cal-com-api-key
CAL_COM_API_BASE_URL=https://api.cal.com/v2
DEFAULT_EVENT_TYPE_ID=1837761
DEFAULT_EVENT_DURATION_MINUTES=30

# Microsoft Graph API
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
SENDER_UPN=sender@yourdomain.com
```

## Deployment

### Deploy to Render.com

1. Fork this repository
2. Connect your GitHub account to Render
3. Create a new Web Service
4. Configure:
   - **Environment**: Python
   - **Root Directory**: `bridge_server`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in Render dashboard
6. Deploy!

### Deploy to other platforms

The bridge server is a standard FastAPI application and can be deployed to:
- Heroku
- Railway
- Google Cloud Run
- AWS Lambda (with Mangum adapter)
- Any platform that supports Python web applications

## Integration with ElevenLabs

Configure your ElevenLabs agent to send webhooks to:
- Cal.com scheduling: `https://your-bridge-url/webhook/cal/schedule_consultation`
- Outlook email: `https://your-bridge-url/webhook/outlook/send_email`

## Testing

Run the test suite:
```bash
python test_direct_api_local.py
```

Test individual endpoints:
```bash
# Test Cal.com integration
curl -X POST http://localhost:8000/webhook/cal/schedule_consultation \
  -H "Content-Type: application/json" \
  -d @test_data/cal_webhook.json

# Test Outlook integration
curl -X POST http://localhost:8000/webhook/outlook/send_email \
  -H "Content-Type: application/json" \
  -d @test_data/outlook_webhook.json
```

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ ElevenLabs  │────▶│    Bridge    │────▶│  Cal.com    │
│   Agent     │     │   Server     │     │    API      │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Microsoft   │
                    │ Graph API   │
                    └─────────────┘
```

## Troubleshooting

### Common Issues

1. **401 Unauthorized from Cal.com**
   - Check your API key is correct
   - Ensure the API key has necessary permissions

2. **Azure authentication fails**
   - Verify all Azure credentials (tenant, client, secret)
   - Check the app registration has Mail.Send permission
   - Ensure the sender UPN matches a valid mailbox

3. **Timezone errors**
   - Use valid IANA timezone identifiers (e.g., "America/New_York")
   - The bridge handles UTC to local timezone conversion

### Debug Mode

Enable debug logging by setting in your code:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Your License Here]

## Support

For issues or questions:
- Open an issue on GitHub
- Check the [Direct API Deployment Guide](DIRECT_API_DEPLOYMENT_GUIDE.md)
- Review logs for detailed error messages
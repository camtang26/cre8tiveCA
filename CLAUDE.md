# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Integration system bridging ElevenLabs AI agents with Cal.com (scheduling) and Microsoft Outlook (email).

**Current Mode**: Direct API integration (recommended over MCP due to deployment simplicity)

## Architecture

```
ElevenLabs Agent → Bridge Server → Cal.com API / Microsoft Graph API
```

### Key Components

1. **Bridge Server** (`bridge_server/`)
   - FastAPI server receiving ElevenLabs webhooks
   - Routes to appropriate API based on `INTEGRATION_MODE`
   - Dual mode support: Direct API (recommended) or MCP

2. **Direct API Clients** (`bridge_server/api_clients/`)
   - `cal_com_direct.py`: Cal.com API v2 integration
   - `outlook_direct.py`: Microsoft Graph API integration

3. **MCP Servers** (legacy, for reference)
   - `cal_com_mcp_server/`: Cal.com MCP wrapper
   - `outlook_mcp_server/`: Outlook MCP wrapper

## Running Locally

```bash
# Set up environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r bridge_server/requirements.txt

# Configure bridge_server/.env
INTEGRATION_MODE=direct
CAL_COM_API_KEY=<your-api-key>
CAL_COM_API_BASE_URL=https://api.cal.com/v2
DEFAULT_EVENT_TYPE_ID=1837761
DEFAULT_EVENT_DURATION_MINUTES=30
AZURE_TENANT_ID=<your-tenant-id>
AZURE_CLIENT_ID=<your-client-id>
AZURE_CLIENT_SECRET=<your-client-secret>
SENDER_UPN=<sender-email@domain.com>

# Run bridge server
uvicorn bridge_server.main:app --port 8000 --reload
```

## Webhook Endpoints

### Cal.com Scheduling
```
POST /webhook/cal/schedule_consultation
```

Expected payload:
```json
{
  "start_time_utc": "2025-12-10T14:00:00Z",  // ISO 8601 UTC
  "attendee_timezone": "America/New_York",    // IANA timezone
  "attendee_name": "John Doe",
  "attendee_email": "john@example.com",
  "event_type_id": 1837761,
  "guests": ["guest@example.com"],            // Optional
  "metadata": {"conversation_id": "123"}      // Optional
}
```

### Outlook Email
```
POST /webhook/outlook/send_email
```

Expected payload:
```json
{
  "recipient_email": "recipient@example.com",
  "email_subject": "Meeting Confirmation",
  "email_body_html": "<html>...</html>",
  "save_to_sent_items": true
}
```

## Testing

```bash
# Quick health check
curl http://localhost:8000/health

# Test full system (comprehensive)
python test_full_system.py http://localhost:8000

# Test direct API clients only
python test_direct_api_local.py

# Manual webhook test
curl -X POST http://localhost:8000/webhook/cal/schedule_consultation \
  -H "Content-Type: application/json" \
  -d '{"start_time_utc": "2025-12-15T16:00:00Z", "attendee_timezone": "America/New_York", "attendee_name": "Test User", "attendee_email": "test@example.com", "event_type_id": 1837761}'
```

## Key Implementation Patterns

### Timezone Handling
```python
# Convert UTC to local (in main.py)
utc_dt = datetime.strptime(payload.start_time_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
attendee_tz = pytz.timezone(payload.attendee_timezone)
local_dt = utc_dt.astimezone(attendee_tz)
```

### Error Response Pattern
```python
# Consistent error responses
return JSONResponse(
    status_code=400,  # or 500 for server errors
    content={"status": "error", "message": "Description", "details": {...}}
)
```

### Direct API Client Pattern
```python
# Both API clients follow similar patterns
async def create_booking(self, booking_input: CalComBookingInput) -> CalComBookingOutput:
    # 1. Validate and convert times
    # 2. Check availability (if applicable)
    # 3. Make API call with proper headers
    # 4. Return standardized output
```

## Deployment URLs (Production)

- Cal.com MCP: https://cal-mcp.onrender.com
- Outlook MCP: https://outlook-mcp-server.onrender.com
- Bridge Server: (pending deployment)

## Important Notes

1. **Event Type ID**: Default is 1837761 (30-min consultation)
2. **Email Formatting**: Outlook client auto-wraps content in professional HTML template
3. **Cold Starts**: Render.com free tier may have 30-40 second initial delays
   - Mitigation: `/ping` endpoint available for keep-alive monitoring
   - Set up external service to ping every 10 minutes
4. **Authentication**: No webhook authentication implemented (consider for production)
5. **Logging**: All operations logged with `logger.info()` for debugging
6. **Email Tool**: System uses single `send_email` tool (no separate compose step)
7. **Performance**: Direct API mode optimized with connection pooling and 10s timeouts
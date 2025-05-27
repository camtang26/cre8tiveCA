# Direct API Integration Guide (Alternative to MCP)

Due to limitations with MCP protocol on Render's deployment, here's a direct integration approach that bypasses the MCP layer.

## Why Direct Integration?

The MCP (Model Context Protocol) adds complexity that isn't necessary for simple webhook handling. By calling the Cal.com and Outlook APIs directly from the bridge server, we can:

1. **Eliminate timeout issues** - No MCP protocol overhead
2. **Simplify debugging** - Direct API calls are easier to trace
3. **Improve reliability** - Fewer moving parts
4. **Maintain the same interface** - ElevenLabs webhooks work the same way

## Architecture

```
ElevenLabs Agent
    ↓ (webhooks)
Bridge Server (Direct API calls)
    ├── Cal.com API
    └── Microsoft Graph API (Outlook)
```

## Implementation

### Option 1: Modify Bridge Server

Update the bridge server to call APIs directly instead of using MCP clients:

```python
# bridge_server/api_clients/cal_com_direct.py
import httpx
from core.config import CAL_COM_API_KEY

async def create_cal_booking(
    date: str,
    time: str, 
    timezone: str,
    name: str,
    email: str,
    event_type_id: int
):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.cal.com/v2/bookings",
            headers={"Authorization": f"Bearer {CAL_COM_API_KEY}"},
            json={
                "eventTypeId": event_type_id,
                "start": f"{date}T{time}:00",
                "timeZone": timezone,
                "attendees": [{
                    "name": name,
                    "email": email
                }]
            }
        )
        return response.json()
```

### Option 2: Use Existing MCP Server Code

The MCP servers already have the API integration code. You can:

1. Extract the API functions from `cal_com_mcp_server/core/cal_api_utils.py`
2. Copy them to the bridge server
3. Remove the MCP wrapper layer

## Benefits

1. **Immediate reliability** - No protocol issues
2. **Faster response times** - Direct API calls
3. **Easier to maintain** - Standard REST API integration
4. **Same functionality** - All features still available

## Quick Test

Here's a simple test script for direct API integration:

```python
import asyncio
import httpx
import os

async def test_direct_cal_api():
    """Test direct Cal.com API call"""
    
    API_KEY = os.getenv("CAL_COM_API_KEY")
    
    async with httpx.AsyncClient() as client:
        # Get event types
        response = await client.get(
            "https://api.cal.com/v2/event-types",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        
        if response.status_code == 200:
            print("✅ Cal.com API accessible")
            print(f"Event types: {response.json()}")
        else:
            print(f"❌ Cal.com API error: {response.status_code}")

asyncio.run(test_direct_cal_api())
```

## Migration Path

1. **Keep the same webhook endpoints** - No changes for ElevenLabs
2. **Update bridge server** - Replace MCP clients with direct API calls
3. **Test thoroughly** - Ensure all functionality works
4. **Deprecate MCP servers** - Can be removed once direct integration works

## Conclusion

While MCP is a powerful protocol for AI model integration, for simple webhook handling between services, direct API integration is more reliable and easier to maintain, especially on free-tier hosting platforms.
# Summary of Your Questions & Fixes

## 1. Environment Variables for Bridge Server

**You asked**: "The cal and outlook URLs in bridge server are still MCP URLs. What URLs should I use?"

**Answer**: When using `INTEGRATION_MODE=direct`, you don't need MCP URLs at all!

### What to set in Bridge Server on Render:

```env
# REQUIRED for Direct Mode
INTEGRATION_MODE=direct

# Cal.com credentials (REQUIRED)
CAL_COM_API_KEY=cal_live_a1a7f415bceb19fa689b6f2bb6b5cf04
CAL_COM_API_BASE_URL=https://api.cal.com/v2
DEFAULT_EVENT_TYPE_ID=1837761
DEFAULT_EVENT_DURATION_MINUTES=30

# Microsoft credentials (REQUIRED)
AZURE_TENANT_ID=14b18652-4ee2-42c2-888f-7d7ced54fc71
AZURE_CLIENT_ID=e35ef5aa-b6c5-4007-a33c-31e6a1df3a0f
AZURE_CLIENT_SECRET=<your-azure-client-secret>
SENDER_UPN=cameron@cre8tive.ai

# These can be REMOVED or IGNORED:
# CAL_COM_MCP_SERVER_URL=<not needed>
# OUTLOOK_MCP_SERVER_URL=<not needed>
```

**Your MCP servers on Render**: Can be shut down to save resources (they're not used in direct mode)

## 2. Data Types in ElevenLabs Configuration

**You asked**: "Should attendee be an object? The Cal.com API expects specific formatting."

**Answer**: All fields in ElevenLabs should be **strings**, even though Cal.com expects an object. Here's why:

### The Data Flow:

1. **ElevenLabs sends flat JSON** (all strings):
```json
{
  "attendee_name": "Cameron Tang",
  "attendee_email": "wowcam26@gmail.com",
  "attendee_timezone": "Australia/Brisbane",
  "start_time_utc": "2025-05-28T00:00:00Z",
  "end_time_utc": "2025-05-28T00:30:00Z",
  "event_type_id": 1837761
}
```

2. **Bridge server transforms it** to Cal.com format:
```json
{
  "eventTypeId": 1837761,
  "start": "2025-05-28T00:00:00Z",
  "attendee": {
    "name": "Cameron Tang",
    "email": "wowcam26@gmail.com",
    "timeZone": "Australia/Brisbane",
    "language": "en"
  }
}
```

**So your ElevenLabs configuration is correct** - all string fields!

## 3. Your Other Tools

**You asked**: "Do I still need get_event_types, get_available_slots, and convert_to_UTC tools?"

### Keep These:
- **get_available_slots** ✅ - Shows available times before booking (better UX)
- **get_event_types** ✅ (optional) - If you offer different appointment types

### Remove This:
- **convert_to_UTC** ❌ - The agent handles this internally now

## Fixes Just Committed:

1. **Made timezone optional** with default value
2. **Fixed Cal.com API v2 format** - using correct `attendee` object
3. **Added required API version header** - cal-api-version: 2024-08-13

## Next Steps:

1. **Push to GitHub**: `git push origin main`
2. **Render will auto-deploy** the fixes
3. **Add the environment variables** to bridge server on Render
4. **Test again** - it should work now!

The main issues were:
- Bridge server was in MCP mode (needs INTEGRATION_MODE=direct)
- API credentials weren't in bridge server
- Cal.com payload format was slightly wrong (now fixed)
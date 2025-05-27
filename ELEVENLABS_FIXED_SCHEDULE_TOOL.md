# Fixed Schedule Consultation Tool Configuration

## Issue Found
The webhook was missing the `attendee_timezone` parameter, causing a 422 error. I've updated the bridge server to make this field optional with a default value of "America/New_York".

## Two Options to Fix in ElevenLabs:

### Option 1: Add the Missing Timezone Field (Recommended)

In your ElevenLabs tool configuration, add this additional property:

**Property Name**: attendee_timezone
- **Data type**: `String`
- **Identifier**: `attendee_timezone`
- **Required**: ❌ No (unchecked)
- **Value Type**: `Static` OR `LLM Prompt`
- **Value** (if Static): `America/New_York`
- **Description**: `Timezone for the appointment (e.g., America/New_York, Europe/London). Defaults to America/New_York if not specified.`

### Option 2: Keep Current Configuration (After Deploy)

Once you deploy the updated bridge server with the fix I just committed, the current configuration will work as-is because the timezone will default to "America/New_York".

## Steps to Deploy the Fix:

1. **Push the fix to GitHub**:
   ```bash
   git push origin main
   ```

2. **Redeploy on Render**:
   - The deployment should trigger automatically
   - Or manually trigger from Render dashboard

3. **Test Again**:
   - Try the same booking request
   - It should now work with or without timezone

## Updated Agent Instructions

If you add the timezone field, update your agent instructions:

```
When scheduling appointments:
1. Ask for name and email (required)
2. Ask for preferred date and time
3. Ask for timezone (optional - if not specified, use America/New_York)
4. Convert the time to UTC format before calling the tool

Example conversation:
User: "Schedule a meeting tomorrow at 2 PM"
Agent: "I'll schedule that for you. What timezone are you in?"
User: "Eastern time" 
Agent: "Perfect, I'll schedule it for 2 PM Eastern Time (America/New_York)"
```

## Testing the Fixed Configuration

### Test without timezone (will use default):
```json
{
  "attendee_name": "Cameron Tang",
  "attendee_email": "wowcam26@gmail.com",
  "start_time_utc": "2025-05-28T18:00:00Z",
  "end_time_utc": "2025-05-28T18:30:00Z",
  "event_type_id": 1837761
}
```

### Test with timezone:
```json
{
  "attendee_name": "Cameron Tang",
  "attendee_email": "wowcam26@gmail.com",
  "attendee_timezone": "America/New_York",
  "start_time_utc": "2025-05-28T18:00:00Z",
  "end_time_utc": "2025-05-28T18:30:00Z",
  "event_type_id": 1837761
}
```

## Direct Testing Command

You can test the bridge server directly:

```bash
curl -X POST https://elevenlabs-bridge-server.onrender.com/webhook/cal/schedule_consultation \
  -H "Content-Type: application/json" \
  -d '{
    "attendee_name": "Test User",
    "attendee_email": "test@example.com",
    "start_time_utc": "2025-05-28T19:00:00Z",
    "end_time_utc": "2025-05-28T19:30:00Z",
    "event_type_id": 1837761
  }'
```

This should now work even without the timezone field!
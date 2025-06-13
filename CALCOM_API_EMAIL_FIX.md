# Cal.com API Email Notification Fix

## The Problem
Cal.com confirmation emails were not being sent when bookings were created through the Netlify Edge Function, even though:
- Bookings were created successfully
- The same API worked fine with the Render backend
- Cal.com settings hadn't changed

## Root Cause
The payload structure was incorrect. Cal.com API v2 requires a specific structure to trigger email notifications.

## The Fix

### ❌ WRONG (What we had):
```json
{
  "eventTypeId": 1837761,
  "start": "2025-06-12T23:00:00Z",
  "end": "2025-06-12T23:30:00Z",
  "timeZone": "Australia/Brisbane",
  "responses": {
    "name": "Cameron",
    "email": "cameron@cre8tive.ai"
  },
  "metadata": {}
}
```

### ✅ CORRECT (What Cal.com expects):
```json
{
  "eventTypeId": 1837761,
  "start": "2025-06-12T23:00:00Z",
  "attendee": {
    "name": "Cameron",
    "email": "cameron@cre8tive.ai",
    "timeZone": "Australia/Brisbane",
    "language": "en"
  },
  "metadata": {}
}
```

## Key Differences:
1. **Use `attendee` object, NOT `responses`** - This is critical for email notifications
2. **Timezone goes INSIDE the attendee object**, not at root level
3. **Language goes INSIDE the attendee object**, not at root level
4. **Don't send `end` time** - Cal.com calculates it from the event type duration
5. **No special headers needed** - Just the standard API headers

## Why This Happened:
- The Cal.com API v2 documentation might show `responses` for some endpoints
- But for email notifications to work, you MUST use the `attendee` structure
- This is an undocumented requirement of the Cal.com API

## Verification:
The fix has been deployed. Test bookings should now:
1. Create the booking successfully ✅
2. Send Cal.com confirmation email to attendee ✅
3. Send Stuart's follow-up email via Outlook ✅
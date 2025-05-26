# ElevenLabs Integration Guide

## System Overview

Your system is now fully deployed and ready for ElevenLabs integration:

- **Bridge Server**: Receives webhooks from ElevenLabs
- **Cal.com MCP Server**: Handles appointment scheduling
- **Outlook MCP Server**: Handles email sending

## 🚀 Quick Start

### Step 1: Get Your Bridge Server URL

Your bridge server URL from Render will look like:
```
https://your-bridge-server-name.onrender.com
```

### Step 2: Configure ElevenLabs Webhooks

In your ElevenLabs agent configuration, add these webhook endpoints:

#### For Calendar Scheduling:
```
URL: https://your-bridge-server-name.onrender.com/webhook/cal/schedule_consultation
Method: POST
```

#### For Email Sending:
```
URL: https://your-bridge-server-name.onrender.com/webhook/outlook/send_email
Method: POST
```

## 📋 Webhook Payload Formats

### Cal.com Scheduling Webhook

**Expected payload from ElevenLabs:**
```json
{
  "start_time_utc": "2025-12-10T14:00:00Z",
  "attendee_timezone": "America/New_York",
  "attendee_name": "John Doe",
  "attendee_email": "john.doe@example.com",
  "event_type_id": 1837761,
  "language": "en",
  "guests": ["guest1@example.com", "guest2@example.com"],  // Optional
  "metadata": {                                             // Optional
    "conversation_id": "elevenlabs_12345",
    "custom_field": "value"
  }
}
```

**Fields:**
- `start_time_utc`: ISO 8601 UTC timestamp (YYYY-MM-DDTHH:MM:SSZ)
- `attendee_timezone`: Valid IANA timezone (e.g., "America/New_York", "Europe/London")
- `attendee_name`: Full name of the attendee
- `attendee_email`: Valid email address
- `event_type_id`: Cal.com event type ID (default: 1837761 for 30-min consultation)
- `language`: Language code (default: "en")
- `guests`: Optional array of additional attendee emails
- `metadata`: Optional object for custom data

**Success Response:**
```json
{
  "status": "success",
  "message": "Booking created successfully",
  "details": {
    "id": "booking_123",
    "status": "accepted",
    "start_time": "2025-12-10T14:00:00Z",
    "end_time": "2025-12-10T14:30:00Z"
  }
}
```

### Outlook Email Webhook

**Expected payload from ElevenLabs:**
```json
{
  "recipient_email": "recipient@example.com",
  "email_subject": "Meeting Confirmation",
  "email_body_html": "<html><body><h2>Your meeting is confirmed</h2><p>Details...</p></body></html>",
  "save_to_sent_items": true
}
```

**Fields:**
- `recipient_email`: Valid email address
- `email_subject`: Email subject line
- `email_body_html`: HTML formatted email body
- `save_to_sent_items`: Boolean (save copy in Sent folder)

**Success Response:**
```json
{
  "status": "success",
  "message": "Email sent successfully"
}
```

## 🧪 Testing Your Integration

### 1. Quick Test (Basic Functionality)
```bash
python quick_system_test.py https://your-bridge-server-name.onrender.com
```

### 2. Full System Test (Comprehensive)
```bash
python test_full_system.py https://your-bridge-server-name.onrender.com
```

### 3. Manual Test with curl

**Test Cal.com scheduling:**
```bash
curl -X POST https://your-bridge-server-name.onrender.com/webhook/cal/schedule_consultation \
  -H "Content-Type: application/json" \
  -d '{
    "start_time_utc": "2025-12-15T16:00:00Z",
    "attendee_timezone": "America/New_York",
    "attendee_name": "Test User",
    "attendee_email": "test@example.com",
    "event_type_id": 1837761
  }'
```

**Test Outlook email:**
```bash
curl -X POST https://your-bridge-server-name.onrender.com/webhook/outlook/send_email \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "test@example.com",
    "email_subject": "Test Email",
    "email_body_html": "<p>This is a test</p>",
    "save_to_sent_items": true
  }'
```

## 🎯 ElevenLabs Agent Configuration Tips

### 1. Conversation Flow Example

```
User: "I'd like to schedule a consultation for next Tuesday at 2 PM"

Agent: 
1. Extract date/time information
2. Convert to UTC
3. Call Cal.com webhook
4. On success, call Outlook webhook to send confirmation

Response: "I've scheduled your consultation for Tuesday at 2 PM Eastern Time. 
A confirmation email has been sent to your email address."
```

### 2. Error Handling

The bridge server returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid data)
- `422`: Validation error (missing fields)
- `500`: Server error

Your ElevenLabs agent should handle these appropriately.

### 3. Timezone Handling

Always specify timezones explicitly:
- Store/process times in UTC
- Accept user's local timezone
- Common US timezones:
  - "America/New_York" (Eastern)
  - "America/Chicago" (Central)
  - "America/Denver" (Mountain)
  - "America/Los_Angeles" (Pacific)

## 🔍 Monitoring and Debugging

### Check Service Health

1. **Bridge Server**: `https://your-bridge-server-name.onrender.com/`
2. **View Logs**: Render Dashboard → Your Service → Logs

### Common Issues and Solutions

#### Issue: "Unknown timezone" error
**Solution**: Ensure timezone is a valid IANA timezone string

#### Issue: Email not sending
**Solution**: Check Outlook MCP server logs for authentication errors

#### Issue: Booking fails
**Solution**: Verify event_type_id matches your Cal.com configuration

## 📊 Performance Considerations

- **Cold Starts**: First request may take 30-40 seconds on free tier
- **Concurrent Requests**: System handles multiple requests well
- **Timeouts**: Set webhook timeout to at least 30 seconds in ElevenLabs

## 🔐 Security Notes

1. **HTTPS Only**: All endpoints use HTTPS
2. **No Authentication**: Consider adding API keys for production
3. **Rate Limiting**: Not implemented - add for production use
4. **Data Privacy**: Emails and booking data are processed but not stored

## 📞 Support and Troubleshooting

### Service Status
- Cal.com MCP: `https://cal-mcp.onrender.com/health`
- Outlook MCP: `https://outlook-mcp-server.onrender.com/health`
- Bridge Server: `https://your-bridge-server-name.onrender.com/`

### Debug Process
1. Check bridge server logs
2. Verify webhook payload format
3. Test with curl commands
4. Check MCP server logs if needed

## ✅ Integration Checklist

Before going live:

- [ ] Run `test_full_system.py` - all tests pass
- [ ] Configure ElevenLabs webhook URLs
- [ ] Test with actual ElevenLabs agent
- [ ] Monitor first few real interactions
- [ ] Set up error alerting (optional)
- [ ] Document any custom event_type_ids
- [ ] Test various timezones
- [ ] Verify email formatting

## 🎉 You're Ready!

Your system is deployed and ready for ElevenLabs integration. The webhooks will handle:
- Scheduling appointments in Cal.com
- Sending emails via Outlook
- Converting timezones automatically
- Providing appropriate error messages

Good luck with your ElevenLabs agent! 🚀
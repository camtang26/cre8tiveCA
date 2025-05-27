# Complete ElevenLabs Custom Tools Setup Guide

This guide provides the exact configuration for setting up Cal.com scheduling and Outlook email tools in your ElevenLabs Conversational AI agent.

## Tool 1: Cal.com Scheduling Tool

### Basic Configuration

**Tool Type**: Webhook

**Name**: `schedule_consultation`

**Description**: 
```
Schedule a consultation appointment with Cal.com. Collect attendee's name, email, preferred date/time, and timezone. Convert times to UTC format before calling this tool.
```

**Method**: `POST`

**URL**: `https://elevenlabs-bridge-server.onrender.com/webhook/cal/schedule_consultation`

**Response timeout**: 20 seconds (default)

### Headers

1. **Header 1**:
   - Type: `Value`
   - Name: `Content-Type`
   - Value: `application/json`

### Body Parameters

**Description**:
```
This request creates a new booking on Cal.com. The bridge server will handle the API integration.
JSON template:
{
  "attendee_name": "$attendeeName",
  "attendee_email": "$attendeeEmail",
  "attendee_timezone": "$attendeeTimezone",
  "start_time_utc": "$startTimeUtc",
  "end_time_utc": "$endTimeUtc",
  "event_type_id": $eventTypeId
}
```

### Properties (Body Parameters)

#### 1. attendee_name
- **Data type**: `String`
- **Identifier**: `attendee_name`
- **Required**: ✅ Yes
- **Value Type**: `LLM Prompt`
- **Description**: `Full name of the person scheduling the appointment`

#### 2. attendee_email
- **Data type**: `String`
- **Identifier**: `attendee_email`
- **Required**: ✅ Yes
- **Value Type**: `LLM Prompt`
- **Description**: `Email address of the attendee`

#### 3. attendee_timezone
- **Data type**: `String`
- **Identifier**: `attendee_timezone`
- **Required**: ✅ Yes
- **Value Type**: `LLM Prompt`
- **Description**: `Attendee's IANA timezone (e.g., America/New_York, Europe/London). Default to America/New_York if not specified.`

#### 4. start_time_utc
- **Data type**: `String`
- **Identifier**: `start_time_utc`
- **Required**: ✅ Yes
- **Value Type**: `LLM Prompt`
- **Description**: `Appointment start time in UTC format. Must be formatted as YYYY-MM-DDTHH:MM:SSZ (e.g., 2025-01-28T15:00:00Z)`

#### 5. end_time_utc
- **Data type**: `String`
- **Identifier**: `end_time_utc`
- **Required**: ✅ Yes
- **Value Type**: `LLM Prompt`
- **Description**: `Appointment end time in UTC format. Must be formatted as YYYY-MM-DDTHH:MM:SSZ. Typically 30 minutes after start time.`

#### 6. event_type_id
- **Data type**: `Number`
- **Identifier**: `event_type_id`
- **Required**: ✅ Yes
- **Value Type**: `Static`
- **Value**: `1837761`
- **Description**: `Cal.com event type ID (static value)`

#### 7. guests (Optional)
- **Data type**: `Array`
- **Identifier**: `guests`
- **Required**: ❌ No
- **Value Type**: `LLM Prompt`
- **Description**: `Array of additional guest email addresses (optional)`

#### 8. metadata (Optional)
- **Data type**: `Object`
- **Identifier**: `metadata`
- **Required**: ❌ No
- **Value Type**: `LLM Prompt`
- **Description**: `Additional metadata for the booking (optional)`

## Tool 2: Outlook Email Tool

### Basic Configuration

**Tool Type**: Webhook

**Name**: `send_email`

**Description**: 
```
Send an email via Outlook/Microsoft 365. Use this to send confirmation emails, follow-ups, or any other email communications.
```

**Method**: `POST`

**URL**: `https://elevenlabs-bridge-server.onrender.com/webhook/outlook/send_email`

**Response timeout**: 20 seconds (default)

### Headers

1. **Header 1**:
   - Type: `Value`
   - Name: `Content-Type`
   - Value: `application/json`

### Body Parameters

**Description**:
```
This request sends an email through Outlook/Microsoft 365.
JSON template:
{
  "recipient_email": "$recipientEmail",
  "email_subject": "$emailSubject",
  "email_body_html": "$emailBodyHtml",
  "save_to_sent_items": $saveToSentItems
}
```

### Properties (Body Parameters)

#### 1. recipient_email
- **Data type**: `String`
- **Identifier**: `recipient_email`
- **Required**: ✅ Yes
- **Value Type**: `LLM Prompt`
- **Description**: `Email address of the recipient`

#### 2. email_subject
- **Data type**: `String`
- **Identifier**: `email_subject`
- **Required**: ✅ Yes
- **Value Type**: `LLM Prompt`
- **Description**: `Subject line of the email`

#### 3. email_body_html
- **Data type**: `String`
- **Identifier**: `email_body_html`
- **Required**: ✅ Yes
- **Value Type**: `LLM Prompt`
- **Description**: `HTML content of the email body. Use proper HTML formatting with tags like <p>, <b>, <ul>, etc.`

#### 4. save_to_sent_items
- **Data type**: `Boolean`
- **Identifier**: `save_to_sent_items`
- **Required**: ❌ No
- **Value Type**: `Static`
- **Value**: `true`
- **Description**: `Whether to save the email to the sent items folder (default: true)`

## Agent Instructions

Add these instructions to your agent's system prompt or configuration:

### For Scheduling:
```
When someone wants to schedule a consultation:
1. Ask for their full name and email address
2. Ask for their preferred date and time
3. Ask for their timezone (or default to America/New_York)
4. Convert the requested time to UTC format (YYYY-MM-DDTHH:MM:SSZ)
5. Calculate end time as 30 minutes after start time
6. Use the schedule_consultation tool with all collected information

Important: Always convert times to UTC before calling the tool. The event_type_id should always be 1837761.
```

### For Email:
```
When sending emails:
1. Use proper HTML formatting in the email body
2. Include professional greeting and closing
3. Format the email body with HTML tags for better presentation
4. Set save_to_sent_items to true to keep a record

Example email body format:
<html>
<body>
<p>Dear [Name],</p>
<p>Your consultation has been scheduled for [date/time].</p>
<p>Best regards,<br>
Your AI Assistant</p>
</body>
</html>
```

## Testing Your Tools

### Test Scheduling:
"I'd like to schedule a consultation. My name is John Doe, email is john@example.com, and I'm available tomorrow at 2 PM EST."

Expected agent behavior:
1. Confirms the information
2. Converts 2 PM EST to UTC
3. Calls schedule_consultation tool
4. Confirms the booking

### Test Email:
"Please send a confirmation email to john@example.com about our scheduled meeting."

Expected agent behavior:
1. Composes a professional email
2. Uses HTML formatting
3. Calls send_email tool
4. Confirms email sent

## Troubleshooting

### Common Issues:

1. **Invalid timezone**: Ensure timezone follows IANA format (e.g., "America/New_York" not "EST")
2. **Time format errors**: UTC times must be in format YYYY-MM-DDTHH:MM:SSZ
3. **HTML formatting**: Email bodies should use valid HTML tags

### Debugging:
- Check bridge server logs on Render.com
- Test bridge server directly: `curl https://elevenlabs-bridge-server.onrender.com/health`
- Verify environment variables are set correctly on Render

## Important Notes

1. The bridge server uses direct API integration (INTEGRATION_MODE=direct)
2. All times must be converted to UTC before sending
3. The agent should handle timezone conversions
4. Email bodies should be formatted in HTML for best results
5. The event_type_id (1837761) is specific to your Cal.com account

## Save Configuration

After entering all the details:
1. Click "Save changes" for each tool
2. Test the tools in a conversation
3. Monitor the bridge server logs for any errors
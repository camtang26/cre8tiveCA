# ElevenLabs Custom Tools Setup Guide

This guide will help you configure custom tools in your ElevenLabs Conversational AI agent to integrate with Cal.com and Outlook via your bridge server.

## Prerequisites

1. Your bridge server is deployed and running at: `https://elevenlabs-bridge-server.onrender.com`
2. You have access to your ElevenLabs agent at: `https://elevenlabs.io/app/conversational-ai/agents/lQXvJFg8zSqlerOKPXm6`

## Step 1: Navigate to Custom Tools

1. Log in to ElevenLabs
2. Go to your agent: https://elevenlabs.io/app/conversational-ai/agents/lQXvJFg8zSqlerOKPXm6
3. Look for "Tools" or "Custom Tools" section (usually in the left sidebar or under agent settings)

## Step 2: Add Cal.com Scheduling Tool

Click "Add Tool" or "Create Custom Tool" and configure:

### Basic Information
- **Tool Name**: `schedule_consultation`
- **Display Name**: Schedule Consultation
- **Description**: Schedule a consultation appointment using Cal.com

### Webhook Configuration
- **Method**: POST
- **URL**: `https://elevenlabs-bridge-server.onrender.com/webhook/cal/schedule_consultation`
- **Headers**: 
  ```json
  {
    "Content-Type": "application/json"
  }
  ```

### Input Schema
```json
{
  "type": "object",
  "properties": {
    "attendee_name": {
      "type": "string",
      "description": "Full name of the person scheduling the appointment"
    },
    "attendee_email": {
      "type": "string",
      "description": "Email address of the attendee"
    },
    "attendee_timezone": {
      "type": "string",
      "description": "Timezone of the attendee (e.g., America/New_York, Europe/London)",
      "default": "America/New_York"
    },
    "start_time_utc": {
      "type": "string",
      "description": "Appointment start time in UTC format (YYYY-MM-DDTHH:MM:SSZ)"
    },
    "end_time_utc": {
      "type": "string",
      "description": "Appointment end time in UTC format (YYYY-MM-DDTHH:MM:SSZ)"
    },
    "event_type_id": {
      "type": "integer",
      "description": "Cal.com event type ID",
      "default": 1837761
    },
    "guests": {
      "type": "array",
      "description": "Additional guest email addresses",
      "items": {
        "type": "string"
      },
      "default": []
    },
    "metadata": {
      "type": "object",
      "description": "Additional metadata for the booking",
      "default": {}
    },
    "language": {
      "type": "string",
      "description": "Language preference",
      "default": "en"
    }
  },
  "required": ["attendee_name", "attendee_email", "attendee_timezone", "start_time_utc", "end_time_utc"]
}
```

### Response Handling
- **Success Status Codes**: 200, 201
- **Extract Response Fields**: 
  - `message` - Confirmation message
  - `details` - Booking details object

## Step 3: Add Outlook Email Tool

Click "Add Tool" or "Create Custom Tool" and configure:

### Basic Information
- **Tool Name**: `send_email`
- **Display Name**: Send Email
- **Description**: Send an email via Outlook/Microsoft 365

### Webhook Configuration
- **Method**: POST
- **URL**: `https://elevenlabs-bridge-server.onrender.com/webhook/outlook/send_email`
- **Headers**: 
  ```json
  {
    "Content-Type": "application/json"
  }
  ```

### Input Schema
```json
{
  "type": "object",
  "properties": {
    "recipient_email": {
      "type": "string",
      "description": "Email address of the recipient"
    },
    "email_subject": {
      "type": "string",
      "description": "Subject line of the email"
    },
    "email_body_html": {
      "type": "string",
      "description": "HTML content of the email body"
    },
    "save_to_sent_items": {
      "type": "boolean",
      "description": "Whether to save the email to sent items folder",
      "default": true
    }
  },
  "required": ["recipient_email", "email_subject", "email_body_html"]
}
```

### Response Handling
- **Success Status Codes**: 200
- **Extract Response Fields**: 
  - `message` - Confirmation message
  - `messageId` - Email message ID

## Step 4: Configure Tool Usage in Agent

After adding both tools, configure your agent to use them:

1. **For Scheduling**: Train your agent to recognize scheduling intents and gather:
   - Name and email
   - Preferred date/time
   - Timezone (or default to a specific timezone)

2. **For Email**: Train your agent to recognize email sending intents and gather:
   - Recipient email
   - Subject
   - Message content

### Example Prompts for Your Agent

Add these to your agent's instructions or examples:

**Scheduling Examples:**
- "When someone wants to schedule a consultation, collect their name, email, and preferred time. Convert times to UTC format before calling the schedule_consultation tool."
- "Always ask for timezone or default to America/New_York if not specified."
- "Appointments are typically 30 minutes long."

**Email Examples:**
- "When sending confirmation emails, use the send_email tool with professional HTML formatting."
- "Always include a clear subject line and format the body with proper HTML tags."

## Step 5: Test Your Tools

1. Start a conversation with your agent
2. Test scheduling: "I'd like to schedule a consultation for tomorrow at 2 PM EST"
3. Test email: "Can you send a confirmation email to test@example.com"

## Troubleshooting

### Common Issues:

1. **401 Unauthorized**: Check that your bridge server has valid API credentials
2. **400 Bad Request**: Verify the data format, especially date/time formats
3. **500 Server Error**: Check bridge server logs on Render.com

### Testing the Bridge Server Directly:

```bash
# Test health endpoint
curl https://elevenlabs-bridge-server.onrender.com/health

# Test scheduling endpoint
curl -X POST https://elevenlabs-bridge-server.onrender.com/webhook/cal/schedule_consultation \
  -H "Content-Type: application/json" \
  -d '{
    "attendee_name": "Test User",
    "attendee_email": "test@example.com",
    "attendee_timezone": "America/New_York",
    "start_time_utc": "2025-01-28T19:00:00Z",
    "end_time_utc": "2025-01-28T19:30:00Z",
    "event_type_id": 1837761
  }'
```

## Notes

- The bridge server uses direct API integration (not MCP protocol)
- All times must be in UTC format (YYYY-MM-DDTHH:MM:SSZ)
- The agent should convert user's local time to UTC before calling the tool
- Email bodies should be in HTML format for proper formatting

## Support

- Check bridge server logs: Render.com dashboard
- API credentials are configured as environment variables on Render
- Ensure INTEGRATION_MODE=direct is set on your bridge server
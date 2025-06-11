# 🚨 Webhook Troubleshooting Guide

## Current Errors & Solutions

### 1. Schedule Tool Error: "no_available_users_found_error"

**What this means**: Cal.com can't find an available user for the event type.

**Solutions**:
1. **Verify Event Type ID**: 
   - Log into Cal.com dashboard
   - Go to Event Types
   - Find your consultation event
   - Check that the ID matches `1837761` (or update in Netlify env vars)

2. **Check Event Type Configuration**:
   - Ensure the event type is active/published
   - Verify it has available time slots
   - Check that it's assigned to at least one user
   - Ensure the user has availability for the requested time

3. **Test with Cal.com API directly**:
   ```bash
   curl -X GET "https://api.cal.com/v2/event-types/1837761" \
     -H "Authorization: Bearer YOUR_CAL_COM_API_KEY" \
     -H "cal-api-version: 2"
   ```

### 2. Email Tool Error: "Failed to obtain access token"

**What this means**: Azure credentials are missing or incorrect.

**Solutions**:

1. **Update ALL Azure Environment Variables in Netlify**:
   
   Go to: https://app.netlify.com/sites/cre8tiveai-elevenlabs-webhooks/settings/env
   
   Update these values (get from Azure Portal):
   - `AZURE_TENANT_ID`: Your Azure AD tenant ID
   - `AZURE_CLIENT_ID`: Your app registration client ID
   - `AZURE_CLIENT_SECRET`: Your app registration client secret
   - `SENDER_UPN`: The email address to send from (e.g., stuart@cre8tive.ai)

2. **Verify Azure App Permissions**:
   - Go to Azure Portal → App registrations
   - Find your app
   - Check API permissions include:
     - `Mail.Send`
     - `User.Read`
   - Ensure admin consent is granted

3. **Test Azure Auth**:
   ```bash
   curl -X POST "https://login.microsoftonline.com/YOUR_TENANT_ID/oauth2/v2.0/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET&scope=https://graph.microsoft.com/.default&grant_type=client_credentials"
   ```

## Quick Fix Checklist

### For Schedule Tool:
- [ ] Cal.com API key is correct (not placeholder)
- [ ] Event type ID 1837761 exists and is active
- [ ] Event type has available slots
- [ ] Event type is assigned to a user
- [ ] User has availability at requested time

### For Email Tool:
- [ ] Azure Tenant ID is set (format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
- [ ] Azure Client ID is set
- [ ] Azure Client Secret is set
- [ ] Sender UPN is a valid email address
- [ ] Azure app has Mail.Send permission

## How to Update Environment Variables

1. Go to: https://app.netlify.com/sites/cre8tiveai-elevenlabs-webhooks/settings/env
2. Click on each variable
3. Replace placeholder values with real ones
4. Click "Save"
5. Wait 30 seconds for changes to propagate
6. Test again

## Getting Your Credentials

### Cal.com API Key:
1. Log into Cal.com
2. Go to Settings → API Keys
3. Create new key or copy existing

### Azure Credentials:
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to Azure Active Directory → App registrations
3. Find your app (or create new)
4. Copy:
   - Directory (tenant) ID
   - Application (client) ID
5. Go to Certificates & secrets → New client secret
6. Copy the secret value (only shown once!)

## Test After Fixing

```bash
# Test schedule endpoint
curl -X POST https://cre8tiveai-elevenlabs-webhooks.netlify.app/api/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "start_time_utc": "2025-01-20T10:00:00Z",
    "end_time_utc": "2025-01-20T10:30:00Z",
    "attendee_timezone": "Australia/Brisbane",
    "attendee_name": "Test User",
    "attendee_email": "test@example.com",
    "event_type_id": 1837761
  }'

# Test email endpoint  
curl -X POST https://cre8tiveai-elevenlabs-webhooks.netlify.app/api/email \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "test@example.com",
    "email_subject": "Test Email",
    "email_body_html": "<p>This is a test</p>",
    "save_to_sent_items": true
  }'
```

## Need More Help?

1. Check Netlify function logs: https://app.netlify.com/sites/cre8tiveai-elevenlabs-webhooks/functions
2. The enhanced error messages will tell you exactly what's missing
3. Once you update the environment variables, the errors should resolve immediately

---

**Remember**: The edge functions are working perfectly - they just need the correct API credentials!
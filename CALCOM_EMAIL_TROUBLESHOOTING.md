# Cal.com Email Troubleshooting Guide

## Issue: Booking Created Successfully but No Confirmation Email

### What's Happening:
- ✅ Booking is created successfully (ID: 8476083)
- ✅ Webhook returns success
- ✅ Stuart's follow-up email is sent
- ❌ Cal.com confirmation email not received

### Possible Causes & Solutions:

## 1. Check Cal.com Event Type Settings

Log into Cal.com and navigate to your event type (ID: 1837761):

### Email Notifications Settings:
- [ ] Go to Event Types → Your Event → Workflows
- [ ] Check if "Send confirmation email to attendee" is enabled
- [ ] Check if "Send confirmation email to host" is enabled
- [ ] Verify email templates are configured

### Required Fields:
- [ ] Ensure "Email" field is marked as required
- [ ] Check if custom questions are blocking emails

## 2. Check Cal.com Account Settings

### Email Configuration:
- [ ] Go to Settings → Appearance → Branding
- [ ] Verify sender email is configured
- [ ] Check SMTP settings if using custom email

### Calendar Integration:
- [ ] Ensure calendar is connected (Google Calendar, Outlook, etc.)
- [ ] Calendar integration might be required for meeting links

## 3. Verify Booking Data

From the logs, your booking has:
- ✅ Valid email: wowcam26@gmail.com
- ✅ Status: ACCEPTED
- ⚠️ Location: "integrations:daily" (might need configuration)

### Meeting Location Issue:
The location shows as "integrations:daily" which suggests:
- Daily.co video integration might not be fully configured
- Meeting link might not be generated properly

## 4. Quick Fixes to Try:

### A. Update Event Type Location:
1. Go to Cal.com → Event Types → Edit your event
2. Under "Location", ensure it's set to:
   - Cal Video (built-in)
   - Or your preferred meeting platform
3. Save and test again

### B. Enable Email Workflows:
1. Go to Event Types → Workflows
2. Create new workflow:
   - Trigger: "When booking is confirmed"
   - Action: "Send Email"
   - To: "Attendee"
3. Configure email template

### C. Check Spam/Junk Folder:
- Cal.com emails might be going to spam
- Add cal.com to safe senders

## 5. API-Level Solutions:

If you need to force email sending, you could:

### Option A: Add Booking Metadata:
```javascript
// In schedule.ts, add to bookingData:
metadata: {
  ...payload.metadata,
  sendConfirmationEmail: true
}
```

### Option B: Use Cal.com Workflows API:
After booking creation, trigger a workflow to send email.

## 6. Alternative Approach:

Since Stuart already sends a confirmation email through your Outlook integration, you could:
1. Include all booking details in Stuart's email
2. Add the meeting link when available
3. This provides a consistent experience

## 7. Debug Steps:

1. **Check if booking appears in Cal.com dashboard**:
   - Log into Cal.com
   - Go to Bookings
   - Find booking ID: 8476083
   - Check its status and details

2. **Test with different email**:
   - Try booking with a different email address
   - See if behavior changes

3. **Check Cal.com logs**:
   - Cal.com dashboard → Settings → Developer
   - Check webhook logs for errors

## 8. Netlify Logs Missing Issue:

For the email function logs not showing:
- Edge Functions logs can have delays
- Try checking: https://app.netlify.com/sites/cre8tiveai-elevenlabs-webhooks/functions
- Filter by time range
- Logs might be under "Realtime" tab

## Summary:

The most likely issue is that Cal.com email notifications are either:
1. Disabled at the event type level
2. Blocked due to missing calendar/video integration
3. Going to spam

Since Stuart's email IS working, you have a functioning system. The Cal.com email is just a nice-to-have for the full experience.
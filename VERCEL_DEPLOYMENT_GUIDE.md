# Vercel Edge Functions Deployment Guide

## Prerequisites
- GitHub account
- Vercel account (free at vercel.com)
- Your existing API keys (Cal.com, Azure/Outlook)

## Step 1: Prepare the Code (5 minutes)

1. Create a new GitHub repository: `cre8tiveai-edge-webhooks`
2. Copy the `vercel-edge-implementation` folder contents to the new repo
3. Commit and push to GitHub

## Step 2: Deploy to Vercel (10 minutes)

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click "Add New..." → "Project"
3. Import your `cre8tiveai-edge-webhooks` repository
4. Vercel will auto-detect the configuration
5. Click "Deploy" (wait ~30 seconds)

## Step 3: Add Environment Variables (5 minutes)

In Vercel Dashboard → Settings → Environment Variables, add:

```bash
# Cal.com
CAL_COM_API_KEY=your-cal-com-api-key
DEFAULT_EVENT_TYPE_ID=1837761

# Microsoft/Outlook
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
SENDER_UPN=sender@yourdomain.com
```

Click "Save" after adding all variables.

## Step 4: Get Your Webhook URLs (2 minutes)

Your new webhook URLs will be:
- **Schedule**: `https://your-project.vercel.app/api/schedule`
- **Email**: `https://your-project.vercel.app/api/email`

Vercel provides automatic SSL and a custom domain if needed.

## Step 5: Update ElevenLabs Agent (10 minutes)

In your ElevenLabs agent configuration:

1. Update the `schedule_consultation` tool:
   ```
   URL: https://your-project.vercel.app/api/schedule
   Method: POST
   ```

2. Update the `send_email` tool:
   ```
   URL: https://your-project.vercel.app/api/email
   Method: POST
   ```

3. Save and test with a simple booking request

## Step 6: Test the System (5 minutes)

### Quick Test with cURL:

```bash
# Test scheduling
curl -X POST https://your-project.vercel.app/api/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "start_time_utc": "2025-01-15T14:00:00Z",
    "attendee_timezone": "Australia/Brisbane",
    "attendee_name": "Test User",
    "attendee_email": "test@example.com"
  }'

# Test email
curl -X POST https://your-project.vercel.app/api/email \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "test@example.com",
    "email_subject": "Test Email",
    "email_body_html": "<p>This is a test</p>"
  }'
```

## Monitoring & Logs

1. **Real-time Logs**: Vercel Dashboard → Functions → Logs
2. **Performance**: Vercel Dashboard → Analytics
3. **Errors**: Automatically captured and displayed

## Troubleshooting

### Issue: 401 Unauthorized
- **Fix**: Check API keys in environment variables
- **Verify**: Keys are correct and have proper permissions

### Issue: Timeout errors
- **Fix**: Shouldn't happen with Edge Functions!
- **Check**: API endpoints are responding

### Issue: CORS errors
- **Fix**: Add CORS headers if needed:
  ```js
  headers: {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json'
  }
  ```

## Migration Checklist

- [ ] Create new GitHub repository
- [ ] Copy edge function files
- [ ] Deploy to Vercel
- [ ] Add environment variables
- [ ] Update ElevenLabs webhooks
- [ ] Test scheduling function
- [ ] Test email function
- [ ] Monitor for 24 hours
- [ ] Shut down old Render services

## Performance Expectations

After deployment, you should see:
- **Response times**: 200-500ms (from 2-40 seconds!)
- **Uptime**: 99.9%
- **Cold starts**: None (Edge Functions stay warm)
- **Reliability**: Consistent performance globally

## Cost Summary

**Free Tier Includes**:
- 100,000 function invocations/month
- 100GB bandwidth
- Unlimited deployments
- Automatic SSL
- DDoS protection

**Your Usage** (estimated):
- 2,000 invocations/month (way under limit)
- <1GB bandwidth
- **Total Cost**: $0

## Next Steps

1. Deploy today (30 minutes total)
2. Test with real bookings
3. Monitor performance
4. Enjoy fast, reliable webhooks!

## Support

- **Vercel Docs**: docs.vercel.com
- **Edge Functions**: vercel.com/docs/functions/edge-functions
- **Cal.com API**: cal.com/docs/api-reference
- **Graph API**: docs.microsoft.com/graph
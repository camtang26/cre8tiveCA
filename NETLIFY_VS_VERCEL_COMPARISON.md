# Netlify Edge Functions vs Vercel/Regular Functions

## Key Differences That Could Affect Cal.com Emails

### 1. Runtime Environment
- **Netlify Edge Functions**: Run on Deno (not Node.js)
- **Vercel/Regular Functions**: Run on Node.js
- **Impact**: Different fetch API implementation, different SSL/TLS handling

### 2. Network Location
- **Edge Functions**: Execute at edge locations globally (distributed)
- **Regular Functions**: Execute from specific regions
- **Impact**: Different IP addresses, possible geo-blocking or IP whitelist issues

### 3. Request Origin
- **Edge Functions**: Requests come from edge network IPs
- **Regular Functions**: Requests come from datacenter IPs
- **Impact**: Cal.com might treat edge requests differently

### 4. HTTP Client Behavior
- **Edge Functions**: Use Deno's built-in fetch
- **Regular Functions**: Use node-fetch or native Node.js http
- **Impact**: Different default headers, SSL negotiation, keep-alive behavior

## What We've Deployed

### Option 1: Edge Function (Currently at /api/schedule)
- Located at: `netlify/edge-functions/schedule.ts`
- Runtime: Deno
- ❌ Not triggering Cal.com emails

### Option 2: Regular Function (New deployment at /api/schedule)
- Located at: `netlify/functions/schedule.js`
- Runtime: Node.js with node-fetch
- 🔄 Testing to see if this triggers emails

## Testing Strategy

1. **Test with Regular Function**: The new Node.js function should behave more like your working Vercel setup
2. **If Regular Function Works**: We know it's an Edge Function issue
3. **If Regular Function Fails**: The issue might be with Netlify's network/IP addresses

## Possible Solutions

### If Edge Functions are the Problem:
1. Use regular Netlify Functions (Node.js) instead
2. Add special headers to mimic non-edge requests
3. Use a proxy to make requests appear from a different origin

### If Netlify Network is the Problem:
1. Contact Cal.com to whitelist Netlify IPs
2. Use a different hosting provider
3. Route requests through a proxy service

## Next Steps

Test with the regular Netlify Function deployment and see if Cal.com emails are triggered. The endpoint remains the same:
```
https://cre8tiveai-elevenlabs-webhooks.netlify.app/api/schedule
```
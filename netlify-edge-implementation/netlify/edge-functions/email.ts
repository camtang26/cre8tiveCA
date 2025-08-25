import type { Context, Config } from "@netlify/edge-functions";

// Simple token cache to avoid repeated auth calls
let tokenCache: string | null = null;
let tokenExpiry = 0;

async function getAccessToken(): Promise<string> {
  // Return cached token if still valid
  if (tokenCache && Date.now() < tokenExpiry) {
    return tokenCache;
  }

  const tokenResponse = await fetch(
    `https://login.microsoftonline.com/${Netlify.env.get('AZURE_TENANT_ID')}/oauth2/v2.0/token`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        client_id: Netlify.env.get('AZURE_CLIENT_ID') || '',
        client_secret: Netlify.env.get('AZURE_CLIENT_SECRET') || '',
        scope: 'https://graph.microsoft.com/.default',
        grant_type: 'client_credentials'
      })
    }
  );

  const tokenData = await tokenResponse.json();
  if (tokenData.access_token) {
    tokenCache = tokenData.access_token;
    tokenExpiry = Date.now() + (tokenData.expires_in * 1000) - 60000; // Refresh 1 min early
    return tokenCache;
  }
  
  // Log the actual error from Azure for debugging
  console.error('Azure token error response:', JSON.stringify(tokenData));
  console.error('Token request details:', {
    tenant_id: Netlify.env.get('AZURE_TENANT_ID'),
    client_id: Netlify.env.get('AZURE_CLIENT_ID'),
    // Don't log the actual secret, just confirm it exists
    has_client_secret: !!Netlify.env.get('AZURE_CLIENT_SECRET'),
    secret_length: Netlify.env.get('AZURE_CLIENT_SECRET')?.length || 0
  });
  
  throw new Error(`Failed to obtain access token: ${tokenData.error || 'Unknown error'} - ${tokenData.error_description || 'No description'}`);
}

export default async (req: Request, context: Context) => {
  if (req.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 });
  }

  try {
    const payload = await req.json();
    
    // Check if Azure credentials are configured
    const tenantId = Netlify.env.get('AZURE_TENANT_ID');
    const clientId = Netlify.env.get('AZURE_CLIENT_ID');
    const clientSecret = Netlify.env.get('AZURE_CLIENT_SECRET');
    const senderUpn = Netlify.env.get('SENDER_UPN');
    
    if (!tenantId || tenantId === 'your-azure-tenant-id' || 
        !clientId || !clientSecret || !senderUpn) {
      console.error('Azure credentials not configured');
      return new Response(JSON.stringify({
        status: 'error',
        message: 'Azure credentials not configured. Please update environment variables in Netlify dashboard.',
        details: 'Missing or placeholder Azure credentials'
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    const accessToken = await getAccessToken();

    // Wrap content in professional template
    const emailBody = `
      <html>
      <head>
        <style>
          body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
          .container { max-width: 600px; margin: 0 auto; padding: 20px; }
          .header { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
          .content { margin: 20px 0; }
          .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #777; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="content">
            ${payload.email_body_html}
          </div>
          <div class="footer">
            <p>This email was sent by Cre8tive AI's automated system.</p>
          </div>
        </div>
      </body>
      </html>
    `;

    const emailResponse = await fetch(
      `https://graph.microsoft.com/v1.0/users/${Netlify.env.get('SENDER_UPN')}/sendMail`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: {
            subject: payload.email_subject,
            body: {
              contentType: 'HTML',
              content: emailBody
            },
            toRecipients: [{
              emailAddress: { address: payload.recipient_email }
            }]
          },
          saveToSentItems: payload.save_to_sent_items !== false
        })
      }
    );

    if (emailResponse.ok || emailResponse.status === 202) {
      return new Response(JSON.stringify({
        status: 'success',
        message: 'Email sent successfully',
        messageId: emailResponse.headers.get('x-ms-message-id') || 'sent'
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    } else {
      const error = await emailResponse.text();
      console.error('Graph API error:', error);
      return new Response(JSON.stringify({
        status: 'error',
        message: 'Failed to send email',
        details: error
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  } catch (error) {
    console.error('Edge function error:', error);
    return new Response(JSON.stringify({
      status: 'error',
      message: 'Internal server error',
      details: error.message
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

export const config: Config = {
  path: "/api/email"
};
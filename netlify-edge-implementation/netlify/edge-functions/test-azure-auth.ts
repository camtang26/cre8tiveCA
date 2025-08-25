import type { Context, Config } from "@netlify/edge-functions";

export default async (req: Request, context: Context) => {
  // Get all the Azure credentials
  const tenantId = Netlify.env.get('AZURE_TENANT_ID');
  const clientId = Netlify.env.get('AZURE_CLIENT_ID');
  const clientSecret = Netlify.env.get('AZURE_CLIENT_SECRET');
  
  // Debug info (without exposing the full secret)
  const debugInfo = {
    tenant_id: tenantId,
    client_id: clientId,
    has_client_secret: !!clientSecret,
    secret_length: clientSecret?.length || 0,
    secret_preview: clientSecret ? `${clientSecret.substring(0, 5)}...${clientSecret.substring(clientSecret.length - 5)}` : 'NOT SET'
  };
  
  // Try to get the token
  let tokenResult;
  try {
    const tokenResponse = await fetch(
      `https://login.microsoftonline.com/${tenantId}/oauth2/v2.0/token`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          client_id: clientId || '',
          client_secret: clientSecret || '',
          scope: 'https://graph.microsoft.com/.default',
          grant_type: 'client_credentials'
        })
      }
    );
    
    const tokenData = await tokenResponse.json();
    
    if (tokenData.access_token) {
      tokenResult = {
        success: true,
        message: 'Token obtained successfully!',
        token_preview: `${tokenData.access_token.substring(0, 20)}...`
      };
    } else {
      tokenResult = {
        success: false,
        error: tokenData.error || 'Unknown error',
        error_description: tokenData.error_description || 'No description',
        error_codes: tokenData.error_codes || [],
        full_response: tokenData
      };
    }
  } catch (error) {
    tokenResult = {
      success: false,
      error: 'Exception during token request',
      message: error.message
    };
  }
  
  return new Response(JSON.stringify({
    credentials: debugInfo,
    token_result: tokenResult
  }, null, 2), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  });
};

export const config: Config = {
  path: "/api/test-azure-auth"
};
import type { Context, Config } from "@netlify/edge-functions";

export default async (req: Request, context: Context) => {
  const envVars = {
    AZURE_TENANT_ID: {
      exists: !!Netlify.env.get('AZURE_TENANT_ID'),
      value: Netlify.env.get('AZURE_TENANT_ID') || 'NOT SET'
    },
    AZURE_CLIENT_ID: {
      exists: !!Netlify.env.get('AZURE_CLIENT_ID'),
      value: Netlify.env.get('AZURE_CLIENT_ID') || 'NOT SET'
    },
    AZURE_CLIENT_SECRET: {
      exists: !!Netlify.env.get('AZURE_CLIENT_SECRET'),
      length: Netlify.env.get('AZURE_CLIENT_SECRET')?.length || 0,
      preview: Netlify.env.get('AZURE_CLIENT_SECRET') 
        ? `${Netlify.env.get('AZURE_CLIENT_SECRET')!.substring(0, 5)}...` 
        : 'NOT SET'
    },
    SENDER_UPN: {
      exists: !!Netlify.env.get('SENDER_UPN'),
      value: Netlify.env.get('SENDER_UPN') || 'NOT SET'
    }
  };

  return new Response(JSON.stringify({
    message: "Environment variables debug info",
    env: envVars,
    timestamp: new Date().toISOString()
  }, null, 2), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  });
};

export const config: Config = {
  path: "/api/debug-env"
};
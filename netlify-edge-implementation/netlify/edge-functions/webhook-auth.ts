import crypto from 'crypto';

export function verifyWebhookSignature(
  payload: string,
  signature: string,
  secret: string
): boolean {
  if (!signature || !secret) {
    return false;
  }

  try {
    // ElevenLabs uses HMAC-SHA256 for webhook signatures
    const expectedSignature = crypto
      .createHmac('sha256', secret)
      .update(payload)
      .digest('hex');

    // Use timing-safe comparison to prevent timing attacks
    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(expectedSignature)
    );
  } catch (error) {
    console.error('Webhook signature verification error:', error);
    return false;
  }
}

export function requireWebhookAuth(req: Request, body: string): Response | null {
  const webhookSecret = Netlify.env.get('ELEVENLABS_WEBHOOK_SECRET');
  
  if (!webhookSecret) {
    console.error('ELEVENLABS_WEBHOOK_SECRET not configured');
    return new Response(JSON.stringify({
      status: 'error',
      message: 'Webhook authentication not configured'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const signature = req.headers.get('x-webhook-signature') || 
                    req.headers.get('x-elevenlabs-signature') ||
                    req.headers.get('x-signature');

  if (!signature) {
    return new Response('Unauthorized', { status: 401 });
  }

  if (!verifyWebhookSignature(body, signature, webhookSecret)) {
    console.error('Invalid webhook signature');
    return new Response('Unauthorized', { status: 401 });
  }

  // Authentication passed
  return null;
}
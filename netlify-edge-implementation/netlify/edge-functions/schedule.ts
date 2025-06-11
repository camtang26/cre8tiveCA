import type { Context, Config } from "@netlify/edge-functions";

export default async (req: Request, context: Context) => {
  if (req.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 });
  }

  try {
    const payload = await req.json();
    
    // Direct pass-through to Cal.com API v2
    const calcomResponse = await fetch('https://api.cal.com/v2/bookings', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${Netlify.env.get('CAL_COM_API_KEY')}`,
        'Content-Type': 'application/json',
        'cal-api-version': '2'
      },
      body: JSON.stringify({
        eventTypeId: parseInt(Netlify.env.get('DEFAULT_EVENT_TYPE_ID') || '1837761'),
        start: payload.start_time_utc,
        timeZone: payload.attendee_timezone,
        responses: {
          name: payload.attendee_name,
          email: payload.attendee_email
        },
        metadata: payload.metadata || {},
        language: payload.language || 'en'
      })
    });

    const result = await calcomResponse.json();

    if (calcomResponse.ok && result.status === 'success') {
      return new Response(JSON.stringify({
        status: 'success',
        message: 'Consultation booked successfully',
        details: {
          id: result.data.id,
          uid: result.data.uid,
          title: result.data.title,
          start_time: result.data.start,
          end_time: result.data.end,
          meet_url: result.data.meetingUrl
        }
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    } else {
      console.error('Cal.com API error:', result);
      return new Response(JSON.stringify({
        status: 'error',
        message: result.message || 'Failed to book consultation',
        details: result
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
  path: "/api/schedule"
};
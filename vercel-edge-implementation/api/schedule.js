/**
 * Vercel Edge Function for Cal.com scheduling
 * Ultra-fast, no cold starts, minimal complexity
 */

export const config = {
  runtime: 'edge',
  regions: ['syd1'], // Sydney for Australian users
};

export default async function handler(request) {
  if (request.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 });
  }

  try {
    const payload = await request.json();
    
    // Direct pass-through to Cal.com API v2 - no complex transformations
    const calcomResponse = await fetch('https://api.cal.com/v2/bookings', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.CAL_COM_API_KEY}`,
        'Content-Type': 'application/json',
        'cal-api-version': '2'
      },
      body: JSON.stringify({
        eventTypeId: parseInt(process.env.DEFAULT_EVENT_TYPE_ID || '1837761'),
        start: payload.start_time_utc, // Cal.com accepts UTC directly
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
      // Cal.com API returned an error
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
const fetch = require('node-fetch');

exports.handler = async (event, context) => {
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: 'Method not allowed'
    };
  }

  try {
    const payload = JSON.parse(event.body);
    
    // Check if API key is set
    const apiKey = process.env.CAL_COM_API_KEY;
    if (!apiKey || apiKey === 'your-cal-com-api-key-here') {
      console.error('Cal.com API key not configured');
      return {
        statusCode: 500,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: 'error',
          message: 'Cal.com API key not configured. Please update environment variables in Netlify dashboard.',
          details: 'Missing or placeholder API key'
        })
      };
    }
    
    // Cal.com API v2 booking structure - exactly as the documentation shows
    const bookingData = {
      eventTypeId: parseInt(process.env.DEFAULT_EVENT_TYPE_ID || '1837761'),
      start: payload.start_time_utc,
      // NO end time - Cal.com calculates it from event type duration
      // NO timeZone at root level
      // NO language at root level
      attendee: {
        name: payload.attendee_name,
        email: payload.attendee_email,
        timeZone: payload.attendee_timezone,
        language: payload.language || 'en'
      },
      metadata: payload.metadata || {}
    };
    
    console.log('Sending to Cal.com:', JSON.stringify(bookingData, null, 2));
    
    // Make request to Cal.com API v2
    const calcomResponse = await fetch('https://api.cal.com/v2/bookings', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'cal-api-version': '2024-08-13',
        'User-Agent': 'Cre8tiveAI/1.0 (Netlify Functions)',
        'Accept': 'application/json'
      },
      body: JSON.stringify(bookingData)
    });

    const result = await calcomResponse.json();
    console.log('Cal.com response:', JSON.stringify(result, null, 2));

    if (calcomResponse.ok && result.status === 'success') {
      return {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: 'success',
          message: 'Consultation booked successfully',
          details: {
            id: result.data.id,
            uid: result.data.uid,
            title: result.data.title,
            start_time: result.data.startTime,
            end_time: result.data.endTime,
            meet_url: result.data.meetingUrl || result.data.location || 'Check your email for meeting details',
            status: result.data.status,
            user_email: result.data.userPrimaryEmail
          }
        })
      };
    } else {
      console.error('Cal.com API error:', result);
      return {
        statusCode: 400,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: 'error',
          message: result.message || result.error || 'Failed to book consultation',
          details: result
        })
      };
    }
  } catch (error) {
    console.error('Function error:', error);
    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        status: 'error',
        message: 'Internal server error',
        details: error.message
      })
    };
  }
};
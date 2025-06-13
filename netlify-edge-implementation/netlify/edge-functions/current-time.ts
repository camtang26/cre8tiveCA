import type { Context, Config } from "@netlify/edge-functions";

export default async (req: Request, context: Context) => {
  // Allow both GET and POST for flexibility
  if (req.method !== 'GET' && req.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 });
  }

  try {
    // Get current UTC time
    const now = new Date();
    
    // Get timezone from query params or body (default to Australia/Brisbane)
    let timezone = 'Australia/Brisbane';
    
    if (req.method === 'GET') {
      const url = new URL(req.url);
      timezone = url.searchParams.get('timezone') || timezone;
    } else {
      try {
        const body = await req.json();
        timezone = body.timezone || timezone;
      } catch {
        // If no body or invalid JSON, use default timezone
      }
    }
    
    // Get current time in the specified timezone
    const formatter = new Intl.DateTimeFormat('en-AU', {
      timeZone: timezone,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
      weekday: 'long'
    });
    
    const parts = formatter.formatToParts(now);
    const dateInfo: any = {};
    parts.forEach(part => {
      if (part.type !== 'literal') {
        dateInfo[part.type] = part.value;
      }
    });
    
    // Calculate useful relative dates
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    const dayAfterTomorrow = new Date(now);
    dayAfterTomorrow.setDate(dayAfterTomorrow.getDate() + 2);
    
    const nextWeek = new Date(now);
    nextWeek.setDate(nextWeek.getDate() + 7);
    
    const response = {
      current_time: {
        utc: now.toISOString(),
        utc_timestamp: now.getTime(),
        timezone: timezone,
        local: formatter.format(now),
        year: parseInt(dateInfo.year),
        month: parseInt(dateInfo.month),
        day: parseInt(dateInfo.day),
        hour: parseInt(dateInfo.hour),
        minute: parseInt(dateInfo.minute),
        second: parseInt(dateInfo.second),
        weekday: dateInfo.weekday,
        is_am: dateInfo.dayPeriod === 'am',
        day_period: dateInfo.dayPeriod
      },
      relative_dates: {
        today: {
          date: now.toISOString().split('T')[0],
          weekday: dateInfo.weekday
        },
        tomorrow: {
          date: tomorrow.toISOString().split('T')[0],
          weekday: formatter.formatToParts(tomorrow).find(p => p.type === 'weekday')?.value
        },
        day_after_tomorrow: {
          date: dayAfterTomorrow.toISOString().split('T')[0],
          weekday: formatter.formatToParts(dayAfterTomorrow).find(p => p.type === 'weekday')?.value
        },
        next_week: {
          date: nextWeek.toISOString().split('T')[0],
          weekday: formatter.formatToParts(nextWeek).find(p => p.type === 'weekday')?.value
        }
      },
      useful_info: {
        current_date_string: `${dateInfo.weekday}, ${dateInfo.day}/${dateInfo.month}/${dateInfo.year}`,
        current_time_string: `${dateInfo.hour}:${dateInfo.minute} ${dateInfo.dayPeriod}`,
        iso_date: now.toISOString().split('T')[0],
        business_hours: {
          is_business_hours: parseInt(dateInfo.hour) >= 9 && parseInt(dateInfo.hour) < 17 && !['Saturday', 'Sunday'].includes(dateInfo.weekday),
          next_business_day: ['Friday', 'Saturday', 'Sunday'].includes(dateInfo.weekday) ? 'Monday' : 'Tomorrow'
        }
      }
    };
    
    return new Response(JSON.stringify(response), {
      status: 200,
      headers: { 
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate'
      }
    });
  } catch (error) {
    console.error('Time function error:', error);
    return new Response(JSON.stringify({
      status: 'error',
      message: 'Failed to get current time',
      details: error.message
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

export const config: Config = {
  path: "/api/current-time"
};
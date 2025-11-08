// Get credentials from HTTP Request Authorization header
const authHeader = $input.first().json.headers.Authorization;
const decoded = Buffer.from(authHeader.replace('Basic ', ''), 'base64').toString('utf-8');
const [EMAIL, PASSWORD] = decoded.split(':');

// Your IDs
const USER_ID = 'your-user-id';
const CALENDAR_ID = 'your-calendar-id';
const BASE_URL = `https://caldav.icloud.com/${USER_ID}/calendars/${CALENDAR_ID}`;

const eventUid = `icloud-${Date.now()}`;
const now = new Date();
const dtstamp = now.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';

// Get event data
const start = $('Edit Fields').first().json.start;
const end = $('Edit Fields').first().json.eind;
const name = $('Edit Fields').first().json.Eventnaam;
const desc = $('Edit Fields').first().json.omschrijving;

const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//EN
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:${eventUid}
DTSTAMP:${dtstamp}
DTSTART:${start}
DTEND:${end}
SUMMARY:${name}
DESCRIPTION:${desc}
END:VEVENT
END:VCALENDAR`;

const eventUrl = `${BASE_URL}/event-${eventUid}.ics`;
const credentials = Buffer.from(`${EMAIL}:${PASSWORD}`).toString('base64');

try {
  const response = await this.helpers.request({
    method: 'PUT',
    url: eventUrl,
    body: icsContent,
    headers: {
      'Content-Type': 'text/calendar',
      'Authorization': `Basic ${credentials}`
    }
  });
  
  return { 
    status: 201, 
    success: true,
    uid: eventUid,
    message: 'Event created'
  };
} catch (error) {
  return {
    status: error.statusCode || 500,
    success: false,
    error: error.message
  };
}
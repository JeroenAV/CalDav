const EMAIL = 'your-email@icloud.com';
const PASSWORD = 'your-app-specific-password';
const USER_ID = 'your-user-id';  // From Step 2
const CALENDAR_ID = 'your-calendar-id';  // From Step 3

const BASE_URL = `https://caldav.icloud.com/${USER_ID}/calendars/${CALENDAR_ID}`;
const eventUid = `icloud-${Date.now()}`;
const now = new Date();
const dtstamp = now.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';

const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//n8n//EN
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:${eventUid}
DTSTAMP:${dtstamp}
DTSTART:${$input.first().json.start}
DTEND:${$input.first().json.eind}
SUMMARY:${$input.first().json.Eventnaam}
DESCRIPTION:${$input.first().json.omschrijving}
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
# CalDAV iCloud Calendar - Complete Setup Summary

## Quick Overview

Integrate iCloud Calendar with n8n using CalDAV to automatically create events.

---

## Prerequisites

1. ✅ iCloud account with Calendar
2. ✅ App-specific password generated from https://appleid.apple.com

---

## Step 1: Get Your Credentials

### Generate App-Specific Password
1. Go to https://appleid.apple.com
2. Security → App-specific passwords
3. Generate password for "n8n"
4. Copy 16-character password

### Find USER_ID
Run this Python script:
```python
import requests
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree as ET

EMAIL = input("Email: ")
PASSWORD = input("Password: ")

response = requests.request(
    'PROPFIND',
    'https://caldav.icloud.com/.well-known/caldav',
    auth=HTTPBasicAuth(EMAIL, PASSWORD),
    timeout=10
)

root = ET.fromstring(response.content)
href = root.findall('.//{DAV:}href')[0].text
USER_ID = href.split('/')[1]
print(f"USER_ID: {USER_ID}")
```

### Find CALENDAR_ID
Run this Python script:
```python
import requests
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree as ET

EMAIL = input("Email: ")
PASSWORD = input("Password: ")
USER_ID = input("USER_ID: ")

response = requests.request(
    'PROPFIND',
    f'https://caldav.icloud.com/{USER_ID}/calendars/',
    auth=HTTPBasicAuth(EMAIL, PASSWORD),
    headers={'Depth': '1'},
    timeout=10
)

root = ET.fromstring(response.content)
hrefs = root.findall('.//{DAV:}href')

for i, href in enumerate(hrefs, 1):
    print(f"{i}. {href.text}")
    
print("\nUse one of the UUID calendars (skip inbox, notification, outbox)")
```

---

## Step 2: Your Configuration

```javascript
const EMAIL = 'your-email@icloud.com';
const PASSWORD = 'your-app-specific-password';
const USER_ID = 'your-user-id-from-step-1';
const CALENDAR_ID = 'your-calendar-uuid-from-step-1';
```

---

## Step 3: n8n Workflow Setup

### Node 1: Edit Fields
Collects event data
- Input fields: `start`, `eind`, `Eventnaam`, `omschrijving`

### Node 2: HTTP Request
**Authentication Setup**
- Method: GET
- URL: `https://caldav.icloud.com/`
- Auth: Basic Auth
  - Username: Your iCloud email
  - Password: Your app-specific password

### Node 3: Function Node
**Code:**
```javascript
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
```

---

## Step 4: DateTime Format

**Critical:** Use format `YYYYMMDDTHHmmssZ` (no colons)

```
Correct:   20251110T100000Z
Wrong:     20251110T10:00:00Z
```

---

## Step 5: Test Your Workflow

1. Fill in Edit Fields with test event
2. Run HTTP Request node
3. Run Function node
4. Check iCloud Calendar for new event
5. Verify response: `{ "success": true }`

---

## Workflow Diagram

```
┌─────────────────┐
│  Edit Fields    │
│  (Event Data)   │
└────────┬────────┘
         │
┌────────▼─────────────┐
│  HTTP Request       │
│  (Get Auth Header)  │
└────────┬─────────────┘
         │
┌────────▼──────────────┐
│  Function Node       │
│  (Create Event)      │
└────────┬──────────────┘
         │
┌────────▼──────────────┐
│  iCloud Calendar     │
│  (Event Created)     │
└──────────────────────┘
```

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| 403 Forbidden | Regenerate app-specific password |
| 401 Unauthorized | Check email and password |
| Wrong event time | Use correct datetime format (no colons) |
| `$input.first()` undefined | Make sure HTTP Request node comes before Function node |

---

## Security Best Practices

- ⚠️ Never hardcode credentials
- ⚠️ Use n8n environment variables
- ⚠️ Regenerate passwords after sharing
- ✅ Use separate app-specific passwords per application

---

## Summary Table

| Item | Value |
|------|-------|
| CalDAV Server | `https://caldav.icloud.com` |
| Discovery Endpoint | `https://caldav.icloud.com/.well-known/caldav` |
| Event Creation | PUT to `/USER_ID/calendars/CALENDAR_ID/event.ics` |
| Auth Method | Basic Auth (Email:Password) |
| Event Format | iCalendar (RFC 5545) |
| Status on Success | 201 Created |

---

## Files Generated

1. ✅ Edit Fields Node - Collects event data
2. ✅ HTTP Request Node - Provides authentication
3. ✅ Function Node - Creates CalDAV event
4. ✅ Event Format - iCalendar (.ics)
5. ✅ Response - JSON with status and event UID
# CalDAV iCloud Calendar Setup Guide - Complete Steps

## Overview
This guide shows how to integrate iCloud Calendar with n8n using CalDAV to automatically create and read calendar events.

---

## Step 1: Generate App-Specific Password

1. Go to https://appleid.apple.com
2. Sign in with your Apple ID
3. Click **"Security"**
4. Under **"App-specific passwords"**, click **"Generate password"**
5. Select **"Other App"** and name it "n8n"
6. Copy the 16-character password (format: `abcd-efgh-ijkl-mnop`)

---

## Step 2: Discover Your USER_ID Using .well-known/caldav

Run this Python script:

```python
#!/usr/bin/env python3
import requests
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree as ET

EMAIL = input("Enter your iCloud email: ")
PASSWORD = input("Enter your app-specific password: ")

response = requests.request(
    'PROPFIND',
    'https://caldav.icloud.com/.well-known/caldav',
    auth=HTTPBasicAuth(EMAIL, PASSWORD),
    timeout=10
)

if response.status_code == 207:
    root = ET.fromstring(response.content)
    hrefs = root.findall('.//{DAV:}href')
    
    if hrefs:
        principal_path = hrefs[0].text
        user_id = principal_path.split('/')[1]
        
        print("\n" + "=" * 60)
        print("✓ CalDAV Discovery Successful!")
        print("=" * 60)
        print(f"\nUSER_ID: {user_id}")
        print(f"Principal: {principal_path}")
        print(f"\nUse this in your n8n code:")
        print(f"const USER_ID = '{user_id}';")
        print("\n" + "=" * 60 + "\n")
    else:
        print("✗ No href found in response")
else:
    print(f"✗ Status: {response.status_code}")
    print(f"Response: {response.text}")
```

**Output example:**
```
✓ CalDAV Discovery Successful!
============================================================
USER_ID: 22700660884
Principal: /22700660884/principal/

Use this in your n8n code:
const USER_ID = '22700660884';
============================================================
```

---

## Step 3: Find Your CALENDAR_ID

Run this Python script with the USER_ID from Step 2:

```python
#!/usr/bin/env python3
import requests
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree as ET

EMAIL = input("Enter your iCloud email: ")
PASSWORD = input("Enter your app-specific password: ")
USER_ID = input("Enter your USER_ID: ")

response = requests.request(
    'PROPFIND',
    f'https://caldav.icloud.com/{USER_ID}/calendars/',
    auth=HTTPBasicAuth(EMAIL, PASSWORD),
    headers={'Depth': '1'},
    timeout=10
)

if response.status_code == 207:
    root = ET.fromstring(response.content)
    hrefs = root.findall('.//{DAV:}href')
    
    print("\n" + "=" * 60)
    print(f"Found {len(hrefs)} calendars:")
    print("=" * 60 + "\n")
    
    calendar_ids = []
    for i, href in enumerate(hrefs, 1):
        href_text = href.text
        # Extract calendar ID (UUID format)
        if '{' in href_text and '}' in href_text:
            calendar_id = href_text.split('/')[-2]
            calendar_ids.append(calendar_id)
            print(f"{i}. Calendar ID: {calendar_id}")
            print(f"   Path: {href_text}\n")
    
    if calendar_ids:
        print("=" * 60)
        print("Use the first calendar ID in your n8n code:")
        print(f"const CALENDAR_ID = '{calendar_ids[0]}';")
        print("=" * 60 + "\n")
else:
    print(f"✗ Status: {response.status_code}")
```

**Output example:**
```
Found 8 calendars:
============================================================

1. Calendar ID: 0E81B09C-6532-4EB3-AA0B-ECAB443E8BBA
   Path: /22700660884/calendars/0E81B09C-6532-4EB3-AA0B-ECAB443E8BBA/

2. Calendar ID: 134CFDC5-A1E0-48A8-99C4-E10EA6C5601F
   Path: /22700660884/calendars/134CFDC5-A1E0-48A8-99C4-E10EA6C5601F/

...

============================================================
Use the first calendar ID in your n8n code:
const CALENDAR_ID = '0E81B09C-6532-4EB3-AA0B-ECAB443E8BBA';
============================================================
```

---

## Step 4: Create Events in n8n - Function Node

Add this code to an n8n **Function node**:

```javascript
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
```

**Input from previous node (required fields):**
```json
{
  "start": "20251110T100000Z",
  "eind": "20251110T110000Z",
  "Eventnaam": "Event Title",
  "omschrijving": "Event Description"
}
```

---

## Step 5: DateTime Format

**Critical:** Use this exact format for dates (NO colons):

- **Correct format:** `YYYYMMDDTHHmmssZ`
  - Example: `20251110T060000Z` = November 10, 2025 at 6:00 AM UTC
  
- **Wrong format:** `20251110T06:00:00Z` (will create events at wrong time)

---

## Step 6: Read Calendar Events

Use this Python script to list all events:

```python
#!/usr/bin/env python3
import requests
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree as ET

EMAIL = 'your-email@icloud.com'
PASSWORD = 'your-app-specific-password'
USER_ID = 'your-user-id'
CALENDAR_ID = 'your-calendar-id'

BASE_URL = f'https://caldav.icloud.com/{USER_ID}/calendars/{CALENDAR_ID}'

response = requests.request(
    'PROPFIND',
    BASE_URL,
    auth=HTTPBasicAuth(EMAIL, PASSWORD),
    headers={'Depth': '1'},
    timeout=10
)

if response.status_code == 207:
    root = ET.fromstring(response.content)
    hrefs = root.findall('.//{DAV:}href')
    
    print(f"Found {len(hrefs)} events:\n")
    for href in hrefs:
        print(href.text)
else:
    print(f"Status: {response.status_code}")
```

---

## Summary of Configuration

Your complete CalDAV configuration:

```javascript
const EMAIL = 'your-email@icloud.com';
const PASSWORD = 'your-app-specific-password';
const USER_ID = 'your-user-id';  // From Step 2
const CALENDAR_ID = 'your-calendar-id';  // From Step 3 (use main calendar)
```

**Available Calendars (from Step 3):**

| # | Calendar ID | Type | Use? |
|---|---|---|---|
| 1 | `/your-user-id/calendars/` | Root folder | ❌ No |
| 2 | `UUID-CALENDAR-1` | Main Calendar | ✅ **Recommended** |
| 3 | `UUID-CALENDAR-2` | Calendar | ✅ Yes |
| 4 | `UUID-CALENDAR-3` | Calendar | ✅ Yes |
| 5 | `inbox` | Inbox | ❌ No |
| 6 | `notification` | Notifications | ❌ No |
| 7 | `outbox` | Outbox | ❌ No |
| 8 | `UUID-CALENDAR-4` | Calendar | ✅ Yes |

**Copy this to your n8n Function node:**

| Item | Value |
|------|-------|
| EMAIL | `your-email@icloud.com` |
| PASSWORD | Your app-specific password |
| USER_ID | From Step 2 output |
| CALENDAR_ID | First UUID calendar from Step 3 |
| Base URL | `https://caldav.icloud.com/{USER_ID}/calendars/{CALENDAR_ID}` |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 207 Status in Step 2 | ✓ Good! Extract USER_ID from response |
| 403 Forbidden | Regenerate app-specific password |
| 401 Unauthorized | Check email and password are correct |
| 501 Not Implemented | Make sure using PUT method, not POST |
| Wrong event time | Check datetime format (no colons: `YYYYMMDDTHHmmssZ`) |
| CalDAV disabled | Account restrictions - contact Apple Support |

---

## Security Notes

- ⚠️ **Never** commit passwords to version control
- ⚠️ Store credentials in n8n environment variables
- ⚠️ Regenerate app-specific passwords after sharing
- ✅ Use separate app-specific passwords for different applications
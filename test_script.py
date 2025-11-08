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
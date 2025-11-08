#!/usr/bin/env python3
import requests
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree as ET

EMAIL = "Enter your iCloud email"
PASSWORD = "Enter your app-specific password"
USER_ID = "Enter your USER_ID"

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
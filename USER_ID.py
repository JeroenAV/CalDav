#!/usr/bin/env python3
import requests
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree as ET

# New user credentials
EMAIL = "Enter your iCloud email"
PASSWORD = "Enter your app-specific password"

print("\n" + "=" * 60)
print("Finding CalDAV Calendar ID")
print("=" * 60)

# Step 1: Test authentication
print("\n[STEP 1] Testing authentication...")
try:
    response = requests.request(
        'PROPFIND',
        'https://caldav.icloud.com/',
        auth=HTTPBasicAuth(EMAIL, PASSWORD),
        timeout=10
    )
    if response.status_code == 207:
        print("✓ Authentication successful!")
    else:
        print(f"✗ Auth failed: {response.status_code}")
        exit()
except Exception as e:
    print(f"✗ Error: {e}")
    exit()

# Step 2: Get calendars using USER_ID
print(f"\n[STEP 2] Finding calendars for USER_ID: {USER_ID}...")
try:
    calendar_url = f'https://caldav.icloud.com/{USER_ID}/calendars/'
    response = requests.request(
        'PROPFIND',
        calendar_url,
        auth=HTTPBasicAuth(EMAIL, PASSWORD),
        headers={'Depth': '1'},
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 207:
        root = ET.fromstring(response.content)
        hrefs = root.findall('.//{DAV:}href')
        
        if hrefs:
            print(f"\n✓ Found {len(hrefs)} calendars:\n")
            calendar_ids = []
            for i, href in enumerate(hrefs, 1):
                href_text = href.text
                print(f"  {i}. {href_text}")
                # Extract calendar ID (UUID format)
                if '{' in href_text and '}' in href_text:
                    calendar_id = href_text.split('/')[-2]
                    calendar_ids.append(calendar_id)
                    print(f"     Calendar ID: {calendar_id}\n")
            
            print("\n" + "=" * 60)
            print("USE THESE VALUES IN YOUR N8N CODE:")
            print("=" * 60)
            print(f"\nconst EMAIL = '{EMAIL}';")
            print(f"const PASSWORD = '{PASSWORD}';")
            print(f"const USER_ID = '{USER_ID}';")
            print(f"const CALENDAR_ID = '{calendar_ids[0]}'; // Main calendar")
            print(f"const BASE_URL = `https://caldav.icloud.com/${{USER_ID}}/calendars/${{CALENDAR_ID}}`;")
            print(f"\n{'=' * 60}\n")
        else:
            print("✗ No calendars found in response")
    else:
        print(f"✗ Failed: {response.status_code}")
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"✗ Error: {e}")
    exit()
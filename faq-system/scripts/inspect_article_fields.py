#!/usr/bin/env python3
"""
Quick script to inspect what fields are available on internal articles
"""

import json
import os
import requests
import time

INTERCOM_ACCESS_TOKEN = os.environ.get("INTERCOM_ACCESS_TOKEN")
INTERCOM_API_BASE = "https://api.intercom.io"

headers = {
    "Authorization": f"Bearer {INTERCOM_ACCESS_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Intercom-Version": "Unstable"
}

# Fetch one internal article to inspect fields
response = requests.get(
    f"{INTERCOM_API_BASE}/internal_articles",
    headers=headers,
    params={"page": 1, "per_page": 1}
)

if response.status_code == 200:
    data = response.json()
    articles = data.get("data", [])

    if articles:
        print("Sample Internal Article Fields:")
        print("=" * 70)
        print(json.dumps(articles[0], indent=2))
else:
    print(f"Error: {response.status_code}")
    print(response.text)

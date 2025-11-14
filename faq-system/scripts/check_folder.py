#!/usr/bin/env python3
"""Quick check to see if articles have folder_id set"""

import requests
import os

INTERCOM_ACCESS_TOKEN = os.environ.get("INTERCOM_ACCESS_TOKEN")
INTERCOM_API_BASE = "https://api.intercom.io"

headers = {
    "Authorization": f"Bearer {INTERCOM_ACCESS_TOKEN}",
    "Accept": "application/json",
    "Intercom-Version": "Unstable"
}

# Get a specific article
response = requests.get(
    f"{INTERCOM_API_BASE}/internal_articles/5623397",  # One of the articles we moved
    headers=headers
)

if response.status_code == 200:
    article = response.json()
    print(f"Article ID: {article.get('id')}")
    print(f"Title: {article.get('title')}")
    print(f"Folder ID: {article.get('folder_id')}")
    print(f"\nFolder successfully set!" if article.get('folder_id') == 2703344 else "⚠️ Folder not set correctly")
else:
    print(f"Error: {response.status_code}")
    print(response.text)

#!/usr/bin/env python3
"""Search for internal articles in a specific folder"""

import requests
import os

INTERCOM_ACCESS_TOKEN = os.environ.get("INTERCOM_ACCESS_TOKEN")
INTERCOM_API_BASE = "https://api.intercom.io"
FOLDER_ID = 2703344

headers = {
    "Authorization": f"Bearer {INTERCOM_ACCESS_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Intercom-Version": "Unstable"
}

# Search for articles in the folder
response = requests.get(
    f"{INTERCOM_API_BASE}/internal_articles/search",
    headers=headers,
    params={"folder_id": FOLDER_ID}
)

if response.status_code == 200:
    data = response.json()
    articles = data.get("data", [])
    print(f"Articles in folder {FOLDER_ID}: {len(articles)}")

    if articles:
        print("\nFirst 5 articles:")
        for article in articles[:5]:
            print(f"  - {article.get('title')[:60]}")
        print(f"\n✓ Articles are successfully in the folder!")
    else:
        print("\n⚠️ No articles found in folder")
else:
    print(f"Error: {response.status_code}")
    print(response.text)

#!/usr/bin/env python3
"""
Inspect all available fields in internal articles
"""

import json
import os
import requests

INTERCOM_ACCESS_TOKEN = os.environ.get("INTERCOM_ACCESS_TOKEN")
INTERCOM_API_BASE = "https://api.intercom.io"

headers = {
    "Authorization": f"Bearer {INTERCOM_ACCESS_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Intercom-Version": "Unstable"
}

# Fetch multiple internal articles to inspect fields
response = requests.get(
    f"{INTERCOM_API_BASE}/internal_articles",
    headers=headers,
    params={"page": 1, "per_page": 5}
)

if response.status_code == 200:
    data = response.json()
    articles = data.get("data", [])

    if articles:
        print("Available fields in internal articles:")
        print("=" * 70)

        # Get all unique keys from all articles
        all_keys = set()
        for article in articles:
            all_keys.update(article.keys())

        for key in sorted(all_keys):
            print(f"  - {key}")

        print("\n" + "=" * 70)
        print(f"\nSample article (first one) with all fields:")
        print(json.dumps(articles[0], indent=2))
else:
    print(f"Error: {response.status_code}")
    print(response.text)

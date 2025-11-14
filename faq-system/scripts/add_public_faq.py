#!/usr/bin/env python3
"""
Add a public FAQ article to Intercom Help Center
"""

import json
import os
import requests
import time


INTERCOM_ACCESS_TOKEN = os.environ.get("INTERCOM_ACCESS_TOKEN")
INTERCOM_API_BASE = "https://api.intercom.io"


def create_public_article(title: str, body: str, description: str = ""):
    """Create a public article in Intercom Help Center."""

    headers = {
        "Authorization": f"Bearer {INTERCOM_ACCESS_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Intercom-Version": "2.10"
    }

    payload = {
        "title": title,
        "description": description,
        "body": body,
        "author_id": 9277214,  # John Ellison
        "state": "published",
        "translate_content": False
    }

    print(f"Creating public article: {title}")
    print()

    response = requests.post(
        f"{INTERCOM_API_BASE}/articles",
        headers=headers,
        json=payload
    )

    if response.status_code in [200, 201]:
        article = response.json()
        print(f"✓ Article created successfully!")
        print(f"  Article ID: {article.get('id')}")
        print(f"  Title: {article.get('title')}")
        print(f"  State: {article.get('state')}")
        return article
    else:
        print(f"✗ Error creating article: {response.status_code}")
        print(f"  Response: {response.text}")
        return None


def main():
    """Create the rent-to-rent FAQ article."""

    if not INTERCOM_ACCESS_TOKEN:
        print("❌ INTERCOM_ACCESS_TOKEN not set")
        return

    print("=" * 80)
    print("Creating Public FAQ Article - Rent-to-Rent Holiday Lets")
    print("=" * 80)
    print()

    # Article content with excellent formatting
    title = "Can I get holiday let insurance if I'm renting the property (rent-to-rent)?"

    description = "Information about insurance options for rent-to-rent holiday let operators, including top-up coverage and public liability."

    body = """<h2>Understanding Rent-to-Rent Holiday Let Insurance</h2>

<p>If you're operating a short-term holiday let in a property you're renting (known as "rent-to-rent"), you have specific insurance needs that differ from traditional property owners.</p>

<h2>Can Pikl insure my rent-to-rent property?</h2>

<p><strong>Unfortunately, we cannot provide main buildings and contents insurance for rent-to-rent situations.</strong></p>

<p>This is because:</p>
<ul>
<li>You don't own the property</li>
<li>Standard landlord policies require the policyholder to be the property owner</li>
<li>Buildings insurance must be held by the property owner</li>
</ul>

<h2>What insurance options do I have?</h2>

<p>Great news! You can still protect your hosting business with our <strong>Top-Up Coverage</strong>.</p>

<h3>✅ Pikl Top-Up Coverage</h3>

<p>Our top-up policy is specifically designed for hosting activities and includes:</p>
<ul>
<li><strong>Public Liability Insurance</strong> - Covers claims from guests for injury or property damage</li>
<li><strong>Hosting-Specific Protection</strong> - Coverage tailored to short-term letting risks</li>
<li>Additional hosting-related benefits</li>
</ul>

<h3>📋 Requirements for Top-Up Coverage</h3>

<p>To purchase our top-up policy, you must have:</p>
<ol>
<li><strong>Existing buildings or contents insurance</strong> already in place for the property</li>
<li><strong>Insurer awareness</strong> - Your current insurer must know about and permit the hosting activity</li>
</ol>

<p><em>Important: Make sure your landlord and their insurer are aware you're running a short-term let. Many standard rental agreements prohibit subletting or holiday letting.</em></p>

<h2>How to Get a Quote for Top-Up Coverage</h2>

<p>Getting a quote is quick and easy:</p>

<ol>
<li>Visit <a href="https://www.pikl.com" target="_blank">www.pikl.com</a></li>
<li>Click <strong>"Get a Quote"</strong></li>
<li>At <strong>Step 3</strong>, select <strong>"Top-Up Only"</strong></li>
<li>Complete your quote</li>
</ol>

<h2>Important Considerations for Rent-to-Rent Operators</h2>

<h3>🏠 Buildings Insurance</h3>
<p>The property owner (your landlord) should have buildings insurance in place. This typically covers:</p>
<ul>
<li>Structure of the building</li>
<li>Permanent fixtures and fittings</li>
<li>Landlord's contents (if furnished)</li>
</ul>

<h3>🛋️ Your Contents</h3>
<p>Consider contents insurance for items you've added to the property:</p>
<ul>
<li>Furniture you've purchased</li>
<li>Decorations and soft furnishings</li>
<li>Kitchen equipment and appliances</li>
<li>Electronics and entertainment systems</li>
</ul>

<h3>⚖️ Legal Requirements</h3>
<p>Before operating a rent-to-rent holiday let, ensure you have:</p>
<ul>
<li>Written permission from your landlord</li>
<li>Appropriate planning permission (if required in your area)</li>
<li>Compliance with local licensing requirements</li>
<li>Fire safety certificates and equipment</li>
<li>Gas and electrical safety certificates</li>
</ul>

<h2>Still Have Questions?</h2>

<p>We understand that rent-to-rent situations can be complex. Our team is here to help!</p>

<p><strong>Contact us for advice on:</strong></p>
<ul>
<li>Which top-up coverage is right for your situation</li>
<li>Understanding your insurance requirements</li>
<li>Getting a personalized quote</li>
<li>Verifying your existing coverage is suitable</li>
</ul>

<p>Reach out through your preferred channel and we'll be happy to assist with your specific circumstances.</p>

<hr>

<p><em>Note: This article provides general guidance. Always ensure you comply with your tenancy agreement and all legal requirements for operating a short-term let.</em></p>"""

    # Create the article
    article = create_public_article(title, body, description)

    if article:
        print()
        print("=" * 80)
        print("✅ Public Article Created Successfully!")
        print("=" * 80)
        print()
        print("This article is now live in your Intercom Help Center and searchable by customers.")
        print()
        print("Suggested next steps:")
        print("  1. Add to a Help Center collection for better organization")
        print("  2. Tag with: holiday-let, rent-to-rent, top-up, public-liability")
        print("  3. Consider creating related articles about top-up coverage benefits")
        print()


if __name__ == "__main__":
    main()

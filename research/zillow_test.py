"""
Zillow Agent Search API Prototype
Fill in the details after reverse engineering the API (see api_discovery_guide.md)
"""

import requests
import json
from pprint import pprint

# =============================================================================
# CONFIGURATION - UPDATE THESE AFTER API DISCOVERY
# =============================================================================

# Endpoint URL (from DevTools Network tab)
ZILLOW_API_URL = "https://www.zillow.com/FILL_THIS_IN"  # TODO: Update this

# Request headers (from "Copy as cURL")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Content-Type": "application/json",
    # Add more headers as needed:
    # "Cookie": "...",
    # "Authorization": "...",
    # "X-API-Key": "...",
}

# Request method
REQUEST_METHOD = "POST"  # or "GET"

# =============================================================================
# SCENARIO A: GraphQL API
# =============================================================================
def test_graphql_search():
    """Test if Zillow uses GraphQL for agent search"""

    # GraphQL query (copy from DevTools Payload tab)
    query = """
    query SearchAgents($location: String!, $limit: Int!) {
      agents(location: $location, limit: $limit) {
        id
        name
        phone
        email
        city
        state
        rating
        reviewCount
        activeListings
        # Add more fields as you discover them
      }
    }
    """

    variables = {
        "location": "California",
        "limit": 10
    }

    payload = {
        "query": query,
        "variables": variables
    }

    print("Testing GraphQL API...")
    print(f"URL: {ZILLOW_API_URL}")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")

    try:
        response = requests.post(
            ZILLOW_API_URL,
            headers=HEADERS,
            json=payload,
            timeout=30
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\n✅ Success! Response:")
            pprint(data)

            # Try to extract agent data
            if "data" in data and "agents" in data["data"]:
                agents = data["data"]["agents"]
                print(f"\n📊 Found {len(agents)} agents")
                if agents:
                    print("\nFirst agent:")
                    pprint(agents[0])
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"\n❌ Exception: {e}")

# =============================================================================
# SCENARIO B: REST API (GET)
# =============================================================================
def test_rest_get():
    """Test if Zillow uses REST GET for agent search"""

    # Query parameters
    params = {
        "location": "California",
        "limit": 10,
        "offset": 0,
        # Add more params as discovered
    }

    print("Testing REST GET API...")
    print(f"URL: {ZILLOW_API_URL}")
    print(f"Params: {params}\n")

    try:
        response = requests.get(
            ZILLOW_API_URL,
            headers=HEADERS,
            params=params,
            timeout=30
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\n✅ Success! Response:")
            pprint(data)

            # Try to find agent array (structure varies)
            if "results" in data:
                agents = data["results"]
            elif "data" in data:
                agents = data["data"]
            elif "agents" in data:
                agents = data["agents"]
            else:
                agents = data

            print(f"\n📊 Found {len(agents) if isinstance(agents, list) else 'unknown'} agents")

        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"\n❌ Exception: {e}")

# =============================================================================
# SCENARIO C: REST API (POST)
# =============================================================================
def test_rest_post():
    """Test if Zillow uses REST POST for agent search"""

    # JSON payload
    payload = {
        "location": "California",
        "limit": 10,
        "offset": 0,
        "filters": {
            "rating_min": 4.0,
            # Add more filters as discovered
        }
    }

    print("Testing REST POST API...")
    print(f"URL: {ZILLOW_API_URL}")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")

    try:
        response = requests.post(
            ZILLOW_API_URL,
            headers=HEADERS,
            json=payload,
            timeout=30
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\n✅ Success! Response:")
            pprint(data)

        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"\n❌ Exception: {e}")

# =============================================================================
# SCENARIO D: HTML Scraping
# =============================================================================
def test_html_scraping():
    """Test if agent data is embedded in HTML"""

    url = "https://www.zillow.com/professionals/FILL_THIS_IN"  # Update with actual agent search URL

    print("Testing HTML scraping...")
    print(f"URL: {url}\n")

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            html = response.text

            # Look for JSON data in script tags
            if '"agents"' in html or '"professionals"' in html:
                print("\n✅ Found agent data in HTML!")
                print("Look for <script> tags containing JSON")

                # Try to extract JSON (simplified)
                import re
                json_pattern = r'<script[^>]*>(.*?)</script>'
                scripts = re.findall(json_pattern, html, re.DOTALL)

                for script in scripts:
                    if 'agent' in script.lower() or 'professional' in script.lower():
                        print("\n📋 Found relevant script tag:")
                        print(script[:500])  # Print first 500 chars
                        break
            else:
                print("\n❓ No obvious JSON data found in HTML")
                print("May need to use Selenium for dynamic content")

        else:
            print(f"\n❌ Error: {response.status_code}")

    except Exception as e:
        print(f"\n❌ Exception: {e}")

# =============================================================================
# MAIN
# =============================================================================
def main():
    print("=" * 80)
    print("ZILLOW AGENT SEARCH API TESTER")
    print("=" * 80)
    print("\n⚠️  Before running, update the configuration section with your findings")
    print("from DevTools Network tab (see api_discovery_guide.md)\n")

    # Uncomment the scenario that matches your findings:

    # test_graphql_search()  # If Zillow uses GraphQL
    # test_rest_get()        # If Zillow uses REST GET
    # test_rest_post()       # If Zillow uses REST POST
    # test_html_scraping()   # If data is in HTML

    print("\n" + "=" * 80)
    print("After successful testing:")
    print("1. Document the API structure in docs/zillow_api.md")
    print("2. Note all available agent fields")
    print("3. Proceed to Phase 2: Implementation")
    print("=" * 80)

if __name__ == "__main__":
    main()

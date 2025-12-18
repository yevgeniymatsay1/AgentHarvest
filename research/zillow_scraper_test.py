"""
Working Zillow Agent Scraper - HTML/SSR Approach
Based on API reverse engineering findings
"""

import requests
import json
import re
from typing import List, Dict, Optional
from pprint import pprint

def scrape_agents_from_zillow(location: str = "new-york-ny", state: str = None, city: str = None) -> List[Dict]:
    """
    Scrape agents from Zillow using HTML parsing (SSR approach)

    Args:
        location: URL slug for location (e.g., "new-york-ny", "california", "san-diego-ca")
        state: State name (optional, for constructing location slug)
        city: City name (optional, for constructing location slug)

    Returns:
        List of agent dictionaries
    """

    # Construct URL
    base_url = "https://www.zillow.com/professionals/real-estate-agent-reviews"

    # Try different URL patterns
    if city and state:
        # City, State format
        location_slug = f"{city.lower().replace(' ', '-')}-{state.lower().replace(' ', '-')}"
        url = f"{base_url}/{location_slug}/"
    elif state:
        # State only
        location_slug = state.lower().replace(' ', '-')
        url = f"{base_url}/{location_slug}/"
    else:
        # Use provided location or default
        if location:
            url = f"{base_url}/{location}/"
        else:
            url = f"{base_url}/"

    print(f"🔍 Fetching agents from: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        html = response.text

        # Extract __NEXT_DATA__
        match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html,
            re.DOTALL
        )

        if not match:
            raise Exception("❌ Could not find __NEXT_DATA__ in HTML. Page structure may have changed.")

        data = json.loads(match.group(1))

        # Navigate to agent results
        try:
            page_props = data['props']['pageProps']
            agent_finder_data = page_props['displayData']['agentFinderGraphData']['agentDirectoryFinderDisplay']
            search_results = agent_finder_data['searchResults']
            results = search_results['results']
            results_cards = results['resultsCards']

            # Print search info
            print(f"✅ Found {search_results.get('resultsFound', 0):,} total agents in this location")
            print(f"📄 Loaded {len(results_cards)} results on this page\n")

        except KeyError as e:
            raise Exception(f"❌ Data structure changed. Missing key: {e}")

        agents = []
        for card in results_cards:
            # Skip ad cards (e.g., "Get help finding an agent" PLCCard)
            if card.get('__typename') != 'AgentDirectoryFinderProfileResultsCard':
                continue

            agent = {
                'agent_id': card.get('encodedZuid'),
                'name': card.get('cardTitle'),
                'brokerage_name': card.get('secondaryCardTitle'),
                'profile_url': card.get('cardActionLink'),
                'photo_url': card.get('imageUrl'),
                'is_top_agent': card.get('isTopAgent', False),
                'logo_url': card.get('logoUrl'),
            }

            # Parse review information
            review_info = card.get('reviewInformation', {})
            agent['rating'] = review_info.get('reviewAverage')
            agent['rating_text'] = review_info.get('reviewAverageText')
            review_count_text = review_info.get('reviewCountText', '(0)')
            # Extract number from "(123)" format
            agent['review_count'] = int(re.sub(r'[^\d]', '', review_count_text) or '0')

            # Parse profile data (sales, price range, etc.)
            profile_data = card.get('profileData', [])
            for item in profile_data:
                label = item.get('label', '').lower()
                data_value = item.get('data')

                if 'price range' in label:
                    agent['price_range'] = data_value
                    # Try to parse min/max
                    if data_value:
                        prices = re.findall(r'\$[\d.]+[KMB]?', data_value)
                        if len(prices) >= 2:
                            agent['price_range_min'] = prices[0]
                            agent['price_range_max'] = prices[1]
                elif 'sales last 12 months' in label or 'last 12 months' in label:
                    try:
                        agent['sales_last_12_months'] = int(re.sub(r'[^\d]', '', data_value))
                    except:
                        agent['sales_last_12_months'] = data_value
                elif 'sales in' in label or 'total sales' in label:
                    try:
                        agent['total_sales'] = int(re.sub(r'[^\d]', '', data_value))
                    except:
                        agent['total_sales'] = data_value

            # Parse tags (certifications, team status, etc.)
            tags = card.get('tags', [])
            agent['tags'] = [tag.get('text') for tag in tags]
            agent['is_team'] = any('TEAM' in tag.get('text', '').upper() for tag in tags)

            # Extract years of experience from tags
            for tag in tags:
                text = tag.get('text', '')
                if 'YRS' in text.upper() or 'YEARS' in text.upper():
                    # Extract number from "LICENSED 10+ YRS"
                    years_match = re.search(r'(\d+)', text)
                    if years_match:
                        agent['years_experience_min'] = int(years_match.group(1))

            agents.append(agent)

        return agents

    except requests.RequestException as e:
        raise Exception(f"❌ Network error: {e}")
    except json.JSONDecodeError as e:
        raise Exception(f"❌ Failed to parse JSON: {e}")
    except Exception as e:
        raise Exception(f"❌ Error: {e}")


def main():
    print("=" * 80)
    print("ZILLOW AGENT SCRAPER TEST")
    print("=" * 80)
    print()

    # Test 1: New York (default)
    print("TEST 1: New York, NY")
    print("-" * 80)
    try:
        agents = scrape_agents_from_zillow("new-york-ny")
        print(f"✅ Successfully scraped {len(agents)} agents\n")

        for i, agent in enumerate(agents, 1):
            print(f"{i}. {agent['name']}")
            print(f"   Brokerage: {agent['brokerage_name']}")
            print(f"   Rating: {agent['rating']} ⭐ ({agent['review_count']} reviews)")
            print(f"   Sales (12mo): {agent.get('sales_last_12_months', 'N/A')}")
            print(f"   Total Sales: {agent.get('total_sales', 'N/A')}")
            print(f"   Price Range: {agent.get('price_range', 'N/A')}")
            print(f"   Top Agent: {'Yes' if agent['is_top_agent'] else 'No'}")
            print(f"   Team: {'Yes' if agent.get('is_team') else 'No'}")
            if agent.get('tags'):
                print(f"   Tags: {', '.join(agent['tags'])}")
            print(f"   Profile: {agent['profile_url']}")
            print()

        # Export to JSON for inspection
        with open('research/scraped_agents_sample.json', 'w') as f:
            json.dump(agents, f, indent=2)
        print("💾 Saved sample to research/scraped_agents_sample.json\n")

    except Exception as e:
        print(f"❌ Test failed: {e}\n")

    # Test 2: California
    print("\n" + "=" * 80)
    print("TEST 2: California (state-level)")
    print("-" * 80)
    try:
        agents = scrape_agents_from_zillow(state="California")
        print(f"✅ Successfully scraped {len(agents)} agents\n")

        for i, agent in enumerate(agents[:3], 1):  # Show first 3
            print(f"{i}. {agent['name']} - {agent['brokerage_name']}")
            print(f"   Rating: {agent['rating']} ({agent['review_count']} reviews)")
            print()

    except Exception as e:
        print(f"❌ Test failed: {e}\n")

    # Test 3: San Diego, CA
    print("\n" + "=" * 80)
    print("TEST 3: San Diego, CA (city-level)")
    print("-" * 80)
    try:
        agents = scrape_agents_from_zillow(city="San Diego", state="CA")
        print(f"✅ Successfully scraped {len(agents)} agents\n")

        for i, agent in enumerate(agents[:3], 1):
            print(f"{i}. {agent['name']} - {agent['brokerage_name']}")
            print(f"   Rating: {agent['rating']} ({agent['review_count']} reviews)")
            print()

    except Exception as e:
        print(f"❌ Test failed: {e}\n")

    print("=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("1. ✅ Basic scraping works!")
    print("2. TODO: Implement pagination to get more than 5-6 agents per page")
    print("3. TODO: Fetch individual agent profiles for comprehensive data (phone, email)")
    print("4. TODO: Add filters (rating_min, sales_min, etc.)")
    print("5. TODO: Test with proxies to avoid rate limiting")
    print("=" * 80)


if __name__ == "__main__":
    main()

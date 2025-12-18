# Zillow Agent Search API - Reverse Engineering Results

## Summary

Zillow uses **server-side rendering with Next.js** for their agent finder page. Agent data is embedded in the initial HTML response within the `__NEXT_DATA__` JSON object, **NOT via separate GraphQL/REST API calls** for the initial results.

## Key Findings

### 1. Data Source
- **Method**: Server-Side Rendering (SSR) with Next.js
- **Initial Data**: Embedded in `<script id="__NEXT_DATA__">` tag in HTML
- **Additional Pages**: Likely uses GraphQL or AJAX for "Load More" functionality

### 2. URL Structure

**Agent Directory by Location:**
```
https://www.zillow.com/professionals/real-estate-agent-reviews/
```

Default shows New York, NY agents. Location can likely be specified via:
- URL path: `/professionals/real-estate-agent-reviews/{city}-{state}/`
- Query parameters (to be tested)

### 3. Data Structure

**Location in __NEXT_DATA__:**
```
__NEXT_DATA__
  └── props
      └── pageProps
          └── displayData
              └── agentFinderGraphData
                  └── agentDirectoryFinderDisplay
                      └── searchResults
                          ├── currentPage: 1
                          ├── resultsFound: 68944
                          ├── loadMoreResultsButtonText: "View more"
                          └── results
                              └── resultsCards: [...]
```

### 4. Agent Card Structure

Each agent in `resultsCards` array contains:

```json
{
  "__typename": "AgentDirectoryFinderProfileResultsCard",
  "cardTitle": "Vincent Koo",
  "secondaryCardTitle": "Keller Williams NYC",
  "encodedZuid": "X1-ZUz2twqkseaknd_7kibb",
  "cardActionLink": "https://www.zillow.com/profile/Vincent-Koo",
  "imageUrl": "https://photos.zillowstatic.com/fp/99b974bb246750e0561b6dca49442202-h_l.jpg",
  "isTopAgent": false,
  "logoUrl": null,
  "profileData": [
    {
      "data": "$78K - $2.4M",
      "label": "price range"
    },
    {
      "data": "60",
      "label": "sales last 12 months"
    },
    {
      "data": "336",
      "label": "sales in New York"
    }
  ],
  "reviewInformation": {
    "reviewAverage": 5,
    "reviewAverageText": "5.0",
    "reviewCountText": "(260)",
    "noReviewsText": "No reviews"
  },
  "tags": [
    {
      "tagType": "SUCCESS",
      "text": "LICENSED 10+ YRS"
    }
  ]
}
```

### 5. Available Agent Fields

From initial search results:
- ✅ `cardTitle` - Agent name
- ✅ `secondaryCardTitle` - Brokerage/company name
- ✅ `encodedZuid` - Unique agent identifier
- ✅ `cardActionLink` - Profile URL
- ✅ `imageUrl` - Agent photo URL
- ✅ `isTopAgent` - Boolean flag
- ✅ `profileData` - Array with:
  - Price range (min-max)
  - Sales last 12 months
  - Total sales in region
- ✅ `reviewInformation`:
  - `reviewAverage` - Rating (0-5)
  - `reviewAverageText` - Formatted rating
  - `reviewCountText` - Number of reviews
- ✅ `tags` - Certifications, team status, experience

### 6. Missing Fields (Need Individual Profile Fetch)

The search results do **NOT** include:
- ❌ Phone number
- ❌ Email address
- ❌ Full address
- ❌ City/State (individual)
- ❌ Years of experience (exact number)
- ❌ Specialties list
- ❌ Languages spoken
- ❌ Individual reviews (only count + average)
- ❌ Recent sales details (addresses, dates, prices)
- ❌ Neighborhoods served (specific list)

**These require fetching individual agent profiles:**
```
https://www.zillow.com/profile/{agent-slug}
```

### 7. Pagination

- **Initial Load**: ~5-6 agents per page (includes ad cards)
- **Total Available**: 68,944 agents (for New York)
- **Load More**: Button text = "View more"
  - Mechanism: Unknown (needs testing)
  - Likely: GraphQL query or AJAX request
  - Params: page number or offset

### 8. Search/Filter Parameters

From `pageProps`:
```json
{
  "filterParams": {},
  "userInput": {},
  "region": {
    "name": "New York",
    "slug": "new-york-ny"
  }
}
```

Filters need to be tested:
- Location (city, state, ZIP)
- Rating minimum
- Years of experience
- Specialties
- Languages
- Sales volume

### 9. Rate Limiting

- **Initial page load**: No obvious rate limiting (standard HTTP request)
- **Pagination/AJAX**: Unknown until tested
- **Anti-bot protection**: PerimeterX (px-cloud.net) detected
  - May require:
    - Valid cookies/session
    - User-Agent headers
    - Potentially solve challenges

## Implementation Strategy

### Approach 1: HTML Scraping (Recommended for Initial Release)

**Pros:**
- No API authentication needed
- Initial data readily available
- Simpler implementation

**Cons:**
- Only 5-6 agents per page load
- Need to paginate by simulating "Load More" or visiting multiple pages
- HTML structure may change

**Implementation:**
1. Request URL with location parameter
2. Parse HTML and extract `__NEXT_DATA__` JSON
3. Navigate to `props.pageProps.displayData.agentFinderGraphData.agentDirectoryFinderDisplay.searchResults.results.resultsCards`
4. Parse each agent card
5. For pagination:
   - Option A: Construct URLs for different pages
   - Option B: Use Selenium/Playwright to click "Load More"

### Approach 2: GraphQL API (For Pagination)

**Needs Investigation:**
- Capture "Load More" button click with Playwright
- Identify GraphQL query for agent search
- Extract query structure and variables

**Next Steps:**
1. Modify Playwright script to click "Load More" multiple times
2. Capture subsequent API calls
3. Document pagination API

### Approach 3: Individual Profile Fetching

For comprehensive data (phone, email, etc.):
1. Get agent list from search (Approach 1)
2. For each agent, fetch their profile page:
   ```
   https://www.zillow.com/profile/{agent-slug}
   ```
3. Extract additional data from profile's `__NEXT_DATA__`

## Code Example: Basic HTML Scraping

```python
import requests
import json
import re

def scrape_agents_from_zillow(location="new-york-ny"):
    """Scrape agents from Zillow using HTML parsing"""

    url = f"https://www.zillow.com/professionals/real-estate-agent-reviews/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    response = requests.get(url, headers=headers)
    html = response.text

    # Extract __NEXT_DATA__
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)

    if not match:
        raise Exception("Could not find __NEXT_DATA__ in HTML")

    data = json.loads(match.group(1))

    # Navigate to agent results
    results_cards = (
        data['props']['pageProps']['displayData']
        ['agentFinderGraphData']['agentDirectoryFinderDisplay']
        ['searchResults']['results']['resultsCards']
    )

    agents = []
    for card in results_cards:
        # Skip ad cards
        if card.get('__typename') != 'AgentDirectoryFinderProfileResultsCard':
            continue

        agent = {
            'agent_id': card.get('encodedZuid'),
            'name': card.get('cardTitle'),
            'brokerage_name': card.get('secondaryCardTitle'),
            'profile_url': card.get('cardActionLink'),
            'photo_url': card.get('imageUrl'),
            'is_top_agent': card.get('isTopAgent'),
            'rating': card.get('reviewInformation', {}).get('reviewAverage'),
            'review_count': card.get('reviewInformation', {}).get('reviewCountText', '').strip('()'),
            'profile_data': card.get('profileData', []),
            'tags': [tag.get('text') for tag in card.get('tags', [])],
        }

        # Parse profile data
        for item in card.get('profileData', []):
            label = item.get('label', '').lower()
            data = item.get('data')

            if 'price range' in label:
                agent['price_range'] = data
            elif 'sales last 12 months' in label:
                agent['recent_sales_count'] = int(data)
            elif 'sales in' in label:
                agent['total_sales'] = int(data)

        agents.append(agent)

    return agents

# Test
agents = scrape_agents_from_zillow()
for agent in agents:
    print(f"{agent['name']} - {agent['brokerage_name']}")
    print(f"  Rating: {agent['rating']} ({agent['review_count']} reviews)")
    print(f"  Sales last 12mo: {agent.get('recent_sales_count', 'N/A')}")
    print()
```

## Next Steps

1. ✅ **COMPLETED**: Extract agent data from initial HTML
2. **TODO**: Test location-based searches (different cities/states)
3. **TODO**: Investigate pagination/load-more mechanism
4. **TODO**: Test fetching individual agent profiles for comprehensive data
5. **TODO**: Implement filters (rating, sales volume, etc.)
6. **TODO**: Test rate limiting and anti-bot measures

## Files Generated

- `research/zillow_screenshot.png` - Screenshot of agent finder page
- `research/zillow_page.html` - Full HTML source
- `research/next_data.json` - Extracted __NEXT_DATA__ JSON
- `research/agent_directory_data.json` - Agent directory structure
- `research/api_calls.json` - Captured network requests

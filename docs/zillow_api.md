# Zillow Agent Search API Documentation

> **Status**: 🔍 In Discovery - Fill this in after reverse engineering (see research/api_discovery_guide.md)

## API Overview

**Base URL**: [TO BE DISCOVERED]

**API Type**: [ ] GraphQL  [ ] REST  [ ] HTML Scraping

**Authentication**: [ ] None  [ ] Cookies  [ ] API Key  [ ] OAuth  [ ] Other: ___________

## Endpoint Details

### Agent Search Endpoint

**URL**:
```
[Fill in the exact endpoint URL]
```

**Method**: [ ] GET  [ ] POST

**Required Headers**:
```
User-Agent: [fill in]
Content-Type: [fill in]
Cookie: [fill in if needed]
[Add any other required headers]
```

## Request Structure

### GraphQL (if applicable)

**Query Name**: `[e.g., SearchAgents, FindProfessionals]`

**Query**:
```graphql
# Paste the GraphQL query here
query SearchAgents($location: String!, $limit: Int!) {
  agents(location: $location, limit: $limit) {
    # Fields...
  }
}
```

**Variables**:
```json
{
  "location": "California",
  "limit": 20,
  "offset": 0
}
```

### REST (if applicable)

**Query Parameters** (for GET):
```
?location=California
&limit=20
&offset=0
&rating_min=4.0
[Add all discovered params]
```

**Request Body** (for POST):
```json
{
  "location": "California",
  "limit": 20,
  "offset": 0,
  "filters": {
    "rating_min": 4.0
  }
}
```

## Response Structure

**Success Response** (200 OK):
```json
{
  "data": {
    "agents": [
      {
        "id": "...",
        "name": "...",
        "phone": "...",
        "email": "...",
        [List all available fields]
      }
    ],
    "total": 1234,
    "hasMore": true
  }
}
```

## Available Agent Fields

Document all fields available in the API response:

### Basic Info
- [ ] `id` / `agent_id` / `zpid` / `encryptedAgentId` - Agent identifier
- [ ] `name` - Full name
- [ ] `firstName` - First name
- [ ] `lastName` - Last name
- [ ] `title` - Professional title
- [ ] `phone` - Phone number
- [ ] `email` - Email address

### Location
- [ ] `address` - Street address
- [ ] `city` - City
- [ ] `state` - State
- [ ] `zip` / `zipCode` - ZIP code
- [ ] `latitude` - Latitude
- [ ] `longitude` - Longitude

### Listings
- [ ] `totalListings` - Total listings
- [ ] `activeListings` - Active listings count
- [ ] `forSaleListings` - For sale count
- [ ] `forRentListings` - For rent count
- [ ] `soldListings` - Sold listings count

### Profile
- [ ] `rating` - Rating (0-5)
- [ ] `reviewCount` - Number of reviews
- [ ] `reviews` - Array of review objects
- [ ] `yearsExperience` - Years of experience
- [ ] `specialties` - Array of specialties
- [ ] `languages` - Array of languages spoken
- [ ] `certifications` - Array of certifications
- [ ] `biography` / `bio` - Agent bio text

### Performance
- [ ] `recentSales` - Array of recent sales
- [ ] `totalSales` - Total sales count
- [ ] `priceRangeMin` - Minimum price handled
- [ ] `priceRangeMax` - Maximum price handled
- [ ] `neighborhoodsServed` - Array of neighborhoods
- [ ] `marketExpertise` - Geographic expertise

### Brokerage
- [ ] `brokerageName` - Brokerage name
- [ ] `brokeragePhone` - Brokerage phone

### Additional
- [ ] `photoUrl` / `profilePhoto` - Agent photo URL
- [ ] `profileUrl` - Profile page URL
- [ ] `website` - Personal website
- [ ] `licenses` - License numbers

## Pagination

**Type**: [ ] Offset-based  [ ] Cursor-based  [ ] Page-based

**Implementation**:
```
[Describe how to paginate through results]
- First page: offset=0, limit=20
- Second page: offset=20, limit=20
OR
- Use cursor/nextToken from previous response
```

**Page Size**: [typical page size, e.g., 20, 50, 100]

**Max Results**: [if there's a limit]

## Filters & Search Parameters

Document all available filter parameters:

### Location
- `location` (string) - State name, city name, or ZIP code
- `state` (string) - State abbreviation (e.g., "CA")
- `city` (string) - City name
- `zipCode` (string) - ZIP code
- `latitude`, `longitude` (float) - Coordinates
- `radius` (float) - Search radius in miles

### Agent Filters
- `ratingMin` (float) - Minimum rating (0-5)
- `minReviews` (int) - Minimum number of reviews
- `minListings` (int) - Minimum active listings
- `maxListings` (int) - Maximum active listings
- `yearsExperienceMin` (int) - Minimum years of experience
- `specialties` (array) - Filter by specialties
- `languages` (array) - Filter by languages

### Sorting
- `sortBy` (string) - Sort field (e.g., "rating", "reviews", "listings")
- `sortOrder` (string) - "asc" or "desc"

## Rate Limiting

**Observed Limits**:
- [ ] No obvious limits
- [ ] Requests per minute: ___________
- [ ] Requests per hour: ___________
- [ ] Requests per day: ___________

**Error Responses**:
- 429 Too Many Requests: [behavior when rate limited]
- 403 Forbidden: [when/why this occurs]

**Recommended Strategy**:
```
[Your recommendations for avoiding rate limits]
- Use delays between requests
- Implement exponential backoff
- Use proxies
- etc.
```

## Authentication & Anti-Bot Measures

**Required for Access**:
- [ ] Cookies (session-based)
- [ ] User-Agent header (specific value required)
- [ ] Referer header
- [ ] CSRF token
- [ ] API key
- [ ] reCAPTCHA
- [ ] Other: ___________

**Detection & Blocking**:
- [ ] IP-based blocking observed
- [ ] User-Agent validation required
- [ ] JavaScript challenge (Cloudflare, etc.)
- [ ] Rate limiting enforcement
- [ ] None observed

**Mitigation Strategies**:
```
[How to avoid being blocked]
- Residential proxies recommended
- Rotate User-Agent strings
- Maintain cookies/session
- Use Selenium if JS required
- etc.
```

## Sample cURL Request

```bash
# Copy the working cURL command from DevTools
curl 'https://www.zillow.com/...' \
  -H 'User-Agent: Mozilla/5.0 ...' \
  -H 'Content-Type: application/json' \
  --data-raw '{"query":"...","variables":{...}}'
```

## Sample Python Request

```python
import requests

url = "[endpoint URL]"

headers = {
    "User-Agent": "...",
    "Content-Type": "application/json",
}

payload = {
    # Request structure
}

response = requests.post(url, headers=headers, json=payload)
data = response.json()
```

## Notes & Observations

[Add any additional notes about the API]
- Stability: Does the API change frequently?
- Reliability: Response times, error rates
- Completeness: Are all desired fields available?
- Alternatives: Are there backup endpoints or methods?
- Legal: Any ToS concerns to be aware of?

## Example Responses

### Successful Agent Search
```json
[Paste a real example response with 2-3 agents]
```

### Error Response
```json
[Paste example error responses]
```

## Next Steps

After completing this documentation:
- [ ] Verified all required fields are available
- [ ] Tested pagination
- [ ] Tested filters
- [ ] Identified rate limits
- [ ] Ready to proceed to Phase 2: Implementation

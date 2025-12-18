# Zillow Agent Search API Discovery Guide

## Step 1: Open Zillow Agent Search

1. Go to https://www.zillow.com/professionals/
2. Or search Google for "zillow find an agent"
3. Enter a location (e.g., "California" or "San Diego, CA")
4. Click search to see agent results

## Step 2: Open Browser DevTools

1. **Chrome/Edge**: Press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
2. Click on the **Network** tab
3. Filter by **XHR** or **Fetch** to see only API calls
4. Click **Clear** to remove existing entries

## Step 3: Trigger Agent Search

1. With DevTools open, perform an agent search again
2. Or apply filters (location, rating, etc.)
3. Or click "Load More" / "Next Page" to see pagination

## Step 4: Identify the API Endpoint

Look for requests that return agent data. Common patterns:
- `/graphql` - GraphQL API
- `/api/agent/search` or `/api/professionals/search` - REST API
- Any URL with "agent" or "professional" in the path

### What to Check:
1. **Request URL**: Copy the full URL
2. **Request Method**: GET or POST?
3. **Request Headers**:
   - Look for: `Authorization`, `Cookie`, `X-API-Key`, `User-Agent`
   - Right-click request → Copy → Copy as cURL (bash)
4. **Request Payload** (if POST):
   - Click on the request
   - Go to "Payload" or "Request" tab
   - Copy the JSON body
5. **Response**:
   - Click "Preview" or "Response" tab
   - Verify it contains agent data
   - Note the JSON structure

## Step 5: Document Findings

Create a file `zillow_api_findings.txt` with:

```
ENDPOINT URL:
[paste URL here]

REQUEST METHOD:
GET or POST

REQUIRED HEADERS:
[paste headers here - get from "Copy as cURL"]

REQUEST BODY (if POST):
[paste JSON body here]

RESPONSE STRUCTURE:
[paste sample response or describe structure]

PAGINATION:
How does pagination work? (offset, cursor, page number?)

AVAILABLE FIELDS:
List all agent fields you see in the response:
- agent_id / zpid / encryptedAgentId
- name
- phone
- email
- ... etc

FILTERS:
What query parameters or filters are available?
- location
- rating
- specialties
- ... etc
```

## Step 6: Test with curl

Once you have the cURL command, test it in your terminal:

```bash
# Example (yours will be different)
curl 'https://www.zillow.com/graphql' \
  -H 'Content-Type: application/json' \
  -H 'User-Agent: Mozilla/5.0 ...' \
  --data-raw '{"query":"...", "variables":{...}}'
```

If it returns agent data, you've found the right endpoint!

## Step 7: Run Prototype Script

Once you have the endpoint details, update `research/zillow_test.py` with:
- The correct URL
- Required headers
- Request structure (GraphQL query or REST params)

Then run:
```bash
cd research
python zillow_test.py
```

## Common Scenarios

### Scenario A: GraphQL API
- Endpoint: `/graphql`
- Method: POST
- Body contains: `{"query": "...", "variables": {...}}`
- Look for agent search query name (e.g., `SearchAgents`, `FindProfessionals`)

### Scenario B: REST API
- Endpoint: `/api/agent/search?location=...&limit=...`
- Method: GET or POST
- Parameters in URL or JSON body

### Scenario C: Server-Side Rendered (HTML)
- No obvious XHR/Fetch requests
- Agent data embedded in HTML
- Look for `<script>` tags with JSON data
- May need BeautifulSoup or Selenium

## Troubleshooting

**No XHR requests found?**
- Agent data might be in initial HTML
- Check "Doc" filter for HTML responses
- Look for JSON data in `<script>` tags

**Requests require authentication?**
- Look for cookies in Request Headers
- May need to maintain session
- Consider using Selenium to automate browser

**Getting 403 Forbidden?**
- Headers might be required (User-Agent, Referer)
- Anti-bot protection might be active
- May need proxies or browser automation

**Data is incomplete?**
- Initial search might return limited data
- Full agent profiles might require separate request
- Click on an agent profile and check for additional API calls

## Next Steps

After documenting the API structure:
1. Update `research/zillow_test.py` with your findings
2. Test fetching agents for one location
3. Verify all required fields are available
4. Document in `docs/zillow_api.md`
5. Proceed to Phase 2 of implementation

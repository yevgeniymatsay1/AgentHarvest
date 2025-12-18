# Zillow Agent Scraper - Implementation Summary

## ✅ Phase 1: API Discovery - COMPLETED

### What We Discovered

1. **Data Source**: Zillow uses Server-Side Rendering (Next.js)
   - Agent data is embedded in HTML within `__NEXT_DATA__` JSON
   - NOT a separate GraphQL/REST API for initial results
   - Pagination likely requires additional requests (to be implemented)

2. **URL Structure**:
   ```
   https://www.zillow.com/professionals/real-estate-agent-reviews/
   https://www.zillow.com/professionals/real-estate-agent-reviews/{city}-{state}/
   https://www.zillow.com/professionals/real-estate-agent-reviews/{state}/
   ```

3. **Available Data Per Agent** (from search results):
   - ✅ Agent Name
   - ✅ Brokerage Name
   - ✅ Agent ID (encodedZuid)
   - ✅ Profile URL
   - ✅ Photo URL
   - ✅ Rating (0-5 stars)
   - ✅ Review Count
   - ✅ Price Range (min-max)
   - ✅ Sales Last 12 Months
   - ✅ Total Sales in Region
   - ✅ Is Top Agent (boolean)
   - ✅ Tags (TEAM, LICENSED X+ YRS, etc.)

4. **Missing Data** (requires individual profile fetch):
   - ❌ Phone Number
   - ❌ Email Address
   - ❌ Full Street Address
   - ❌ City/State (individual level)
   - ❌ Specialties
   - ❌ Languages
   - ❌ Individual Reviews (full text)
   - ❌ Recent Sales Details (addresses, dates, exact prices)
   - ❌ Certifications (detailed)

5. **Anti-Bot Protection**: 🚨 **CRITICAL FINDING**
   - Zillow uses PerimeterX bot detection
   - Simple `requests` library → **403 Forbidden**
   - Browser automation (Playwright/Selenium) → **✅ Works**
   - **SOLUTION**: Must use Playwright or Selenium

### Files Generated

All saved in `/research` directory:
- `zillow_screenshot.png` - Visual confirmation of page
- `zillow_page.html` - Full HTML source
- `next_data.json` - Extracted `__NEXT_DATA__`
- `agent_directory_data.json` - Parsed agent structure
- `api_calls.json` - Network traffic capture
- `zillow_scraper_test.py` - Working scraper (needs Playwright)
- `playwright_api_capture.py` - Automated browser script

Documentation:
- `/docs/zillow_api_findings.md` - Complete API documentation
- `/docs/IMPLEMENTATION_SUMMARY.md` - This file

---

## 📋 Implementation Plan - Updated

### Architecture Decision

Based on discoveries, we'll use a **hybrid approach**:

1. **Playwright for Page Fetching** (bypass anti-bot)
2. **HTML Parsing** for initial agent list (fast, SSR data)
3. **Optional Profile Fetching** for comprehensive data

### Data Models (from Plan)

```python
class Agent(BaseModel):
    # From Search Results
    agent_id: str                          # encodedZuid
    name: str
    profile_url: str
    brokerage_name: Optional[str]
    photo_url: Optional[str]
    is_top_agent: bool
    rating: Optional[float]
    review_count: int
    price_range: Optional[str]            # "$78K - $2.4M"
    price_range_min: Optional[int]
    price_range_max: Optional[int]
    sales_last_12_months: Optional[int]
    total_sales: Optional[int]
    tags: List[str]
    is_team: bool
    years_experience_min: Optional[int]    # From tags

    # From Individual Profile (optional, requires extra fetch)
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    specialties: Optional[List[str]]
    languages: Optional[List[str]]
    certifications: Optional[List[str]]
    biography: Optional[str]
    recent_sales: Optional[List[Sale]]
    reviews: Optional[List[Review]]
    neighborhoods_served: Optional[List[str]]
```

### Implementation Approach

#### Stage 1: Basic Search (5-6 agents per location)
**Files**:
- `agentharvest/core/scrapers/zillow/__init__.py` (ZillowScraper)
- `agentharvest/core/scrapers/zillow/parsers.py` (HTML parsing)

**Method**:
1. Use Playwright to fetch page HTML
2. Extract `__NEXT_DATA__` JSON
3. Parse `resultsCards` array
4. Return list of Agent objects

**Limitations**:
- Only returns ~5-6 agents per request
- No phone/email (requires profile fetch)

#### Stage 2: Pagination (50-200+ agents)
**Options**:
- **Option A**: Playwright auto-scroll / click "Load More"
  - Simulates user behavior
  - Gets more results in single session
- **Option B**: Discover pagination API
  - Capture requests when clicking "Load More"
  - Implement direct API calls
  - Faster, but may be blocked

#### Stage 3: Comprehensive Data (phone, email, etc.)
**Method**:
1. For each agent from search, fetch their profile:
   ```
   https://www.zillow.com/profile/{agent-slug}
   ```
2. Extract additional `__NEXT_DATA__` from profile page
3. Merge with search results

**Trade-off**: 1 request per agent (slow for large lists)

---

## 🛠️ Technical Requirements

### Required Dependencies

**Add to `pyproject.toml` / `setup.py`**:
```python
dependencies = [
    "requests>=2.31.0",         # Keep for HTTP (if needed)
    "pandas>=2.0.0",            # CSV export
    "pydantic>=2.0.0",          # Data validation
    "tenacity>=8.2.0",          # Retry logic
    "playwright>=1.40.0",       # CRITICAL: Browser automation
    "beautifulsoup4>=4.12.0",   # Optional: HTML parsing fallback
]
```

**Install Playwright browsers**:
```bash
playwright install chromium
```

### ZillowScraper Architecture

```
agentharvest/core/scrapers/zillow/
├── __init__.py              # ZillowScraper class
├── browser.py               # Playwright session management
├── parsers.py               # HTML/JSON parsing functions
├── processors.py            # Agent data transformation
└── queries.py               # URL builders
```

**Key Classes**:

```python
class ZillowScraper:
    def __init__(self, search_input: SearchInput):
        self.browser = PlaywrightBrowser()  # Manages Playwright instance

    def search_agents(self) -> List[Agent]:
        # 1. Build URL from search_input
        # 2. Fetch page with Playwright
        # 3. Extract __NEXT_DATA__
        # 4. Parse resultsCards
        # 5. Apply client-side filters
        # 6. Optionally fetch profiles for comprehensive data
        # 7. Return Agent objects

    def _fetch_page_html(self, url: str) -> str:
        # Use Playwright to get HTML (bypasses bot detection)

    def _extract_agents_from_html(self, html: str) -> List[Agent]:
        # Parse __NEXT_DATA__ and extract agents

    def _fetch_agent_profile(self, profile_url: str) -> Dict:
        # Optional: Get comprehensive data from profile page

class PlaywrightBrowser:
    """Manages Playwright browser instance with anti-detection"""

    def __init__(self):
        self.browser = None
        self.context = None

    def get_page_html(self, url: str) -> str:
        # Launch browser if not started
        # Navigate to URL
        # Wait for page load
        # Return HTML

    def close(self):
        # Clean up browser instance
```

---

## ⚠️ Challenges & Solutions

### 1. Anti-Bot Protection
**Problem**: 403 Forbidden with `requests` library

**Solution**: Use Playwright
- Renders JavaScript
- Uses real browser fingerprint
- Can solve challenges if needed

**Implementation**:
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)
    html = page.content()
    browser.close()
```

### 2. Limited Results Per Page
**Problem**: Only 5-6 agents per search

**Solutions**:
- **Short-term**: Accept limitation, document in README
- **Long-term**: Implement pagination (Stage 2)

### 3. Missing Contact Info
**Problem**: No phone/email in search results

**Solutions**:
- **Option A**: Fetch individual profiles (slow but comprehensive)
- **Option B**: Return what's available, document limitations

### 4. Rate Limiting
**Problem**: May get blocked with too many requests

**Solutions**:
- Implement delays between requests
- Support proxy rotation
- Limit default results
- Use browser session management (keep cookies)

---

## 📊 Success Metrics

### Minimum Viable Product (MVP)
- ✅ Can search agents by city/state
- ✅ Returns 5-6 agents per search
- ✅ Includes: name, brokerage, rating, sales data
- ✅ Outputs to CSV

### Full Feature Set
- ✅ Pagination (50-200+ agents)
- ✅ Comprehensive data (phone, email) via profile fetch
- ✅ Filters: rating_min, sales_min, years_experience_min
- ✅ Proxy support

---

## 🚀 Next Steps (Ready to Implement)

1. **Phase 2 - Foundation** (1-2 hours):
   - Delete Realtor.com code
   - Create new directory structure
   - Define Agent/Sale/Review models

2. **Phase 3 - Core Scraper** (2-3 hours):
   - Implement `PlaywrightBrowser` class
   - Implement `ZillowScraper.search_agents()`
   - Implement HTML parsing functions

3. **Phase 4 - Integration** (1 hour):
   - Create `scrape_agent()` function
   - Update utils for CSV export
   - Rename package to `agentharvest`

4. **Phase 5 - Testing** (1 hour):
   - Test with multiple locations
   - Verify CSV export
   - Test error handling

**Total Estimated Time**: 5-7 hours

---

## 💰 Cost/Performance Considerations

### Playwright Overhead
- **Pros**: Bypasses anti-bot, gets JavaScript-rendered content
- **Cons**: Slower than pure requests (~2-5s per page vs ~0.5s)
- **Mitigation**: Cache results, use headless mode, reuse browser instance

### Scalability
- **Initial**: 5-6 agents per request
- **With Pagination**: 50-200+ per search
- **With Profile Fetch**: 1 request per agent for phone/email

**Recommendation**:
- Stage 1: Basic search (fast, limited results)
- Stage 2: Add pagination as optional `limit` parameter
- Stage 3: Add `fetch_profiles=True` flag for comprehensive data

---

## 📝 Documentation Updates Needed

### README.md
- Update description to "Zillow real estate agent scraper"
- Update examples to agent search
- Document limitations (5-6 results default, no phone/email without profile fetch)
- Add Playwright installation instructions

### Function Signature
```python
def scrape_agent(
    state: str = None,
    city: str = None,
    zip_code: str = None,
    # Filters (client-side)
    rating_min: float = None,
    sales_min: int = None,
    years_experience_min: int = None,
    # Control
    limit: int = 10,  # How many to return (may require pagination)
    fetch_profiles: bool = False,  # Get phone/email (slower)
    proxy: str = None,
) -> pd.DataFrame:
    """Search for real estate agents on Zillow"""
```

---

## ✅ Summary

### What's Working
- ✅ API structure discovered and documented
- ✅ Data extraction method identified (HTML parsing)
- ✅ Sample data captured and analyzed
- ✅ Anti-bot bypass solution found (Playwright)

### What's Next
- Implement ZillowScraper with Playwright
- Build data models
- Create CSV export
- Test with real data

### Key Takeaway
The foundation is solid - we know exactly how to scrape Zillow agents. The main challenge is anti-bot protection, which Playwright solves. We're ready to proceed with full implementation!

---

## 🎯 Ready to Build?

All research is complete. You can now proceed with confidence to Phase 2 (Foundation) and begin building the AgentHarvest scraper.

**Would you like me to start implementing now?**

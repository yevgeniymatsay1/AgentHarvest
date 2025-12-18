# Rate Limiting Safeguards Guide

## Built-in Safeguards (Already Implemented)

Your scraper has multiple layers of protection:

### 1. Automatic Delays Between Requests ✅
- **Default:** 2.5 seconds between profile requests
- **Configurable:** Up to 10 seconds
- **Always on:** Cannot be disabled

```python
agents = scrape_agent(
    state="Texas",
    limit=10,
    delay_between_requests=5.0  # Increase if needed
)
```

### 2. Browser Impersonation ✅
- Uses `curl_cffi` with Chrome 124 impersonation
- Sends authentic browser headers
- Harder to detect as bot

### 3. Smart Request Management ✅
- Only fetches profiles when needed
- Reuses connections
- Sequential, never parallel (prevents burst traffic)

## Testing Safeguards (Choose One)

### Level 1: MINIMAL TEST (Safest - Only 1 Request)
```bash
python test_minimal_safe.py
```
- Makes only 1 request total
- No profile fetching
- Fastest way to test if IP is blocked
- **Use this first after waiting**

### Level 2: ULTRA-SAFE TEST (2 Agents, 5s delays)
```bash
python test_safe.py
```
- Fetches 2 agent profiles
- 5 second delays between requests
- Tests full functionality safely
- **Use this if Level 1 succeeds**

### Level 3: NORMAL USE (After Confirmed Safe)
```bash
streamlit run app.py
```
or
```python
from agentharvest import scrape_agent

agents = scrape_agent(
    state="California",
    limit=20,
    # Uses default 2.5s delays
)
```

## Recommended Testing Sequence

After waiting 12+ hours:

```bash
# Step 1: Test with single request (safest)
python test_minimal_safe.py

# ✅ If successful → Step 2
# ❌ If 403 error → Wait 24 hours or use proxy

# Step 2: Test with profiles (2 agents, 5s delays)
python test_safe.py

# ✅ If successful → Step 3
# ❌ If 403 error → Your IP needs more time

# Step 3: Use normally
streamlit run app.py
# or do regular scraping with default settings
```

## Best Practices Going Forward

### For Small Scrapes (< 10 agents)
```python
agents = scrape_agent(
    state="Texas",
    limit=5,
    # Default settings are fine
)
```

### For Medium Scrapes (10-50 agents)
```python
agents = scrape_agent(
    state="California",
    limit=30,
    delay_between_requests=3.0,  # Slightly more conservative
)
```

### For Large Scrapes (50+ agents)
```python
# Option A: Use proxy
agents = scrape_agent(
    state="California",
    limit=100,
    proxy="http://your-proxy:port",
    delay_between_requests=2.5,
)

# Option B: Increase delays (slower but safer)
agents = scrape_agent(
    state="California",
    limit=100,
    delay_between_requests=5.0,  # Double delay
)

# Option C: Batch over time
# Do 20 agents now, wait 30 minutes, do 20 more, etc.
```

## If You Get Rate Limited Again

### Immediate Actions:
1. **Stop all requests immediately**
2. **Wait at least 15-30 minutes**
3. **Test with minimal test first**

### Prevention:
1. **Use different states** - Don't hammer same location
2. **Space out sessions** - Wait 5+ minutes between search sessions
3. **Lower your limits** - 10-20 agents per search is safer than 100
4. **Use proxies for production** - Essential for regular/automated use

## Proxy Setup (For Production Use)

### Why Use Proxies?
- No rate limits (each request uses different IP)
- Faster scraping (no need for long delays)
- More reliable for production

### Recommended Proxy Services:
1. **Bright Data** - Premium, expensive, very reliable
2. **Oxylabs** - Good quality, moderate price
3. **ScraperAPI** - Easy to use, handles rotation
4. **Webshare** - Budget-friendly option

### Usage:
```python
agents = scrape_agent(
    state="California",
    proxy="http://username:password@proxy-host:port",
    limit=100,
    delay_between_requests=1.0,  # Can be faster with proxy
)
```

## Rate Limit Detection

You'll know you're rate limited if you see:

```
❌ 403 Forbidden. Zillow blocked the request.
```

### Recovery Time:
- **Light block:** 15-30 minutes
- **Medium block:** 1-4 hours
- **Heavy block:** 12-24 hours
- **Severe block:** 24-48 hours

## Emergency Workarounds

If you need data NOW and your IP is blocked:

### Option 1: Mobile Hotspot
```bash
# Switch to phone's hotspot
# Run test_minimal_safe.py
```

### Option 2: VPN
```bash
# Enable VPN
# Connect to different region
# Run test_minimal_safe.py
```

### Option 3: Cloud Instance
```bash
# Spin up AWS/GCP instance
# Different IP guaranteed
# Run your scraper there
```

### Option 4: Proxy Service (Best)
```python
# Sign up for proxy service
# Use their IPs instead of yours
agents = scrape_agent(
    state="Nevada",
    proxy="http://your-proxy:port",
    limit=50
)
```

## Monitoring Your Status

### Check if blocked:
```bash
python test_minimal_safe.py
```

### Expected results:
- **Not blocked:** ✅ Gets data successfully
- **Blocked:** ❌ 403 Forbidden error
- **Other error:** Check error message

## Summary

✅ **Built-in safeguards:**
- Automatic 2.5s delays
- Browser impersonation
- Sequential requests only

✅ **Testing safeguards:**
- test_minimal_safe.py (1 request)
- test_safe.py (ultra-safe)
- New states only

✅ **Usage safeguards:**
- Start small (5-10 agents)
- Increase delays for large scrapes
- Use proxies for production
- Space out sessions

✅ **Recovery safeguards:**
- Wait 15-30 min minimum
- Test before resuming
- Use different network if needed

---

**Remember:** Better to be slow and safe than fast and blocked!

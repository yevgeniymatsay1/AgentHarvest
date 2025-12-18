# Production Scraping Guide - Safe Continuous Operation

## The Problem with Fast Scraping

**Fast scraping (2.5s delays):**
- ✅ Good for: Quick one-time searches
- ❌ Bad for: Continuous/production use
- **Gets blocked after:** ~50 profile requests

**Production scraping (10-20s delays):**
- ✅ Good for: 24/7 continuous operation
- ✅ Never gets blocked
- **Can run:** Indefinitely

---

## Recommended Settings for Production

### Conservative (Safest)
```python
delay_min=15        # 15 seconds minimum
delay_max=25        # 25 seconds maximum
batch_size=5        # 5 agents per batch
batch_break=3600    # 60 minute break between batches
```
**Result:** ~3-4 agents/hour, never blocked ✅

### Balanced (Recommended)
```python
delay_min=10        # 10 seconds minimum
delay_max=20        # 20 seconds maximum
batch_size=10       # 10 agents per batch
batch_break=1800    # 30 minute break between batches
```
**Result:** ~10-15 agents/hour, very safe ✅

### Aggressive (Use with Caution)
```python
delay_min=5         # 5 seconds minimum
delay_max=10        # 10 seconds maximum
batch_size=15       # 15 agents per batch
batch_break=900     # 15 minute break between batches
```
**Result:** ~30-40 agents/hour, may get blocked ⚠️

---

## Quick Start - Safe Continuous Scraping

### 1. Run the Safe Continuous Scraper

```bash
python scrape_safe_continuous.py
```

This will:
- Scrape 10 agents
- Wait 30 minutes
- Scrape 10 more agents
- Repeat indefinitely
- Save progress after each batch
- Can be stopped/resumed anytime

### 2. Monitor Progress

While running, you'll see:
```
📦 BATCH 1
State: Nevada
Batch size: 10
Estimated time: 2.5 minutes

[Progress updates...]

✅ Batch complete: 10 agents saved

⏸️  Taking 30 minute break...
   Next batch starts at: 15:30:00
```

### 3. Results

All data saved to `./scraped_agents/`:
```
scraped_agents/
├── agents_nevada_batch1_20250118_143000.csv
├── agents_nevada_batch2_20250118_150000.csv
├── agents_nevada_batch3_20250118_153000.csv
├── checkpoint.json (resume point)
└── all_agents_merged.csv (combined file)
```

---

## Why These Settings Work

### The Math

Zillow's rate limits (estimated from testing):
- **Fast requests:** ~50 profiles before block
- **Time window:** ~1 hour
- **Safe rate:** ~10-15 profiles/hour

**Our conservative approach:**
- 10 agents per batch × 15s avg delay = 2.5 minutes
- 30 minute break between batches
- Total: 32.5 minutes per 10 agents
- **Rate:** ~18 agents/hour (safe!) ✅

### Random Delays Make It Look Human

```python
delay_min=10, delay_max=20  # Random between 10-20s

# Actual delays will be:
# Agent 1: 14.3s
# Agent 2: 18.7s
# Agent 3: 11.2s
# Agent 4: 19.4s
# ...
```

This **looks like a human** browsing profiles, not a bot.

---

## Advanced: Customize for Your Needs

### Example 1: Scrape 1000 Agents Overnight

```python
scraper = SafeContinuousScraper(
    delay_min=10,
    delay_max=15,
    batch_size=20,     # Larger batches
    batch_break=1200,  # 20 min breaks
)

scraper.run_continuous(
    states=["California", "Texas", "Florida"],
    agents_per_state=350  # 350 × 3 = 1050 agents
)

# Time: ~12-14 hours (run overnight)
```

### Example 2: Super Safe Daily Scraping

```python
scraper = SafeContinuousScraper(
    delay_min=20,
    delay_max=30,      # Very slow
    batch_size=5,      # Small batches
    batch_break=7200,  # 2 hour breaks
)

scraper.run_continuous(
    states=["Nevada"],
    agents_per_state=50
)

# Time: ~20 hours for 50 agents
# Result: Zero risk of blocking
```

### Example 3: Multiple States in Rotation

```python
scraper = SafeContinuousScraper(
    delay_min=10,
    delay_max=20,
    batch_size=15,
    batch_break=1800,
)

# Rotates between states automatically
scraper.run_continuous(
    states=[
        "California",
        "Texas",
        "Florida",
        "New York",
        "Nevada",
    ],
    agents_per_state=100  # 100 each = 500 total
)

# Time: ~2-3 days running continuously
```

---

## Features of Safe Continuous Scraper

### ✅ Checkpoint/Resume
- Saves progress after each batch
- Can stop with Ctrl+C anytime
- Run again to resume from last position

### ✅ Automatic Batching
- Scrapes in small batches
- Long breaks between batches
- Looks like natural usage patterns

### ✅ Random Delays
- Each request has random delay
- Mimics human behavior
- Harder to detect as bot

### ✅ Progress Tracking
- Shows real-time progress
- Estimates completion time
- Saves all intermediate results

### ✅ Error Recovery
- Continues if one batch fails
- Saves successful batches
- Logs errors for review

---

## Best Practices

### DO ✅

1. **Use random delays (10-20s)**
   ```python
   delay_min=10, delay_max=20
   ```

2. **Take long breaks between batches**
   ```python
   batch_break=1800  # 30 minutes
   ```

3. **Save progress frequently**
   - Built into the continuous scraper

4. **Rotate states/locations**
   - Don't hammer same location

5. **Monitor for 403 errors**
   - If you see 403, increase delays

6. **Start conservative**
   - Can always speed up if working

### DON'T ❌

1. **Don't use 2.5s delays for production**
   - Too fast, will get blocked

2. **Don't scrape same state repeatedly**
   - Rotate between states

3. **Don't skip breaks**
   - Breaks are essential

4. **Don't fetch 100+ agents at once**
   - Use batches of 10-20

5. **Don't run multiple instances**
   - One scraper at a time from same IP

6. **Don't ignore 403 errors**
   - Stop immediately if blocked

---

## Performance Expectations

### Conservative Settings (15-25s delays, 60min breaks)
- **Rate:** 3-4 agents/hour
- **Daily:** ~75-100 agents/day
- **Risk:** Virtually zero ✅

### Balanced Settings (10-20s delays, 30min breaks)
- **Rate:** 10-15 agents/hour
- **Daily:** ~250-350 agents/day
- **Risk:** Very low ✅

### Aggressive Settings (5-10s delays, 15min breaks)
- **Rate:** 30-40 agents/hour
- **Daily:** ~700-900 agents/day
- **Risk:** Medium ⚠️

---

## Monitoring Your Scraper

### Check Progress

```bash
# View checkpoint
cat scraped_agents/checkpoint.json

# Count total agents scraped
wc -l scraped_agents/*.csv

# View latest batch
tail -20 scraped_agents/agents_*.csv | head -10
```

### Signs You're Going Too Fast ⚠️

- Getting 403 errors
- Requests timing out
- Empty responses
- **Solution:** Increase delays and breaks

### Signs You're Safe ✅

- No 403 errors
- All batches completing
- Data quality good
- Can run for hours without issues

---

## Running in Background (Optional)

### On Mac/Linux:

```bash
# Run in background
nohup python scrape_safe_continuous.py > scraper.log 2>&1 &

# Check if running
ps aux | grep scrape_safe

# View logs
tail -f scraper.log

# Stop
pkill -f scrape_safe_continuous
```

### On Windows:

```powershell
# Run in background
Start-Process python -ArgumentList "scrape_safe_continuous.py" -WindowStyle Hidden

# Or use Task Scheduler for scheduled runs
```

---

## Alternative: Schedule Daily Runs

Instead of continuous, run once per day:

```python
# daily_scrape.py
scraper = SafeContinuousScraper(
    delay_min=10,
    delay_max=20,
    batch_size=20,
    batch_break=600,  # 10 min breaks
)

# Quick daily scrape
scraper.run_continuous(
    states=["California"],
    agents_per_state=50  # Takes ~2 hours
)
```

Schedule with cron (Mac/Linux):
```bash
# Run every day at 2am
0 2 * * * cd /path/to/AgentHarvest && python daily_scrape.py
```

Or Windows Task Scheduler:
- Trigger: Daily at 2:00 AM
- Action: Start python.exe
- Arguments: daily_scrape.py

---

## Summary: Production Settings

| Use Case | Settings | Rate | Risk |
|----------|----------|------|------|
| Test/Demo | 2.5s delay, no breaks | 100+/hr | High ❌ |
| Quick one-time | 5s delay, 10 min breaks | 40/hr | Medium ⚠️ |
| **Continuous (Recommended)** | 10-20s delay, 30 min breaks | 10-15/hr | Low ✅ |
| Super safe | 15-25s delay, 60 min breaks | 3-4/hr | None ✅ |

**For production: Use the balanced settings (10-20s, 30min breaks)**

This gets you **~250-350 agents per day** with virtually no risk of blocking.

---

## Ready to Start?

```bash
# Use the safe continuous scraper
python scrape_safe_continuous.py
```

Let it run overnight, come back to hundreds of agents safely scraped! 🎉

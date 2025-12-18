# AgentHarvest - Zillow Real Estate Agent Scraper

**Find real estate agents on Zillow with comprehensive contact information, ratings, and sales data.**

This tool helps you discover and collect information about real estate agents from Zillow.com. Perfect for building lead lists, market research, or finding top agents in specific locations.

---

## 🎯 What This Tool Does

- **Search by Location**: Find agents by state, city, or ZIP code
- **Filter Results**: Filter by rating, sales count, years of experience, and more
- **Comprehensive Data**: Get phone numbers, emails, ratings, sales history, specialties, and more
- **Export to CSV**: Save results to CSV/Excel for easy use in your CRM
- **Easy-to-Use Interface**: Simple web interface - no coding required
- **Smart Duplicate Prevention**: Automatically skips agents you've already scraped

---

## 📋 Complete Setup Guide (Mac)

**This guide assumes you have ZERO technical experience. Just follow each step exactly as written.**

### Step 1: Install Homebrew (Package Manager)

Homebrew makes it easy to install software on Mac. Copy and paste this command into Terminal:

1. Open **Terminal** (press `Command + Space` and type "Terminal")
2. Copy and paste this entire command, then press Enter:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**What you'll see:**
- It will ask for your Mac password (type it and press Enter - you won't see the letters as you type, this is normal)
- Installation takes 2-5 minutes
- You'll see lots of text scrolling

**If you already have Homebrew installed:** You'll see a message saying so. That's fine, just continue to Step 2.

### Step 2: Install Python

Now install Python using Homebrew:

```bash
brew install python3
```

**What you'll see:** Text scrolling as it downloads and installs Python (takes 1-2 minutes).

**To verify it worked:**
```bash
python3 --version
```

You should see something like `Python 3.11.5` or similar.

### Step 3: Download This Project from GitHub

Now we'll download the AgentHarvest project to your computer.

1. In Terminal, go to your Desktop folder:

```bash
cd ~/Desktop
```

**What this does:** The `cd` command means "change directory" (go to a different folder).

2. Download the project:

```bash
git clone https://github.com/yevgeniymatsay1/AgentHarvest.git
```

**What you'll see:** Text like "Cloning into 'AgentHarvest'..." - this means it's downloading.

### Step 4: Navigate to the Project Folder

Now we need to "go inside" the AgentHarvest folder:

```bash
cd AgentHarvest
```

**What this does:** This moves you into the AgentHarvest folder that was just created. Think of it like opening a folder in Finder, but using text commands.

**How to verify you're in the right place:** Type `pwd` and press Enter. You should see something like `/Users/yourname/Desktop/AgentHarvest`.

### Step 5: Install Required Packages

The project needs some additional software packages. We'll install them now:

```bash
pip3 install -r requirements.txt
```

**What you'll see:** You'll see a lot of text scrolling by. This is normal! It's installing all the required packages.

**How long it takes:** Usually 1-3 minutes depending on your internet speed.

**If you see an error about "pip3 not found":** Try this instead:
```bash
python3 -m pip install -r requirements.txt
```

### Step 6: Run the Application

Now you're ready to start the application!

```bash
streamlit run app.py
```

**What happens:**
1. You'll see some text in Terminal
2. Your web browser will automatically open to `http://localhost:8501`
3. You'll see the AgentHarvest interface!

**If your browser doesn't open automatically:** Copy this URL and paste it into your web browser:
```
http://localhost:8501
```

---

## 🚀 How to Use the Tool

Once the application is running in your browser, here's how to use it:

### Basic Search

1. **Enter a Location** (choose ONE):
   - State (e.g., "California" or "CA")
   - City and State (e.g., City: "San Diego", State: "CA")
   - ZIP Code (e.g., "92101")

2. **Set How Many Agents** (optional):
   - Default: 100 agents
   - You can request up to 1000, but keep in mind this will take longer

3. **Click "🔍 Search Agents"**

4. **Wait for Results**:
   - Basic search info loads in 5-10 seconds
   - Full contact details take longer (intelligent batching with delays)
   - Progress bar shows current status

5. **Download Results**:
   - Click the **"📥 Download as CSV"** button
   - File will be saved to your Downloads folder

### Advanced Filters (Optional)

Click **"⚙️ Advanced Options"** in the sidebar to access filters:

- **Minimum Rating**: Only show agents with 4+ stars, 4.5+ stars, etc.
- **Review Count**: Only agents with X+ reviews
- **Sales**: Filter by number of sales in last 12 months
- **Years of Experience**: Only show experienced agents
- **Top Agents Only**: Filter for Zillow Premier Agents
- **Exclude Teams**: Show only individual agents (not teams)
- **Agent Type**: Filter by Solo, Team, or Broker

### Duplicate Prevention (Built-In)

**What it does:** Automatically remembers which agents you've already scraped and skips them in future searches.

**How it works:**
- First search: Gets all agents found
- Second search: Skips agents from first search
- Third search: Skips agents from first + second search
- And so on...

**This is ENABLED by default** and works automatically. You don't need to do anything!

**If you want to scrape the same agents again:**
1. Go to Advanced Options
2. Uncheck "Skip Previously Scraped Agents"

**To clear your history (start fresh):**
1. Click the **"🗑️ Clear Scraping History"** button at the bottom of the sidebar

---

## 📊 What Data You Get

Each agent record includes:

### Basic Information
- Agent ID
- Full Name
- Brokerage/Company Name
- Profile URL
- Photo URL

### Contact Information
- Phone Number
- Email Address
- Office Address
- Website

### Performance Metrics
- Star Rating (0-5)
- Number of Reviews
- Sales in Last 12 Months
- Total Sales
- Active Listings Count
- Price Range Handled

### Professional Details
- Years of Experience
- Specialties (Buyer's Agent, Listing Agent, etc.)
- Languages Spoken
- Certifications
- Professional Biography
- Neighborhoods Served
- Market Expertise Areas

### Brokerage
- Brokerage Name
- Brokerage Phone
- Brokerage Address

---

## 💡 Tips for Best Results

### Getting More Agents
- **Search broader locations first**: Start with state-level searches
- **Try multiple cities**: Different cities have different agents
- **Use the limit parameter**: Set limit to 500 or 1000 for larger lists

### Avoiding Restrictions
- **Mobile user agents are enabled by default**: This helps avoid IP restrictions
- **Intelligent delays are automatic**: The tool adds random delays between requests
- **If you get blocked**: Wait 10-15 minutes before trying again, or use a proxy

### Using Filters Effectively
- **Start broad, then filter**: Get a large list first, then filter in Excel/Sheets
- **Ratings 4.5+**: Usually indicates top performers
- **10+ sales in 12 months**: Shows active agents
- **Years of experience**: 5+ years often means established agents

### Working with Results
- **Open CSV in Excel/Google Sheets**: Easy to sort, filter, and analyze
- **Combine multiple searches**: Run different cities/states and merge the files
- **Use duplicate prevention**: Let the tool automatically avoid duplicates across days

---

## 🔧 Troubleshooting

### "Command not found" errors
**Problem:** You see errors like `python3: command not found` or `pip3: command not found`

**Solution:**
1. Make sure you completed Step 2 (Installing Python)
2. Close Terminal completely and open it again
3. Try the command again

### Application won't start
**Problem:** When you run `streamlit run app.py`, you get an error

**Solution:**
1. Make sure you're in the AgentHarvest folder (run `pwd` to check)
2. Make sure you installed requirements (Step 5)
3. Try closing Terminal and starting over from Step 4

### Browser shows "This site can't be reached"
**Problem:** Browser can't load `http://localhost:8501`

**Solution:**
1. Check if the application is actually running in Terminal (should see text like "You can now view your Streamlit app in your browser")
2. Try typing the URL manually: `http://localhost:8501`
3. Try a different browser (Chrome, Safari, Firefox)

### "All agents were already scraped"
**Problem:** Search returns 0 results with this message

**Solution:** You've already scraped these agents before!
1. Either search a different location (different state/city)
2. Or uncheck "Skip Previously Scraped Agents" in Advanced Options
3. Or click "Clear Scraping History" to reset

### Getting 403 Forbidden errors
**Problem:** The scraper says "403 Forbidden" when trying to fetch agents

**Solution:**
- **Mobile user agents are enabled by default**, which helps avoid this
- If you still get blocked:
  1. Wait 10-15 minutes before trying again
  2. Try a different location
  3. Consider using a proxy (see Proxy section below)

### Slow performance
**Problem:** Taking a very long time to scrape agents

**Solution:**
- **This is normal!** The tool uses intelligent delays to avoid detection:
  - 15-60 seconds between batches
  - 20-40 minute breaks after every 5-15 agents
- Fetching 100 agents with full profiles can take 1-2 hours
- Set `limit` to a smaller number (10-20) for testing

---

## 🌐 Using a Proxy (Advanced)

If you need to use a proxy to avoid restrictions:

1. Get a **paid residential proxy** (free proxies don't work with Zillow)
   - Recommended: Bright Data, Smartproxy, Oxylabs
2. In the Advanced Options, expand **"🌐 Proxy Configuration"**
3. Enter your proxy in this format:
   ```
   http://username:password@proxy-host:port
   ```
4. The tool will route all requests through your proxy

**Note:** Mobile user agents (enabled by default) work well enough that most users won't need a proxy.

---

## 🎓 Python Library Usage (For Developers)

If you're comfortable with Python, you can also use AgentHarvest as a library:

```python
from agentharvest import scrape_agent

# Search for agents
agents = scrape_agent(
    state="CA",
    rating_min=4.5,
    sales_min=10,
    limit=50
)

# Export to CSV
agents.to_csv("california_agents.csv", index=False)
print(f"Found {len(agents)} agents")
```

**Available Parameters:**
```python
scrape_agent(
    # Location (at least one required)
    state="CA",                    # State name or abbreviation
    city="San Diego",              # City name
    zip_code="92101",              # ZIP code

    # Filters
    rating_min=4.5,                # Minimum rating 0-5
    review_count_min=10,           # Minimum number of reviews
    sales_min=10,                  # Minimum sales in last 12 months
    sales_max=100,                 # Maximum sales in last 12 months
    years_experience_min=5,        # Minimum years of experience
    specialties=["buyer_agent"],   # Filter by specialties
    languages=["English", "Spanish"], # Filter by languages
    is_top_agent=True,             # Only Zillow Premier Agents
    exclude_teams=True,            # Exclude team listings
    agent_type="solo",             # "solo", "team", or "broker"

    # Control
    limit=100,                     # Max results (max: 1000)
    offset=0,                      # Starting position
    fetch_profiles=True,           # Fetch comprehensive data

    # Duplicate Prevention
    skip_scraped=True,             # Skip previously scraped agents
    history_file=None,             # Custom history file path

    # Technical
    proxy="http://user:pass@host:port",  # Proxy URL
    timeout=30,                    # Request timeout in seconds
)
```

**Clear Scraping History:**
```python
from agentharvest import clear_scraping_history

clear_scraping_history()  # Clear all history
```

---

## ⚙️ How It Works (Technical Details)

### Anti-Detection Features
AgentHarvest includes advanced anti-bot detection bypass:

- **Mobile User Agents**: Uses iOS/Android browsers (enabled by default)
- **User Agent Rotation**: 17 different browser/OS combinations
- **Referrer Headers**: Simulates real navigation (homepage → search → profile)
- **Session Persistence**: Maintains cookies like a real browser
- **Random Order Fetching**: Fetches profiles in random order
- **Warm-up Requests**: Visits homepage before scraping
- **Accept-Language Rotation**: Simulates users from different regions
- **Intelligent Batching**: Random delays (15-60s), breaks (20-40 min)

All features work automatically - no configuration needed!

### Duplicate Prevention
Two-level system to prevent duplicate agents:

1. **Within a Single Run**: Automatically removes duplicates by agent_id
2. **Across Multiple Runs**: Tracks all scraped agent IDs in `~/.agentharvest_history.json`

History persists across days, weeks, and months until manually cleared.

### How Data is Collected
1. **Initial Search**: Fetches agent list from Zillow search API
2. **Profile Fetching**: Visits each agent's profile page for comprehensive data
3. **Intelligent Rate Limiting**: Adds random delays to avoid detection
4. **Data Processing**: Extracts all available fields and formats them
5. **CSV Export**: Converts to clean CSV format for easy use

---

## 📝 Example Use Cases

### Use Case 1: Building a Lead List
**Goal:** Get 500 top-rated agents in California for outreach

```python
from agentharvest import scrape_agent

agents = scrape_agent(
    state="CA",
    rating_min=4.5,
    sales_min=10,
    limit=500
)

agents.to_csv("ca_top_agents.csv", index=False)
```

**In Streamlit:**
1. Enter State: "CA"
2. Set Limit: 500
3. Advanced Options → Rating: 4.5
4. Advanced Options → Min Sales: 10
5. Click Search
6. Download CSV

### Use Case 2: Multi-City Campaign
**Goal:** Scrape agents from 5 different cities over a week

**Day 1:**
```python
agents = scrape_agent(city="San Diego", state="CA", limit=100)
agents.to_csv("day1_san_diego.csv", index=False)
```

**Day 2:**
```python
agents = scrape_agent(city="Los Angeles", state="CA", limit=100)
agents.to_csv("day2_los_angeles.csv", index=False)
```

**Result:** All agents are unique (duplicate prevention active)

### Use Case 3: Market Research
**Goal:** Analyze agent distribution by experience level

```python
# Get all agents in Nevada
all_agents = scrape_agent(state="NV", limit=500)

# Analyze in pandas
import pandas as pd
experience_dist = all_agents['years_experience'].value_counts()
print(experience_dist)

avg_rating_by_experience = all_agents.groupby('years_experience')['rating'].mean()
print(avg_rating_by_experience)
```

---

## ⚠️ Disclaimer

**USE AT YOUR OWN RISK.** This software is provided "as is" without warranty of any kind. The authors and contributors are not responsible for any consequences, damages, or legal issues arising from the use of this software.

By using this tool, you agree that:
- You are solely responsible for compliance with Zillow's Terms of Service
- You will not use this tool for spamming, harassment, or unauthorized contact
- You will not use this tool for any illegal purposes
- The authors bear no liability for your actions or how you use this software
- You understand that web scraping may violate terms of service and carry legal risks

This tool is provided for educational and research purposes only. Users must conduct their own legal review before any commercial use.

---

## 🆘 Need Help?

### Common Questions

**Q: How long does it take to scrape 100 agents?**
A: With full profile fetching, expect 1-2 hours due to intelligent rate limiting.

**Q: Can I scrape multiple states at once?**
A: Not in a single search, but you can run multiple searches and combine the CSVs.

**Q: Will I get banned from Zillow?**
A: The tool uses advanced anti-detection. Follow best practices (reasonable limits, use mobile UAs).

**Q: Do I need to pay for a proxy?**
A: Usually no - mobile user agents work well. Only needed if you hit restrictions.

**Q: Can I use this on Windows?**
A: Yes, but the setup instructions above are for Mac. The process is similar on Windows.

**Q: How do I update to the latest version?**
A: In Terminal, run:
```bash
cd ~/Desktop/AgentHarvest
git pull
pip3 install -r requirements.txt --upgrade
```

**Q: How do I run this again in the future?**
A: Just open Terminal and run:
```bash
cd ~/Desktop/AgentHarvest
streamlit run app.py
```

---

## 🙏 Support

If you find this tool useful, please star the repository on GitHub!

**Found a bug?** Open an issue on GitHub with details about what happened.

**Have a feature request?** Open an issue describing what you'd like to see.

---

## 📚 Additional Documentation

- [ANTI_DETECTION.md](ANTI_DETECTION.md) - Detailed anti-detection techniques
- [DUPLICATE_PREVENTION.md](DUPLICATE_PREVENTION.md) - How duplicate prevention works
- [INTELLIGENT_BATCHING.md](INTELLIGENT_BATCHING.md) - Batching and rate limiting details

---

**Happy Agent Hunting! 🏠🔍**

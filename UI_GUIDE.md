# AgentHarvest Web UI Guide

Simple web interface for scraping Zillow agents - perfect for non-technical users!

## Quick Start

### 1. Install Requirements

```bash
pip install streamlit
```

### 2. Run the App

```bash
streamlit run app.py
```

This will automatically open your web browser to the app (usually at http://localhost:8501)

## How to Use

### Basic Search

1. **Enter a State** (required)
   - Example: "California" or "CA"

2. **Add Filters** (optional)
   - Minimum Rating: Slider from 0-5 stars
   - Minimum Sales: Number of sales in last 12 months
   - Agent Type: Solo, Team, or Broker

3. **Click "Search Agents"**

4. **Download CSV** when results appear

### Example Searches

**Find Top Agents in Texas:**
- State: `Texas`
- Minimum Rating: `4.5`
- Minimum Sales: `10`
- Click Search

**Find Solo Agents in California:**
- State: `California`
- Agent Type: `Solo`
- Click Search

**Find Agents in Miami:**
- State: `FL`
- City: `Miami`
- Click Search

## Understanding Results

### Columns in CSV

**Basic Info:**
- `name`: Agent's full name
- `phone`: Phone number (if available)
- `email`: Email address (if available)
- `brokerage_name`: Company name

**Performance:**
- `rating`: Average rating (0-5 stars)
- `review_count`: Number of reviews
- `sales_last_12_months`: Sales in last year
- `total_sales`: Total sales in region

**Status:**
- `agent_type`: solo, team, or broker
- `agent_badge`: "ZILLOW PREMIER AGENT" for top agents
- `is_team`: True/False

**Location:**
- `city`: Agent's city
- `state`: Agent's state
- `zip_code`: Agent's ZIP code

### Tips

1. **Start Small**: Use limit of 5-10 for testing
2. **Be Patient**: Each agent takes ~2.5 seconds to fetch (to avoid rate limits)
3. **Use Filters**: Narrow down results with rating/sales filters
4. **Save CSVs**: Download and organize your data

## Troubleshooting

### "Rate Limit Detected" Error

**What happened:** Too many requests to Zillow

**Solutions:**
1. Wait 15-30 minutes
2. Use different network/WiFi
3. Reduce the limit (fewer results)

### No Results Found

**Solutions:**
1. Try broader search (state only, no city)
2. Lower the minimum rating
3. Remove filters
4. Check spelling of state/city

### App Won't Start

**Solution:**
```bash
# Make sure you're in the right directory
cd /Users/yevgeniymatsay/Desktop/AgentHarvest

# Install streamlit if you haven't
pip install streamlit

# Run the app
streamlit run app.py
```

## Advanced Features

### Comprehensive Data (Default)

By default, the app fetches **full profiles** including:
- Phone numbers
- Email addresses
- Specialties
- Languages
- Certifications

**Slower but complete data (recommended)**

### Fast Mode

Uncheck "Fetch Comprehensive Data" for faster searches:
- No phone/email
- Basic info only (name, rating, sales)
- Much faster (good for large searches)

## Keyboard Shortcuts

- `Ctrl+C` in terminal: Stop the app
- `R` in browser: Rerun search with same parameters
- `C` in browser: Clear cache

## Sharing with Non-Technical Users

To let your partner use this:

### Option 1: Local Access
1. Run `streamlit run app.py` on your computer
2. Tell them to open: `http://YOUR-IP:8501`
3. They can access it from any device on same WiFi

### Option 2: Deploy Online (Free)

Deploy to Streamlit Cloud (free hosting):

1. Push your code to GitHub
2. Go to https://share.streamlit.io
3. Connect your GitHub repo
4. Deploy `app.py`
5. Share the public URL with your partner

**Example:** `https://your-app.streamlit.app`

Now they can use it from anywhere without any setup!

## Support

For questions or issues:
1. Check this guide first
2. Make sure you waited 15+ minutes since last request
3. Try with a smaller limit (5 agents)
4. Check your internet connection

---

**Made with ❤️ for non-technical real estate professionals**

"""
Production Configuration
Modify these settings for your scraping needs
"""

# ==============================================================================
# SCRAPING SETTINGS - Adjust these for your needs
# ==============================================================================

# CONSERVATIVE (Safest - Never blocked)
# ~3-4 agents/hour, ~75-100 agents/day
CONSERVATIVE = {
    'delay_min': 15,        # Minimum seconds between requests
    'delay_max': 25,        # Maximum seconds between requests
    'batch_size': 5,        # Agents per batch
    'batch_break': 3600,    # Break between batches (seconds)
}

# BALANCED (Recommended - Very safe)
# ~10-15 agents/hour, ~250-350 agents/day
BALANCED = {
    'delay_min': 10,
    'delay_max': 20,
    'batch_size': 10,
    'batch_break': 1800,    # 30 minutes
}

# AGGRESSIVE (Use with caution)
# ~30-40 agents/hour, ~700-900 agents/day
AGGRESSIVE = {
    'delay_min': 5,
    'delay_max': 10,
    'batch_size': 15,
    'batch_break': 900,     # 15 minutes
}

# ==============================================================================
# CHOOSE YOUR MODE (edit this line)
# ==============================================================================
CURRENT_MODE = BALANCED  # Change to CONSERVATIVE or AGGRESSIVE as needed

# ==============================================================================
# STATES TO SCRAPE
# ==============================================================================
STATES = [
    "Nevada",
    "Florida",
    "Texas",
    "California",
    # Add more states here
]

# ==============================================================================
# TARGETS
# ==============================================================================
AGENTS_PER_STATE = 50  # How many agents to get per state

# ==============================================================================
# OUTPUT
# ==============================================================================
OUTPUT_DIR = "./scraped_agents"

# ==============================================================================
# FILTERS (Optional)
# ==============================================================================
FILTERS = {
    'rating_min': 4.0,      # Minimum rating (0-5), set to None to disable
    'sales_min': 10,        # Minimum sales, set to None to disable
    'is_top_agent': None,   # True/False/None
    'agent_type': None,     # "solo"/"team"/"broker"/None
}

# ==============================================================================
# PROXY (Optional)
# ==============================================================================
# If you have a proxy, set it here
# Format: "http://username:password@proxy-host:port"
PROXY = None

# Example:
# PROXY = "http://user:pass@proxy.example.com:8080"

# ==============================================================================
# NOTES
# ==============================================================================
"""
How to use:

1. Choose your mode above (CONSERVATIVE, BALANCED, or AGGRESSIVE)
2. Add states you want to scrape
3. Set how many agents per state
4. Run: python run_production.py

Example outputs:
- CONSERVATIVE: ~75-100 agents/day (zero risk)
- BALANCED: ~250-350 agents/day (very safe) ⭐ RECOMMENDED
- AGGRESSIVE: ~700-900 agents/day (may get blocked)

Tips:
- Start with BALANCED mode
- If you get 403 errors, switch to CONSERVATIVE
- If running smoothly, can try AGGRESSIVE
- Use proxy for faster scraping without risk
"""

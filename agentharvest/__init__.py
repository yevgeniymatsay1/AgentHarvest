"""
AgentHarvest - Zillow Real Estate Agent Scraper
"""

import pandas as pd
from typing import Optional, List
from .core.scrapers.models import Agent, SearchInput, ReturnType, AgentType
from .core.scrapers.zillow import ZillowScraper
from .core.scrapers.zillow.history import ScrapingHistory


__version__ = "1.0.0"


def scrape_agent(
    # Location (at least one required)
    state: Optional[str] = None,
    city: Optional[str] = None,
    zip_code: Optional[str] = None,
    # Filters
    rating_min: Optional[float] = None,
    review_count_min: Optional[int] = None,
    sales_min: Optional[int] = None,
    sales_max: Optional[int] = None,
    years_experience_min: Optional[int] = None,
    specialties: Optional[List[str]] = None,
    languages: Optional[List[str]] = None,
    is_top_agent: Optional[bool] = None,
    exclude_teams: bool = False,
    agent_type: Optional[str] = None,
    # Control
    limit: int = 100,
    offset: int = 0,
    fetch_profiles: bool = True,  # Fetch comprehensive data by default
    # Duplicate prevention
    skip_scraped: bool = True,  # Skip agents scraped in previous runs
    history_file: Optional[str] = None,  # Custom history file location
    # Technical
    proxy: Optional[str] = None,
    timeout: int = 30,
) -> pd.DataFrame:
    """
    Scrape real estate agents from Zillow.com

    Args:
        state: State name or abbreviation (e.g., "CA", "California")
        city: City name (e.g., "San Diego")
        zip_code: ZIP code (e.g., "92101")

        rating_min: Minimum rating 0-5
        review_count_min: Minimum number of reviews
        sales_min: Minimum sales in last 12 months
        sales_max: Maximum sales in last 12 months
        years_experience_min: Minimum years of experience
        specialties: List of specialties to filter by
        languages: List of languages to filter by
        is_top_agent: Filter for top agents only (True/False)
        exclude_teams: Exclude team listings (default: False)
        agent_type: Filter by agent type - "solo", "team", or "broker" (default: None shows all)

        limit: Maximum number of results to return (default: 100, max: 1000)
        offset: Starting position for pagination (default: 0)
        fetch_profiles: Fetch comprehensive data from individual profiles (default: True)
                       Uses intelligent batching with random delays (15-60s) and breaks (20-40 min)
                       Set to False for faster searches without phone/email/specialties

        skip_scraped: Skip agents that were scraped in previous runs (default: True)
                     Tracks agent IDs in ~/.agentharvest_history.json
                     Set to False to allow re-scraping same agents
        history_file: Custom path to history file (optional)
                     Defaults to ~/.agentharvest_history.json if not specified

        proxy: Proxy in format 'http://user:pass@host:port'
        timeout: Request timeout in seconds (default: 30)

    Returns:
        pandas DataFrame with agent data

    Raises:
        ValueError: If no location parameter provided
        Exception: If scraping fails

    Example:
        ```python
        from agentharvest import scrape_agent

        # Search for top-rated agents in California
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

    Available Agent Fields in DataFrame:
        - agent_id: Unique agent identifier
        - name: Agent full name
        - brokerage_name: Brokerage/company name
        - profile_url: Link to agent profile
        - photo_url: Agent photo URL
        - agent_badge: "ZILLOW PREMIER AGENT" for top agents, empty otherwise
        - is_team: Whether this is a team listing
        - agent_type: Agent type (solo, team, or broker)
        - rating: Average rating 0-5
        - review_count: Total number of reviews
        - sales_last_12_months: Sales in last 12 months
        - total_sales: Total sales in region
        - price_range: Price range handled
        - tags: Certifications and badges
        - years_experience_min: Minimum years of experience

    Note:
        - Comprehensive data (phone/email/specialties) fetched by default (1 request per agent)
        - Set fetch_profiles=False for faster searches with basic data only
        - Initial search returns ~5-15 agents per location
        - Uses curl_cffi with browser impersonation (bypasses anti-bot detection)
        - Much faster than browser automation - no Chromium needed!

    """
    # Convert agent_type string to AgentType enum if provided
    agent_type_enum = None
    if agent_type is not None:
        if agent_type.lower() == "solo":
            agent_type_enum = AgentType.SOLO
        elif agent_type.lower() == "team":
            agent_type_enum = AgentType.TEAM
        elif agent_type.lower() == "broker":
            agent_type_enum = AgentType.BROKER
        else:
            raise ValueError(
                f"Invalid agent_type: '{agent_type}'. Must be one of: 'solo', 'team', 'broker'"
            )

    # Create SearchInput
    search_input = SearchInput(
        state=state,
        city=city,
        zip_code=zip_code,
        rating_min=rating_min,
        review_count_min=review_count_min,
        sales_min=sales_min,
        sales_max=sales_max,
        years_experience_min=years_experience_min,
        specialties=specialties,
        languages=languages,
        is_top_agent=is_top_agent,
        exclude_teams=exclude_teams,
        agent_type=agent_type_enum,
        limit=limit,
        offset=offset,
        fetch_profiles=fetch_profiles,
        proxy=proxy,
        timeout=timeout,
        return_type=ReturnType.pandas,
    )

    # Validate location
    if not search_input.validate_location():
        raise ValueError(
            "Must provide at least one location parameter: state, city, or zip_code\n"
            "Examples:\n"
            "  scrape_agent(state='CA')\n"
            "  scrape_agent(city='San Diego', state='CA')\n"
            "  scrape_agent(zip_code='92101')"
        )

    # Initialize history tracker (if enabled)
    history = None
    if skip_scraped:
        history = ScrapingHistory(history_file)
        print()  # Add spacing after history load

    # Run scraper
    scraper = ZillowScraper(search_input)
    agents = scraper.search_agents()

    # Filter out previously scraped agents (if enabled)
    if history and agents:
        before_count = len(agents)
        agents = history.filter_new(agents)

        # Save new agent IDs to history
        if agents:
            new_ids = [agent.agent_id for agent in agents]
            history.add_many(new_ids)
            history.save()

        # If all were duplicates, inform user
        if len(agents) == 0:
            print(f"\n⚠️  All {before_count} agents were already scraped in previous runs")
            print(f"   Use skip_scraped=False to re-scrape them")

    # Convert to DataFrame
    df = _agents_to_dataframe(agents)

    return df


def _agents_to_dataframe(agents: List[Agent]) -> pd.DataFrame:
    """
    Convert list of Agent objects to pandas DataFrame

    Args:
        agents: List of Agent objects

    Returns:
        pandas DataFrame with agent data
    """
    if not agents:
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=[
            'agent_id', 'name', 'brokerage_name', 'profile_url', 'photo_url',
            'agent_badge', 'is_team', 'agent_type', 'rating', 'review_count',
            'sales_last_12_months', 'total_sales', 'price_range',
            'price_range_min', 'price_range_max', 'tags', 'years_experience_min',
            # Optional fields from profiles
            'phone', 'email', 'address', 'city', 'state', 'zip_code',
            'specialties', 'languages', 'certifications'
        ])

    records = []
    for agent in agents:
        record = {
            # IDs
            'agent_id': agent.agent_id,
            'profile_url': agent.profile_url,

            # Basic Info
            'name': agent.name,
            'brokerage_name': agent.brokerage_name,

            # Media
            'photo_url': str(agent.photo_url) if agent.photo_url else None,

            # Status
            'agent_badge': 'ZILLOW PREMIER AGENT' if agent.is_top_agent else None,
            'is_team': agent.is_team,
            'agent_type': agent.agent_type.value if agent.agent_type else None,

            # Ratings
            'rating': agent.rating,
            'rating_text': agent.rating_text,
            'review_count': agent.review_count,

            # Performance
            'sales_last_12_months': agent.sales_last_12_months,
            'total_sales': agent.total_sales,
            'price_range': agent.price_range,
            'price_range_min': agent.price_range_min,
            'price_range_max': agent.price_range_max,

            # Experience
            'tags': ', '.join(agent.tags) if agent.tags else None,
            'years_experience_min': agent.years_experience_min,

            # Contact (from profile fetch)
            'phone': agent.phone,
            'email': agent.email,
            'website': str(agent.website) if agent.website else None,

            # Location (from profile fetch)
            'address': agent.address,
            'city': agent.city,
            'state': agent.state,
            'zip_code': agent.zip_code,

            # Professional Details (from profile fetch)
            'title': agent.title,
            'years_experience': agent.years_experience,
            'specialties': ', '.join(agent.specialties) if agent.specialties else None,
            'languages': ', '.join(agent.languages) if agent.languages else None,
            'certifications': ', '.join(agent.certifications) if agent.certifications else None,
            'biography': agent.biography,

            # Brokerage
            'brokerage_phone': agent.brokerage_phone,
            'brokerage_address': agent.brokerage_address,

            # Listings
            'active_listings': agent.active_listings,
            'for_sale_listings': agent.for_sale_listings,
            'for_rent_listings': agent.for_rent_listings,
            'total_listings': agent.total_listings,

            # Performance Details
            'recent_sales_count': len(agent.recent_sales),
            'reviews_count': len(agent.reviews),
            'neighborhoods_served': ', '.join(agent.neighborhoods_served) if agent.neighborhoods_served else None,
            'market_expertise': ', '.join(agent.market_expertise) if agent.market_expertise else None,
        }

        records.append(record)

    return pd.DataFrame(records)


def clear_scraping_history(history_file: Optional[str] = None):
    """
    Clear all scraped agent history

    Useful when you want to start fresh and allow re-scraping previously seen agents

    Args:
        history_file: Optional custom history file path
                     Defaults to ~/.agentharvest_history.json

    Example:
        >>> from agentharvest import clear_scraping_history
        >>> clear_scraping_history()  # Clear all history
    """
    history = ScrapingHistory(history_file)
    history.clear()
    print(f"✅ History cleared: {history.get_history_file()}")


# Export main function and models
__all__ = ['scrape_agent', 'clear_scraping_history', 'Agent', 'SearchInput']

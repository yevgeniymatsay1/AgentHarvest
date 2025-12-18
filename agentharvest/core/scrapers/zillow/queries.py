"""
URL builders for Zillow agent search
"""

from ..models import SearchInput


def build_agent_search_url(search_input: SearchInput) -> str:
    """
    Build Zillow agent directory URL from search parameters

    Args:
        search_input: Search parameters

    Returns:
        Full URL for agent search

    Examples:
        - State only: https://www.zillow.com/professionals/real-estate-agent-reviews/california/
        - City + State: https://www.zillow.com/professionals/real-estate-agent-reviews/san-diego-ca/
        - ZIP: https://www.zillow.com/professionals/real-estate-agent-reviews/92101/
    """
    base_url = "https://www.zillow.com/professionals/real-estate-agent-reviews"

    # Get location slug
    location_slug = search_input.get_location_slug()

    if location_slug:
        return f"{base_url}/{location_slug}/"
    else:
        # Default to base URL (will show agents from user's location or default)
        return f"{base_url}/"


def build_agent_profile_url(agent_id: str, agent_slug: str = None) -> str:
    """
    Build URL for individual agent profile

    Args:
        agent_id: Agent's encodedZuid
        agent_slug: URL-friendly agent name (optional, for validation)

    Returns:
        Full URL to agent profile

    Note:
        Profile URL is usually already in agent.profile_url from search results
    """
    # Profile URLs are typically: https://www.zillow.com/profile/{slug}
    # We already get these from search results, but this can construct them if needed

    if agent_slug:
        return f"https://www.zillow.com/profile/{agent_slug}"
    else:
        # Cannot construct without slug, return placeholder
        return f"https://www.zillow.com/profile/agent-{agent_id}"

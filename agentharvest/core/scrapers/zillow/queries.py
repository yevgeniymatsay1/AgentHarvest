"""
URL builders for Zillow agent search
"""

from ..models import SearchInput


def build_agent_search_url(search_input: SearchInput, page: int = 1) -> str:
    """
    Build Zillow agent directory URL from search parameters

    Args:
        search_input: Search parameters
        page: Page number for pagination (default: 1)

    Returns:
        Full URL for agent search

    Examples:
        - State only: https://www.zillow.com/professionals/real-estate-agent-reviews/california/
        - City + State: https://www.zillow.com/professionals/real-estate-agent-reviews/san-diego-ca/
        - ZIP: https://www.zillow.com/professionals/real-estate-agent-reviews/92101/
        - With page: https://www.zillow.com/professionals/real-estate-agent-reviews/california/?page=2
    """
    base_url = "https://www.zillow.com/professionals/real-estate-agent-reviews"

    # Get location slug
    location_slug = search_input.get_location_slug()

    if location_slug:
        base = f"{base_url}/{location_slug}/"
    else:
        # Default to base URL (will show agents from user's location or default)
        base = f"{base_url}/"

    # Add page parameter if not first page
    if page > 1:
        return f"{base}?page={page}"

    return base


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

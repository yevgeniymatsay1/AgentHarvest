"""
Agent data processing and filtering
"""

from typing import List
from ..models import Agent, SearchInput


def apply_filters(agents: List[Agent], search_input: SearchInput) -> List[Agent]:
    """
    Apply client-side filters to agent list

    Args:
        agents: List of Agent objects
        search_input: Search parameters with filters

    Returns:
        Filtered list of Agent objects
    """
    filtered = agents

    # Filter by rating
    if search_input.rating_min is not None:
        filtered = [
            agent for agent in filtered
            if agent.rating is not None and agent.rating >= search_input.rating_min
        ]

    # Filter by review count
    if search_input.review_count_min is not None:
        filtered = [
            agent for agent in filtered
            if agent.review_count >= search_input.review_count_min
        ]

    # Filter by sales (last 12 months)
    if search_input.sales_min is not None:
        filtered = [
            agent for agent in filtered
            if agent.sales_last_12_months is not None and agent.sales_last_12_months >= search_input.sales_min
        ]

    if search_input.sales_max is not None:
        filtered = [
            agent for agent in filtered
            if agent.sales_last_12_months is not None and agent.sales_last_12_months <= search_input.sales_max
        ]

    # Filter by years of experience
    if search_input.years_experience_min is not None:
        filtered = [
            agent for agent in filtered
            if agent.years_experience_min is not None and agent.years_experience_min >= search_input.years_experience_min
        ]

    # Filter by top agent status
    if search_input.is_top_agent is not None:
        filtered = [
            agent for agent in filtered
            if agent.is_top_agent == search_input.is_top_agent
        ]

    # Exclude teams if requested
    if search_input.exclude_teams:
        filtered = [
            agent for agent in filtered
            if not agent.is_team
        ]

    # Filter by agent type (if provided)
    if search_input.agent_type is not None:
        filtered = [
            agent for agent in filtered
            if agent.agent_type == search_input.agent_type
        ]

    # Filter by specialties (if provided)
    if search_input.specialties:
        filtered = [
            agent for agent in filtered
            if any(
                specialty.lower() in ' '.join(agent.specialties).lower()
                for specialty in search_input.specialties
            )
        ]

    # Filter by languages (if provided)
    if search_input.languages:
        filtered = [
            agent for agent in filtered
            if any(
                language.lower() in ' '.join(agent.languages).lower()
                for language in search_input.languages
            )
        ]

    return filtered


def deduplicate_agents(agents: List[Agent]) -> List[Agent]:
    """
    Remove duplicate agents based on agent_id

    Args:
        agents: List of Agent objects

    Returns:
        Deduplicated list of Agent objects
    """
    seen_ids = set()
    unique_agents = []

    for agent in agents:
        if agent.agent_id not in seen_ids:
            seen_ids.add(agent.agent_id)
            unique_agents.append(agent)

    return unique_agents


def sort_agents(agents: List[Agent], sort_by: str = 'rating', descending: bool = True) -> List[Agent]:
    """
    Sort agents by specified field

    Args:
        agents: List of Agent objects
        sort_by: Field to sort by ('rating', 'review_count', 'sales_last_12_months', 'name')
        descending: Sort in descending order (True) or ascending (False)

    Returns:
        Sorted list of Agent objects
    """
    sort_key_map = {
        'rating': lambda a: (a.rating is not None, a.rating or 0),
        'review_count': lambda a: a.review_count,
        'sales_last_12_months': lambda a: (a.sales_last_12_months is not None, a.sales_last_12_months or 0),
        'total_sales': lambda a: (a.total_sales is not None, a.total_sales or 0),
        'name': lambda a: a.name.lower(),
    }

    if sort_by not in sort_key_map:
        # Default to rating if unknown sort field
        sort_by = 'rating'

    try:
        return sorted(agents, key=sort_key_map[sort_by], reverse=descending)
    except Exception as e:
        print(f"⚠️  Sort failed: {e}. Returning unsorted list.")
        return agents


def limit_results(agents: List[Agent], limit: int, offset: int = 0) -> List[Agent]:
    """
    Apply pagination limits to agent list

    Args:
        agents: List of Agent objects
        limit: Maximum number of results to return
        offset: Starting position (skip first N agents)

    Returns:
        Sliced list of Agent objects
    """
    return agents[offset:offset + limit]

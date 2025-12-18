"""
HTML/JSON parsing functions for Zillow agent data
"""

import json
import re
from typing import Dict, List, Optional
from ..models import Agent, ProfileData, ReviewInformation, AgentTag


def extract_next_data(html: str) -> Dict:
    """
    Extract __NEXT_DATA__ JSON from Zillow HTML

    Args:
        html: Full HTML content from page

    Returns:
        Parsed JSON data from __NEXT_DATA__

    Raises:
        Exception: If __NEXT_DATA__ not found or invalid JSON
    """
    # Find __NEXT_DATA__ script tag
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html,
        re.DOTALL
    )

    if not match:
        raise Exception("Could not find __NEXT_DATA__ in HTML. Page structure may have changed.")

    try:
        data = json.loads(match.group(1))
        return data
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse __NEXT_DATA__ JSON: {e}")


def extract_agent_results(next_data: Dict) -> List[Dict]:
    """
    Navigate __NEXT_DATA__ structure to find agent results

    Args:
        next_data: Parsed __NEXT_DATA__ JSON

    Returns:
        List of agent card dictionaries

    Raises:
        KeyError: If expected data structure not found
    """
    try:
        # Navigate to agent results
        props = next_data['props']['pageProps']
        agent_finder_data = props['displayData']['agentFinderGraphData']
        agent_directory = agent_finder_data['agentDirectoryFinderDisplay']
        search_results = agent_directory['searchResults']
        results = search_results['results']
        results_cards = results['resultsCards']

        return results_cards

    except KeyError as e:
        raise Exception(f"Data structure changed. Missing key: {e}")


def parse_agent_card(card: Dict) -> Optional[Agent]:
    """
    Parse individual agent card from search results

    Args:
        card: Agent card dictionary from resultsCards

    Returns:
        Agent object or None if card is not an agent (e.g., ad card)
    """
    # Skip non-agent cards (ads, PLCs, etc.)
    if card.get('__typename') != 'AgentDirectoryFinderProfileResultsCard':
        return None

    try:
        # Basic identifiers
        agent_id = card.get('encodedZuid', '')
        name = card.get('cardTitle', '')
        profile_url = card.get('cardActionLink', '')

        if not agent_id or not name or not profile_url:
            # Invalid agent data
            return None

        # Basic info
        brokerage_name = card.get('secondaryCardTitle')
        photo_url = card.get('imageUrl')
        logo_url = card.get('logoUrl')
        is_top_agent = card.get('isTopAgent', False)

        # Parse review information
        review_info_data = card.get('reviewInformation', {})
        review_info = ReviewInformation(
            review_average=review_info_data.get('reviewAverage'),
            review_average_text=review_info_data.get('reviewAverageText'),
            review_count_text=review_info_data.get('reviewCountText'),
            no_reviews_text=review_info_data.get('noReviewsText')
        )

        # Extract review count from text like "(123)"
        review_count = 0
        if review_info.review_count_text:
            count_match = re.sub(r'[^\d]', '', review_info.review_count_text)
            if count_match:
                review_count = int(count_match)

        # Parse profile data (sales, price range, etc.)
        profile_data_raw = card.get('profileData', [])
        profile_data_list = [
            ProfileData(label=item['label'], data=item['data'])
            for item in profile_data_raw
            if item.get('data') is not None  # Skip items with None data
        ]

        # Extract specific fields from profile data
        price_range = None
        price_range_min = None
        price_range_max = None
        sales_last_12_months = None
        total_sales = None

        for item in profile_data_raw:
            label = item.get('label', '').lower()
            data_value = item.get('data', '')

            if 'price range' in label:
                price_range = data_value
                # Parse min/max from "$78K - $2.4M" format
                prices = re.findall(r'\$[\d.]+[KMB]?', data_value)
                if len(prices) >= 2:
                    price_range_min = prices[0]
                    price_range_max = prices[1]

            elif 'sales last 12 months' in label or 'last 12 months' in label:
                # Extract number
                sales_match = re.sub(r'[^\d]', '', data_value)
                if sales_match:
                    sales_last_12_months = int(sales_match)

            elif 'sales in' in label or 'total sales' in label:
                # Extract number
                sales_match = re.sub(r'[^\d]', '', data_value)
                if sales_match:
                    total_sales = int(sales_match)

        # Parse tags
        tags_data = card.get('tags', [])
        tags = [tag.get('text', '') for tag in tags_data if tag.get('text')]

        # Determine if team
        is_team = any('TEAM' in tag.upper() for tag in tags)

        # Extract years of experience from tags
        years_experience_min = None
        for tag in tags:
            if 'YRS' in tag.upper() or 'YEARS' in tag.upper():
                # Extract number from "LICENSED 10+ YRS"
                years_match = re.search(r'(\d+)', tag)
                if years_match:
                    years_experience_min = int(years_match.group(1))
                    break

        # Create Agent object
        agent = Agent(
            agent_id=agent_id,
            name=name,
            profile_url=profile_url,
            brokerage_name=brokerage_name,
            photo_url=photo_url,
            logo_url=logo_url,
            is_top_agent=is_top_agent,
            is_team=is_team,
            rating=review_info.review_average,
            rating_text=review_info.review_average_text,
            review_count=review_count,
            review_information=review_info,
            price_range=price_range,
            price_range_min=price_range_min,
            price_range_max=price_range_max,
            sales_last_12_months=sales_last_12_months,
            total_sales=total_sales,
            tags=tags,
            years_experience_min=years_experience_min,
            profile_data=profile_data_list,
        )

        return agent

    except Exception as e:
        print(f"⚠️  Failed to parse agent card: {e}")
        return None


def parse_agents_from_html(html: str) -> List[Agent]:
    """
    Extract all agents from Zillow HTML page

    Args:
        html: Full HTML content from Zillow agent directory page

    Returns:
        List of Agent objects

    Raises:
        Exception: If data extraction fails
    """
    # Extract __NEXT_DATA__
    next_data = extract_next_data(html)

    # Get agent results
    results_cards = extract_agent_results(next_data)

    # Parse each card
    agents = []
    for card in results_cards:
        agent = parse_agent_card(card)
        if agent:
            agents.append(agent)

    return agents


def get_search_metadata(next_data: Dict) -> Dict[str, any]:
    """
    Extract search metadata (total count, current page, etc.)

    Args:
        next_data: Parsed __NEXT_DATA__ JSON

    Returns:
        Dictionary with metadata:
        - total_results: Total agents available
        - current_page: Current page number
        - results_on_page: Number of results loaded on this page
        - location: Location being searched
    """
    try:
        props = next_data['props']['pageProps']
        agent_finder_data = props['displayData']['agentFinderGraphData']
        agent_directory = agent_finder_data['agentDirectoryFinderDisplay']
        search_results = agent_directory['searchResults']

        metadata = {
            'total_results': search_results.get('resultsFound', 0),
            'current_page': search_results.get('currentPage', 1),
            'results_on_page': len(search_results.get('results', {}).get('resultsCards', [])),
            'location': props.get('region', {}).get('name', 'Unknown'),
        }

        return metadata

    except (KeyError, TypeError) as e:
        # Return empty metadata if structure is unexpected
        return {
            'total_results': 0,
            'current_page': 1,
            'results_on_page': 0,
            'location': 'Unknown',
        }


def parse_agent_profile(html: str, agent: Agent) -> Agent:
    """
    Parse comprehensive agent data from individual profile page

    Args:
        html: Full HTML content from agent profile page
        agent: Existing Agent object to enhance with profile data

    Returns:
        Agent object with enhanced profile data (phone, email, etc.)

    Raises:
        Exception: If profile data extraction fails
    """
    try:
        # Extract __NEXT_DATA__ from profile page
        next_data = extract_next_data(html)

        # Navigate to profile data - structure is different for profile pages
        props = next_data.get('props', {}).get('pageProps', {})

        # Main profile data is in displayUser
        display_user = props.get('displayUser', {})
        professional_info = props.get('professionalInformation', [])

        # Determine agent type from profileTypes
        from ..models import AgentType
        agent_type = None
        profile_types = display_user.get('profileTypes', [])
        if isinstance(profile_types, list):
            if 'broker' in profile_types:
                agent_type = AgentType.BROKER
            elif agent.is_team:  # Check existing is_team value
                agent_type = AgentType.TEAM
            elif 'agent' in profile_types:
                agent_type = AgentType.SOLO

        # Extract phone number - phoneNumbers is a dict with 'cell' and 'brokerage' keys
        phone = None
        phone_numbers = display_user.get('phoneNumbers', {})
        if isinstance(phone_numbers, dict):
            # Prefer cell phone, fallback to brokerage
            phone = phone_numbers.get('cell') or phone_numbers.get('brokerage')
        elif isinstance(phone_numbers, str):
            phone = phone_numbers

        # Extract email
        email = display_user.get('email')

        # Extract address from businessAddress
        address = None
        city = None
        state = None
        zip_code = None

        business_address = display_user.get('businessAddress', {})
        if business_address:
            address_parts = []
            if business_address.get('address1'):
                address_parts.append(business_address['address1'])
            if business_address.get('address2'):
                address_parts.append(business_address['address2'])
            address = ', '.join(address_parts) if address_parts else None

            city = business_address.get('city')
            state = business_address.get('state')
            zip_code = business_address.get('postalCode')

        # Extract additional profile details
        brokerage_name = display_user.get('businessName')

        # Get data from getToKnowMe section (this has most profile details)
        get_to_know_me = props.get('getToKnowMe', {})

        title = get_to_know_me.get('title') or display_user.get('title')
        biography = get_to_know_me.get('description')
        website = get_to_know_me.get('websiteUrl') or display_user.get('website')

        # Extract professional details from getToKnowMe
        specialties = get_to_know_me.get('specialties', [])
        if not isinstance(specialties, list):
            specialties = []

        # Languages and certifications - check professionalInformation
        languages = []
        certifications = []

        if isinstance(professional_info, list):
            for item in professional_info:
                if isinstance(item, dict):
                    term = item.get('term', '').lower()
                    lines = item.get('lines', [])

                    if lines:
                        if 'language' in term:
                            languages.extend(lines if isinstance(lines, list) else [lines])
                        elif 'certification' in term or 'designation' in term or 'license' in term:
                            # Include licenses as certifications
                            certifications.extend(lines if isinstance(lines, list) else [lines])

        # Extract years of experience - prefer getToKnowMe.yearsInIndustry
        years_experience = get_to_know_me.get('yearsInIndustry')

        # Fallback to calculating from licenses if not in getToKnowMe
        if not years_experience:
            agent_licenses = props.get('agentLicenses', [])
            if isinstance(agent_licenses, list) and agent_licenses:
                # Find oldest license year
                for license_info in agent_licenses:
                    if isinstance(license_info, dict):
                        year_obtained = license_info.get('yearObtained')
                        if year_obtained:
                            try:
                                year = int(year_obtained)
                                from datetime import datetime
                                experience = datetime.now().year - year
                                if years_experience is None or experience > years_experience:
                                    years_experience = experience
                            except (ValueError, TypeError):
                                pass

        # Extract brokerage phone
        brokerage_phone = None
        if isinstance(phone_numbers, dict):
            brokerage_phone = phone_numbers.get('brokerage')

        # Extract listings counts
        for_sale_listings_data = props.get('forSaleListings', {})
        for_rent_listings_data = props.get('forRentListings', {})

        if isinstance(for_sale_listings_data, dict):
            for_sale_count = for_sale_listings_data.get('listing_count', 0)
        else:
            for_sale_count = 0

        if isinstance(for_rent_listings_data, dict):
            for_rent_count = for_rent_listings_data.get('listing_count', 0)
        else:
            for_rent_count = 0

        active_listings = for_sale_count + for_rent_count
        total_listings = active_listings

        # Extract service areas (neighborhoods served)
        neighborhoods_served = []
        service_areas = props.get('serviceAreas', [])
        if isinstance(service_areas, list):
            for area in service_areas:
                if isinstance(area, dict):
                    # serviceAreas has 'text' field for area name
                    name = area.get('text') or area.get('name')
                    if name:
                        neighborhoods_served.append(name)
                elif isinstance(area, str):
                    neighborhoods_served.append(area)

        # Market expertise from service areas
        market_expertise = neighborhoods_served[:5] if neighborhoods_served else []

        # Extract brokerage address from professionalInformation
        brokerage_address = None
        if isinstance(professional_info, list):
            for item in professional_info:
                if isinstance(item, dict):
                    term = item.get('term', '').lower()
                    lines = item.get('lines', [])
                    if 'broker address' in term and lines:
                        # lines is like ['Pardee Properties', '1524 Abbot Kinney Blvd.', 'Venice, CA 90291']
                        brokerage_address = ', '.join(lines) if isinstance(lines, list) else lines

        # Update agent with profile data
        agent.phone = phone or agent.phone
        agent.email = email or agent.email
        agent.address = address or agent.address
        agent.city = city or agent.city
        agent.state = state or agent.state
        agent.zip_code = zip_code or agent.zip_code
        agent.title = title or agent.title
        agent.biography = biography or agent.biography
        agent.website = website or agent.website
        agent.brokerage_name = brokerage_name or agent.brokerage_name
        agent.agent_type = agent_type or agent.agent_type
        agent.specialties = specialties or agent.specialties
        agent.languages = languages or agent.languages
        agent.certifications = certifications or agent.certifications
        agent.years_experience = years_experience or agent.years_experience
        agent.brokerage_phone = brokerage_phone or agent.brokerage_phone
        agent.brokerage_address = brokerage_address or agent.brokerage_address
        agent.active_listings = active_listings if active_listings else agent.active_listings
        agent.for_sale_listings = for_sale_count if for_sale_count else agent.for_sale_listings
        agent.for_rent_listings = for_rent_count if for_rent_count else agent.for_rent_listings
        agent.total_listings = total_listings if total_listings else agent.total_listings
        agent.neighborhoods_served = neighborhoods_served or agent.neighborhoods_served
        agent.market_expertise = market_expertise or agent.market_expertise

        return agent

    except Exception as e:
        print(f"⚠️  Failed to parse profile for {agent.name}: {e}")
        # Return agent with whatever data we have
        return agent

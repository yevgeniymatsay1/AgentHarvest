"""
Data models for AgentHarvest - Zillow Agent Scraper
"""

from __future__ import annotations
from enum import Enum
from typing import Optional, List, Callable, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


# ============================================================================
# Enums
# ============================================================================

class ReturnType(Enum):
    """Output format for scraped data"""
    pandas = "pandas"
    pydantic = "pydantic"
    raw = "raw"


class AgentSpecialty(str, Enum):
    """Agent specialties"""
    BUYERS_AGENT = "buyers_agent"
    LISTING_AGENT = "listing_agent"
    RELOCATION = "relocation"
    FORECLOSURE = "foreclosure"
    SHORT_SALE = "short_sale"
    CONSULTING = "consulting"
    PROPERTY_MANAGEMENT = "property_management"
    LANDLORD = "landlord"


class TransactionType(str, Enum):
    """Transaction type for sales"""
    BUYER = "buyer"
    SELLER = "seller"
    BOTH = "both"


class TagType(str, Enum):
    """Tag types from Zillow"""
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    INFO = "INFO"


class AgentType(str, Enum):
    """Agent profile type"""
    SOLO = "solo"  # Individual agent
    TEAM = "team"  # Team of agents
    BROKER = "broker"  # Brokerage company


# ============================================================================
# Core Agent Models
# ============================================================================

class AgentTag(BaseModel):
    """Tag/badge on agent profile"""
    tag_type: Optional[str] = None
    text: Optional[str] = None


class ProfileData(BaseModel):
    """Structured profile data (sales, price range, etc.)"""
    label: str
    data: str


class ReviewInformation(BaseModel):
    """Review summary for an agent"""
    review_average: Optional[float] = Field(None, description="Average rating 0-5")
    review_average_text: Optional[str] = Field(None, description="Formatted rating text")
    review_count_text: Optional[str] = Field(None, description="Review count text like '(123)'")
    no_reviews_text: Optional[str] = Field(None, description="Text when no reviews")


class Review(BaseModel):
    """Individual review for an agent"""
    reviewer_name: Optional[str] = None
    rating: float
    date: Optional[datetime] = None
    text: Optional[str] = None
    transaction_type: Optional[str] = Field(None, description="Buyer, Seller, etc.")
    verified: Optional[bool] = Field(None, description="Whether review is verified")


class Sale(BaseModel):
    """Individual sale transaction"""
    address: Optional[str] = None
    sale_date: Optional[datetime] = None
    sale_price: Optional[int] = None
    property_type: Optional[str] = None
    transaction_type: Optional[str] = Field(None, description="Buyer's agent, Listing agent, etc.")
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None


class Agent(BaseModel):
    """
    Real estate agent model with comprehensive data

    Data is split into two tiers:
    1. Search Results Data: Available from agent directory search (fast)
    2. Profile Data: Requires fetching individual profile page (slower)
    """

    # ========================================================================
    # From Search Results (Always Available)
    # ========================================================================

    # Identifiers
    agent_id: str = Field(..., description="Zillow unique agent ID (encodedZuid)")
    profile_url: str = Field(..., description="Full URL to agent profile")

    # Basic Info
    name: str = Field(..., description="Agent full name")
    brokerage_name: Optional[str] = Field(None, description="Brokerage/company name")

    # Media
    photo_url: Optional[HttpUrl] = Field(None, description="Agent photo URL")
    logo_url: Optional[HttpUrl] = Field(None, description="Brokerage logo URL")

    # Status
    is_top_agent: bool = Field(False, description="Whether agent is flagged as 'Top Agent'")
    is_team: bool = Field(False, description="Whether this is a team vs individual")
    agent_type: Optional[AgentType] = Field(None, description="Type: solo, team, or broker")

    # Ratings & Reviews
    rating: Optional[float] = Field(None, description="Average rating 0-5")
    rating_text: Optional[str] = Field(None, description="Formatted rating like '5.0'")
    review_count: int = Field(0, description="Total number of reviews")

    # Sales Performance
    price_range: Optional[str] = Field(None, description="Price range like '$78K - $2.4M'")
    price_range_min: Optional[str] = Field(None, description="Minimum price from range")
    price_range_max: Optional[str] = Field(None, description="Maximum price from range")
    sales_last_12_months: Optional[int] = Field(None, description="Number of sales in last 12 months")
    total_sales: Optional[int] = Field(None, description="Total sales in current region")

    # Tags & Certifications
    tags: List[str] = Field(default_factory=list, description="Tags like 'TEAM', 'LICENSED 10+ YRS'")
    years_experience_min: Optional[int] = Field(None, description="Minimum years of experience from tags")

    # Structured data from search results
    profile_data: List[ProfileData] = Field(default_factory=list, description="Raw profile data items")
    review_information: Optional[ReviewInformation] = Field(None, description="Review summary")

    # ========================================================================
    # From Individual Profile Page (Optional - Requires Extra Fetch)
    # ========================================================================

    # Contact Info
    phone: Optional[str] = Field(None, description="Primary phone number")
    email: Optional[str] = Field(None, description="Email address")
    website: Optional[HttpUrl] = Field(None, description="Personal website")

    # Location
    address: Optional[str] = Field(None, description="Office street address")
    city: Optional[str] = Field(None, description="Office city")
    state: Optional[str] = Field(None, description="Office state")
    zip_code: Optional[str] = Field(None, description="Office ZIP code")

    # Professional Details
    title: Optional[str] = Field(None, description="Professional title like 'Real Estate Agent', 'Broker'")
    years_experience: Optional[int] = Field(None, description="Exact years of experience")
    specialties: List[str] = Field(default_factory=list, description="Agent specialties")
    languages: List[str] = Field(default_factory=list, description="Languages spoken")
    certifications: List[str] = Field(default_factory=list, description="Professional certifications")
    licenses: List[str] = Field(default_factory=list, description="License numbers")
    biography: Optional[str] = Field(None, description="Agent bio text")

    # Brokerage Details
    brokerage_phone: Optional[str] = Field(None, description="Brokerage phone number")
    brokerage_address: Optional[str] = Field(None, description="Brokerage address")

    # Detailed Performance
    recent_sales: List[Sale] = Field(default_factory=list, description="Recent sales transactions")
    reviews: List[Review] = Field(default_factory=list, description="Individual reviews")
    neighborhoods_served: List[str] = Field(default_factory=list, description="Neighborhoods served")
    market_expertise: List[str] = Field(default_factory=list, description="Geographic market areas")

    # Listings
    active_listings: Optional[int] = Field(None, description="Number of active listings")
    for_sale_listings: Optional[int] = Field(None, description="Number of for-sale listings")
    for_rent_listings: Optional[int] = Field(None, description="Number of for-rent listings")
    total_listings: Optional[int] = Field(None, description="Total number of listings")

    class Config:
        use_enum_values = True


# ============================================================================
# Search Input Model
# ============================================================================

class SearchInput(BaseModel):
    """
    Input parameters for agent search
    """

    # Location (at least one required)
    state: Optional[str] = Field(None, description="State name or abbreviation (e.g., 'CA', 'California')")
    city: Optional[str] = Field(None, description="City name (e.g., 'San Diego')")
    zip_code: Optional[str] = Field(None, description="ZIP code (e.g., '92101')")
    location_slug: Optional[str] = Field(None, description="Pre-formatted location slug (e.g., 'san-diego-ca')")

    # Filters (client-side filtering)
    rating_min: Optional[float] = Field(None, ge=0, le=5, description="Minimum rating 0-5")
    review_count_min: Optional[int] = Field(None, ge=0, description="Minimum number of reviews")
    sales_min: Optional[int] = Field(None, ge=0, description="Minimum sales last 12 months")
    sales_max: Optional[int] = Field(None, ge=0, description="Maximum sales last 12 months")
    years_experience_min: Optional[int] = Field(None, ge=0, description="Minimum years of experience")
    specialties: Optional[List[str]] = Field(None, description="Filter by specialties")
    languages: Optional[List[str]] = Field(None, description="Filter by languages")
    is_top_agent: Optional[bool] = Field(None, description="Filter for top agents only")
    exclude_teams: bool = Field(False, description="Exclude team listings")
    agent_type: Optional[AgentType] = Field(None, description="Filter by agent type (solo, team, or broker)")

    # Control
    limit: int = Field(100, ge=1, le=1000, description="Maximum results to return")
    offset: int = Field(0, ge=0, description="Starting position for pagination")
    fetch_profiles: bool = Field(False, description="Fetch comprehensive data from individual profiles (slower)")

    # Technical
    proxy: Optional[str] = Field(None, description="Proxy in format 'http://user:pass@host:port'")
    timeout: int = Field(30, ge=1, le=300, description="Request timeout in seconds")
    # Note: delay_between_requests removed - now uses automatic intelligent batching with random delays (15-60s)

    # Progress tracking
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = Field(None, description="Callback function for progress updates")

    # Output
    return_type: ReturnType = Field(ReturnType.pandas, description="Output format")

    def validate_location(self) -> bool:
        """Ensure at least one location parameter is provided"""
        return any([self.state, self.city, self.zip_code, self.location_slug])

    def get_location_slug(self) -> str:
        """Generate location slug for URL"""
        if self.location_slug:
            return self.location_slug

        parts = []
        if self.city:
            parts.append(self.city.lower().replace(' ', '-'))
        if self.state:
            # Handle both full state names and abbreviations
            state_normalized = self.state.lower().replace(' ', '-')
            parts.append(state_normalized)

        if parts:
            return '-'.join(parts)

        if self.zip_code:
            return self.zip_code

        return ""

    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True  # Allow callable types

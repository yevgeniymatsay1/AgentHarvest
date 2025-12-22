import json
import random
from typing import Any, Dict, Iterable, List, Optional, Set

import scrapy
from scrapy.http import Request
from scrapy_playwright.page import PageMethod


def _get(obj: Dict[str, Any], path: List[str], default=None):
    current = obj
    for key in path:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return current


def _walk_urls(value: Any, accumulator: Set[str]) -> None:
    if isinstance(value, dict):
        for child in value.values():
            _walk_urls(child, accumulator)
    elif isinstance(value, list):
        for child in value:
            _walk_urls(child, accumulator)
    elif isinstance(value, str) and "/realestateagents/" in value:
        accumulator.add(value)


def _intercept_resource(route, request):
    if request.resource_type in {"image", "media", "stylesheet", "font"}:
        return route.abort()
    return route.continue_()


class AgentsSpider(scrapy.Spider):
    name = "agents"
    allowed_domains = ["realtor.com"]

    def __init__(self, state: str = "new-york", city: str = "ny", intent: Optional[str] = None, start_url: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.state = state.strip().replace(" ", "-").lower()
        self.city = city.strip().replace(" ", "-").lower()
        self.intent = intent.strip().lower() if intent else None
        self.custom_start_url = start_url
        self.location_slug = f"{self.city}_{self.state}".strip("_")

    async def start(self):
        async for req in self._iter_start_requests():
            yield req

    def start_requests(self):
        if self.custom_start_url:
            yield Request(
                url=self.custom_start_url,
                meta=self.playwright_meta(),
                callback=self.parse,
            )
            return

        yield Request(
            url=self.directory_url(1),
            meta=self.playwright_meta(),
            callback=self.parse,
        )

    async def _iter_start_requests(self):
        for req in self.start_requests():
            yield req

    def directory_url(self, page: int = 1) -> str:
        base = f"https://www.realtor.com/realestateagents/{self.location_slug}"
        if self.intent:
            base = f"{base}/intent-{self.intent}"
        if page > 1:
            base = f"{base}/pg-{page}"
        return f"{base}"

    def parse(self, response):
        profile_links = self.extract_profile_links(response)
        for href in profile_links:
            yield response.follow(href, callback=self.parse_agent, dont_filter=True, meta=self.playwright_meta())

        next_page = self.get_next_page(response)
        if next_page:
            yield response.follow(next_page, callback=self.parse, dont_filter=True, meta=self.playwright_meta())

    def extract_profile_links(self, response) -> Iterable[str]:
        links: Set[str] = set()
        for href in response.css('a[href*="/realestateagents/"]::attr(href)').getall():
            links.add(response.urljoin(href))

        next_data = self.load_next_data(response)
        if next_data:
            url_candidates: Set[str] = set()
            _walk_urls(next_data, url_candidates)
            for href in url_candidates:
                if "/realestateagents/" in href:
                    links.add(response.urljoin(href))

        return links

    def get_next_page(self, response) -> Optional[str]:
        link = response.css('a[aria-label="Next"]::attr(href), link[rel="next"]::attr(href)').get()
        if link:
            return response.urljoin(link)

        next_data = self.load_next_data(response)
        pagination = _get(
            next_data or {},
            ["props", "pageProps", "searchPageProps", "searchResultsProps", "pagination"],
            {},
        )
        if isinstance(pagination, dict):
            next_url = pagination.get("nextUrl") or pagination.get("next")
            if next_url:
                return response.urljoin(next_url)
        return None

    def parse_agent(self, response):
        next_data = self.load_next_data(response) or {}
        agent_data = _get(next_data, ["props", "pageProps", "agentDetailPageProps"], {}) or {}

        ld_json_data = self.load_ld_json(response)

        phones = self.extract_phone_numbers(agent_data, ld_json_data)
        listing_stats = agent_data.get("listing_stats", {}) or {}
        for_sale = listing_stats.get("for_sale", {}) or {}
        recently_sold = listing_stats.get("recently_sold", {}) or {}
        combined_annual = listing_stats.get("combined_annual", {}) or {}

        areas = agent_data.get("areas_served") or agent_data.get("served_areas") or []
        served_areas = [a.get("name") if isinstance(a, dict) else a for a in areas]

        specializations = agent_data.get("specializations") or []
        if isinstance(specializations, dict):
            specializations = specializations.values()

        brokerage = None
        broker_info = agent_data.get("broker") or {}
        if isinstance(broker_info, dict):
            brokerage = broker_info.get("name")

        rating = agent_data.get("average_rating") or agent_data.get("rating")
        reviews_count = agent_data.get("reviews_count") or agent_data.get("rating_count")

        item = {
            "agent_id": agent_data.get("agent_id") or agent_data.get("id"),
            "name": agent_data.get("fullname") or agent_data.get("name"),
            "brokerage": brokerage,
            "phone_numbers": phones,
            "rating": rating,
            "reviews_count": reviews_count,
            "listed_properties_count": for_sale.get("count"),
            "sold_properties_count": recently_sold.get("count"),
            "min_listing_price": combined_annual.get("min"),
            "max_listing_price": combined_annual.get("max"),
            "served_areas": [a for a in served_areas if a],
            "specializations": [s for s in specializations if s],
            "license_number": agent_data.get("license_number") or agent_data.get("license"),
            "profile_url": response.url,
        }

        schema_profile = ld_json_data.get("profile") or ld_json_data.get("url")
        if schema_profile and not item.get("profile_url"):
            item["profile_url"] = response.urljoin(schema_profile)

        if not item["name"] and not item["agent_id"]:
            self.logger.debug("Skipping page without agent data: %s", response.url)
            return

        yield item

    def playwright_meta(self) -> Dict[str, Any]:
        user_agent = random.choice(self.settings.getlist("USER_AGENT_LIST")) if self.settings.getlist("USER_AGENT_LIST") else None
        return {
            "playwright": True,
            "playwright_page_methods": [
                PageMethod("wait_for_timeout", 1000),
                PageMethod("route", "**/*", _intercept_resource),
            ],
            "playwright_context_kwargs": {
                "user_agent": user_agent or self.settings.get("USER_AGENT"),
            },
        }

    def extract_phone_numbers(self, agent_data: Dict[str, Any], ld_json_data: Dict[str, Any]) -> List[str]:
        numbers: Set[str] = set()
        for phone in agent_data.get("phones", []) or []:
            if isinstance(phone, dict):
                number = phone.get("number") or phone.get("phone") or phone.get("value")
                if number:
                    numbers.add(number)
            elif isinstance(phone, str):
                numbers.add(phone)

        schema_numbers = ld_json_data.get("telephone")
        if isinstance(schema_numbers, list):
            numbers.update(schema_numbers)
        elif isinstance(schema_numbers, str):
            numbers.add(schema_numbers)

        return list(numbers)

    def load_ld_json(self, response) -> Dict[str, Any]:
        for script in response.css('script[type="application/ld+json"]::text').getall():
            try:
                data = json.loads(script)
                if isinstance(data, list):
                    for entry in data:
                        if isinstance(entry, dict) and entry.get("@type") == "RealEstateAgent":
                            return entry
                elif isinstance(data, dict) and data.get("@type") == "RealEstateAgent":
                    return data
            except json.JSONDecodeError:
                continue
        return {}

    def load_next_data(self, response) -> Optional[Dict[str, Any]]:
        script = response.css('script#__NEXT_DATA__::text').get()
        if not script:
            return None
        try:
            return json.loads(script)
        except json.JSONDecodeError:
            return None

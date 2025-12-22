# Realtor.com Agent Scraper (Scrapy)

This repository now hosts a Scrapy project for crawling Realtor.com real estate agent profiles and exporting structured agent data.

## Project layout

```
realtor_scraper/
├── scrapy.cfg
└── realtor_scraper/
    ├── settings.py
    └── spiders/
        └── agents_spider.py
```

## Installation

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt  # or `pip install poetry && poetry install`
# Install the Playwright browser binary (one-time)
python -m playwright install chromium
```

If you are not using Poetry, you can install directly from `pyproject.toml` with `pip install scrapy`.

## Running the spider

From the repository root:

```bash
cd realtor_scraper
scrapy crawl agents -o new_york_agents.json -a state=new-york -a city=ny
```

### Spider arguments
- `state` (default: `new-york`): State slug used in the Realtor.com directory URL. Spaces are converted to dashes automatically.
- `city` (default: `ny`): City slug used in the directory URL.
- `intent` (optional): Append an intent segment such as `buy` to crawl URLs like `.../intent-buy`.
- `start_url` (optional): Use a fully qualified start URL (e.g., `https://www.realtor.com/realestateagents/new-york_ny/intent-buy`). When provided, `state`/`city` are ignored for the first page; pagination still follows in-site links.

The spider builds URLs like `https://www.realtor.com/realestateagents/<city>_<state>/pg-<page>`. Update `city` and `state` to target different locations (e.g., `-a state=texas -a city=austin`).

### Output

Each item emitted by the spider includes (when available):

```json
{
  "agent_id": "...",
  "name": "Full Name",
  "brokerage": "Brokerage Name",
  "phone_numbers": ["..."],
  "rating": 4.8,
  "reviews_count": 25,
  "listed_properties_count": 12,
  "sold_properties_count": 30,
  "min_listing_price": 350000,
  "max_listing_price": 2200000,
  "served_areas": ["New York, NY", "Brooklyn, NY"],
  "specializations": ["BuyerAgent", "ListingAgent"],
  "license_number": "XXXXXX",
  "profile_url": "https://www.realtor.com/realestateagents/..."
}
```

### Pagination and data extraction

- The spider paginates through directory result pages by following “Next” links or pagination URLs exposed in `__NEXT_DATA__` JSON.
- Agent profile pages are parsed by loading the `__NEXT_DATA__` script payload (which contains `props.pageProps.agentDetailPageProps`) and any Schema.org `application/ld+json` data present on the page.
- All HTTP requests are executed via a headless Playwright-driven browser (Scrapy Playwright handler) with non-essential assets (images, media, fonts, stylesheets) blocked to reduce load and noise. This mimics real browser traffic instead of direct cURL-style requests.

### Respectful crawling

The project enables download delays, auto-throttling, and user-agent rotation (see `realtor_scraper/settings.py`) to reduce the chance of being blocked. Update these values as needed for your environment and legal/ethical requirements. Robots.txt compliance is disabled by default (`ROBOTSTXT_OBEY = False`); change this to `True` if required for your use case.

## Troubleshooting

- Realtor.com may present bot-protection or block anonymous requests. If you receive HTML error pages or 403 responses, consider slower crawl rates, additional user-agent strings, or running behind an allowed proxy.
- Inspect saved HTML responses with `scrapy shell <url>` to adjust selectors if Realtor.com changes their markup.

## Further testing

You can add unit tests for parsing helpers (e.g., validating `__NEXT_DATA__` parsing) by creating fixtures under `realtor_scraper/tests/` and invoking them with `pytest`.

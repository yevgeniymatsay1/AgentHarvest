"""
Zillow Agent Scraper - Main implementation
"""

import time
import random
from datetime import datetime
from typing import List, Tuple, Dict
from ..models import Agent, SearchInput
from .browser import HTTPClient
from .queries import build_agent_search_url
from .parsers import parse_agents_from_html, extract_next_data, get_search_metadata, parse_agent_profile
from .processors import apply_filters, deduplicate_agents, sort_agents, limit_results


class ZillowScraper:
    """
    Main scraper class for Zillow agent directory

    Handles:
    - HTTP requests with curl_cffi (browser impersonation)
    - HTML fetching and parsing
    - Data extraction from __NEXT_DATA__
    - Client-side filtering
    - Result pagination
    """

    def __init__(self, search_input: SearchInput):
        """
        Initialize scraper with search parameters

        Args:
            search_input: Search parameters and filters
        """
        self.search_input = search_input
        self.client: HTTPClient = None

    def search_agents(self) -> List[Agent]:
        """
        Main entry point: Search for agents on Zillow

        Returns:
            List of Agent objects matching search criteria

        Raises:
            Exception: If search fails
        """
        # Validate location
        if not self.search_input.validate_location():
            raise ValueError("Must provide at least one location parameter: state, city, or zip_code")

        print("=" * 80)
        print("ZILLOW AGENT SEARCH")
        print("=" * 80)

        all_agents = []

        try:
            # Initialize HTTP client
            self.client = HTTPClient(
                timeout=self.search_input.timeout,
                proxy=self.search_input.proxy
            )

            # Pagination: Keep fetching pages until we have enough agents
            page = 1
            max_pages = 100  # Safety limit to prevent infinite loops

            print(f"\n🔄 Pagination enabled - fetching up to {self.search_input.limit} agents")
            print(f"   Will fetch multiple pages as needed\n")

            while len(all_agents) < self.search_input.limit and page <= max_pages:
                print(f"\n{'='*60}")
                print(f"📄 FETCHING PAGE {page}")
                print(f"{'='*60}")

                # Fetch agents from this page
                agents, metadata = self._fetch_agents_page(page)

                if not agents:
                    print(f"\n⚠️  No agents found on page {page}. Stopping pagination.")
                    break

                all_agents.extend(agents)
                print(f"\n📊 Progress: {len(all_agents)} agents collected so far")

                # Check if we have enough agents
                if len(all_agents) >= self.search_input.limit:
                    print(f"✅ Reached target of {self.search_input.limit} agents!")
                    break

                # Check if there are more pages available
                total_available = metadata.get('total_results', 0)
                if len(all_agents) >= total_available:
                    print(f"\n✅ Fetched all available agents ({total_available})")
                    break

                # Delay before next page (shorter than profile fetching)
                # Use 3-8 seconds between page requests to avoid detection
                if page < max_pages and len(all_agents) < self.search_input.limit:
                    delay = random.uniform(3, 8)
                    print(f"\n⏱️  Waiting {delay:.1f}s before next page...")
                    time.sleep(delay)

                page += 1

            print(f"\n📊 Total agents collected from {page} page(s): {len(all_agents)}")

            # If agent_type filter is specified, we need to fetch profiles first
            # because agent_type is only available from profile pages
            if self.search_input.agent_type is not None:
                if not self.search_input.fetch_profiles:
                    print(f"\n⚠️  agent_type filter requires fetch_profiles=True")
                    print(f"   Automatically enabling profile fetching...")
                    self.search_input.fetch_profiles = True

            # Apply filters (except agent_type if we need to fetch profiles first)
            print(f"\n🔍 Applying filters...")

            # Save agent_type filter temporarily if profiles need to be fetched
            saved_agent_type = None
            if self.search_input.fetch_profiles and self.search_input.agent_type is not None:
                saved_agent_type = self.search_input.agent_type
                self.search_input.agent_type = None  # Temporarily disable

            filtered_agents = apply_filters(all_agents, self.search_input)
            print(f"   After filters: {len(filtered_agents)} agents")

            # Deduplicate
            unique_agents = deduplicate_agents(filtered_agents)
            if len(unique_agents) < len(filtered_agents):
                print(f"   Removed {len(filtered_agents) - len(unique_agents)} duplicates")

            # Sort by rating (default)
            sorted_agents = sort_agents(unique_agents, sort_by='rating', descending=True)

            # Apply limit (with extra buffer if we'll filter by agent_type later)
            limit_to_fetch = self.search_input.limit
            if saved_agent_type is not None:
                # Fetch more agents since we'll filter by agent_type after profiles
                limit_to_fetch = min(self.search_input.limit * 3, len(sorted_agents))

            final_agents = limit_results(
                sorted_agents,
                limit=limit_to_fetch,
                offset=self.search_input.offset
            )

            # Fetch comprehensive profiles if requested
            if self.search_input.fetch_profiles:
                print(f"\n📞 Fetching comprehensive profiles (phone/email)...")
                print(f"   This will make {len(final_agents)} additional requests (slower)")
                final_agents = self._fetch_all_profiles(final_agents)

            # Apply agent_type filter after profiles are fetched
            if saved_agent_type is not None:
                self.search_input.agent_type = saved_agent_type  # Restore filter
                print(f"\n🔍 Applying agent_type filter: {saved_agent_type.value}")
                before_count = len(final_agents)
                final_agents = [a for a in final_agents if a.agent_type == saved_agent_type]
                print(f"   Filtered from {before_count} to {len(final_agents)} agents")

                # Apply limit again after agent_type filtering
                final_agents = final_agents[:self.search_input.limit]

            print(f"\n✅ Returning {len(final_agents)} agents")
            print("=" * 80)

            return final_agents

        except Exception as e:
            print(f"\n❌ Search failed: {e}")
            raise

        finally:
            # Clean up client
            if self.client:
                self.client.close()

    def _fetch_agents_page(self, page: int = 1) -> Tuple[List[Agent], Dict]:
        """
        Fetch agents from a single page

        Args:
            page: Page number to fetch (default: 1)

        Returns:
            Tuple of (agents list, metadata dict)
        """
        # Build URL with page number
        url = build_agent_search_url(self.search_input, page)

        print(f"\n🔍 Location: {self.search_input.get_location_slug()}")
        print(f"🌐 URL: {url}")

        # Fetch page HTML
        html = self.client.get_page_html(url)

        # Parse agents from HTML
        print(f"\n📝 Parsing agent data...")
        agents = parse_agents_from_html(html)

        # Get metadata
        metadata = {}
        try:
            next_data = extract_next_data(html)
            metadata = get_search_metadata(next_data)

            print(f"\n📈 Page {page} Results:")
            print(f"   Total available: {metadata['total_results']:,}")
            print(f"   Loaded on this page: {metadata['results_on_page']}")
            print(f"   Location: {metadata['location']}")
        except Exception as e:
            print(f"⚠️  Could not extract metadata: {e}")
            metadata = {'total_results': 0, 'current_page': page, 'results_on_page': len(agents)}

        print(f"\n✅ Parsed {len(agents)} agents from page {page}")

        return agents, metadata

    def _fetch_all_profiles(self, agents: List[Agent]) -> List[Agent]:
        """
        Fetch comprehensive data for all agents from their profile pages

        Uses intelligent batching with random delays to avoid detection:
        - Random delays between 15-60 seconds per request
        - Random batch sizes (5-15 agents)
        - Random break times (20-40 minutes) between batches
        - Random order (not sequential) - looks more human
        - No detectable patterns

        Args:
            agents: List of Agent objects with basic data

        Returns:
            List of Agent objects with enhanced profile data (in original order)
        """
        # CRITICAL: Shuffle agents to fetch in random order
        # Don't go 1→2→3→4... but rather 3→7→1→5→2...
        # This looks like a human browsing randomly, not a bot going sequentially
        agents_shuffled = agents.copy()
        random.shuffle(agents_shuffled)

        enhanced_agents_dict = {}  # Track by agent_id to restore original order
        total = len(agents_shuffled)

        # Configuration for randomness
        DELAY_MIN = 15  # Minimum seconds between requests
        DELAY_MAX = 60  # Maximum seconds between requests
        BATCH_MIN = 5   # Minimum agents per batch
        BATCH_MAX = 15  # Maximum agents per batch
        BREAK_MIN = 10  # Minimum minutes between batches (reduced from 20)
        BREAK_MAX = 20  # Maximum minutes between batches (reduced from 40)

        print(f"\n🤖 SMART BATCH PROCESSING (Anti-Detection)")
        print(f"   🎲 Randomized order: Yes (not sequential)")
        print(f"   Delays: {DELAY_MIN}-{DELAY_MAX}s (random)")
        print(f"   Batch sizes: {BATCH_MIN}-{BATCH_MAX} agents (random)")
        print(f"   Breaks: {BREAK_MIN}-{BREAK_MAX} min (random)")
        print(f"   Total to fetch: {total} agents")

        # Calculate estimated time
        avg_delay = (DELAY_MIN + DELAY_MAX) / 2
        avg_batch = (BATCH_MIN + BATCH_MAX) / 2
        avg_break = (BREAK_MIN + BREAK_MAX) / 2
        num_batches = (total // avg_batch) + (1 if total % avg_batch else 0)
        estimated_minutes = (total * avg_delay / 60) + ((num_batches - 1) * avg_break)
        print(f"   ⏱️  Estimated time: {estimated_minutes:.0f} minutes ({estimated_minutes/60:.1f} hours)")
        print()

        # Send initial progress
        if self.search_input.progress_callback:
            self.search_input.progress_callback({
                'stage': 'profile_fetch_start',
                'total': total,
                'estimated_minutes': estimated_minutes
            })

        i = 0
        batch_num = 1

        while i < total:
            # Determine random batch size
            remaining = total - i
            # Ensure min batch size doesn't exceed remaining (for small quantities)
            batch_min = min(BATCH_MIN, remaining)
            batch_max = min(BATCH_MAX, remaining)
            batch_size = random.randint(batch_min, batch_max)

            print(f"\n📦 BATCH {batch_num} (agents {i+1}-{i+batch_size} of {total})")
            print(f"   Batch size: {batch_size} agents")
            print(f"   Started at: {datetime.now().strftime('%H:%M:%S')}")

            # Send batch start progress
            if self.search_input.progress_callback:
                self.search_input.progress_callback({
                    'stage': 'batch_start',
                    'batch_num': batch_num,
                    'batch_size': batch_size,
                    'current': i,
                    'total': total
                })

            # Process this batch
            for j in range(batch_size):
                if i >= total:
                    break

                agent = agents_shuffled[i]  # Use shuffled list
                print(f"   [{i+1}/{total}] Fetching: {agent.name}")

                # Send agent fetch progress
                if self.search_input.progress_callback:
                    self.search_input.progress_callback({
                        'stage': 'fetching_agent',
                        'agent_name': agent.name,
                        'current': i + 1,
                        'total': total,
                        'batch_num': batch_num
                    })

                try:
                    enhanced_agent = self._fetch_agent_profile(agent)
                    enhanced_agents_dict[agent.agent_id] = enhanced_agent
                    print(f"      ✅ Success")

                except Exception as e:
                    print(f"      ⚠️  Failed: {e}")
                    # Keep agent with basic data if profile fetch fails
                    enhanced_agents_dict[agent.agent_id] = agent

                i += 1

                # Random delay before next request (unless last one)
                if i < total:
                    delay = random.uniform(DELAY_MIN, DELAY_MAX)
                    print(f"      ⏱️  Random delay: {delay:.1f}s")

                    # Send delay progress
                    if self.search_input.progress_callback:
                        self.search_input.progress_callback({
                            'stage': 'delay',
                            'delay_seconds': delay,
                            'current': i,
                            'total': total
                        })

                    time.sleep(delay)

            # Stats for this batch
            with_phone = sum(1 for a in enhanced_agents_dict.values() if a.phone)
            with_email = sum(1 for a in enhanced_agents_dict.values() if a.email)
            print(f"\n   ✅ Batch {batch_num} complete")
            print(f"      Total fetched so far: {len(enhanced_agents_dict)}/{total}")
            print(f"      With phone: {with_phone}/{len(enhanced_agents_dict)}")
            print(f"      With email: {with_email}/{len(enhanced_agents_dict)}")

            # Random break before next batch (unless this was the last batch)
            if i < total:
                break_minutes = random.uniform(BREAK_MIN, BREAK_MAX)
                break_seconds = break_minutes * 60
                resume_time = datetime.fromtimestamp(time.time() + break_seconds)

                print(f"\n   ⏸️  RANDOM BREAK: {break_minutes:.1f} minutes")
                print(f"      Resuming at: {resume_time.strftime('%H:%M:%S')}")
                print(f"      Remaining: {total - i} agents")
                print(f"      Progress: {(i/total)*100:.1f}%")

                # Send break start progress
                if self.search_input.progress_callback:
                    self.search_input.progress_callback({
                        'stage': 'break_start',
                        'break_minutes': break_minutes,
                        'break_seconds': break_seconds,
                        'resume_time': resume_time.strftime('%H:%M:%S'),
                        'current': i,
                        'total': total,
                        'progress_percent': (i/total)*100,
                        'batch_num': batch_num
                    })

                # Sleep in smaller chunks to allow for progress updates
                chunk_size = 10  # Update every 10 seconds
                remaining_seconds = break_seconds
                while remaining_seconds > 0:
                    sleep_time = min(chunk_size, remaining_seconds)
                    time.sleep(sleep_time)
                    remaining_seconds -= sleep_time

                    # Send break progress update
                    if remaining_seconds > 0 and self.search_input.progress_callback:
                        self.search_input.progress_callback({
                            'stage': 'break_progress',
                            'break_minutes': break_minutes,
                            'remaining_seconds': remaining_seconds,
                            'elapsed_seconds': break_seconds - remaining_seconds,
                            'resume_time': resume_time.strftime('%H:%M:%S'),
                            'current': i,
                            'total': total,
                            'batch_num': batch_num
                        })

                batch_num += 1

        print(f"\n{'='*80}")
        print(f"✅ ALL PROFILES COMPLETE")
        print(f"{'='*80}")
        print(f"   Total profiles fetched: {len(enhanced_agents_dict)}")
        print(f"   With phone: {sum(1 for a in enhanced_agents_dict.values() if a.phone)}/{len(enhanced_agents_dict)}")
        print(f"   With email: {sum(1 for a in enhanced_agents_dict.values() if a.email)}/{len(enhanced_agents_dict)}")
        print(f"{'='*80}\n")

        # Send completion progress
        if self.search_input.progress_callback:
            self.search_input.progress_callback({
                'stage': 'complete',
                'total': len(enhanced_agents_dict),
                'with_phone': sum(1 for a in enhanced_agents_dict.values() if a.phone),
                'with_email': sum(1 for a in enhanced_agents_dict.values() if a.email)
            })

        # Restore original order (important for consistent output)
        enhanced_agents = [enhanced_agents_dict[agent.agent_id] for agent in agents]

        return enhanced_agents

    def _fetch_agent_profile(self, agent: Agent) -> Agent:
        """
        Fetch comprehensive data from individual agent profile page

        Args:
            agent: Agent object with basic data from search

        Returns:
            Agent object with enhanced profile data (phone, email, etc.)

        Raises:
            Exception: If profile fetching fails
        """
        # Profile URL is already in the agent data
        if not agent.profile_url:
            raise Exception(f"No profile URL for agent: {agent.name}")

        # Build full URL if needed
        profile_url = agent.profile_url
        if not profile_url.startswith('http'):
            profile_url = f"https://www.zillow.com{profile_url}"

        # Fetch profile page HTML
        html = self.client.get_page_html(profile_url)

        # Parse profile data and enhance agent
        enhanced_agent = parse_agent_profile(html, agent)

        return enhanced_agent

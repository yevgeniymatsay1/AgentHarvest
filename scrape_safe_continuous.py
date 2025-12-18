"""
PRODUCTION-SAFE Continuous Scraper
For running 24/7 without IP restrictions

Key features:
- Very slow but steady (10-15 agents/hour)
- Random delays to look human
- Automatic breaks between sessions
- Saves progress continuously
- Can resume from interruption
"""

import time
import random
import pandas as pd
from datetime import datetime
from agentharvest import scrape_agent
import os
import json

class SafeContinuousScraper:
    def __init__(self,
                 delay_min=10,      # Minimum delay between requests (seconds)
                 delay_max=20,      # Maximum delay between requests (seconds)
                 batch_size=10,     # Agents per batch
                 batch_break=1800,  # Break between batches (30 minutes)
                 output_dir="./scraped_data"):

        self.delay_min = delay_min
        self.delay_max = delay_max
        self.batch_size = batch_size
        self.batch_break = batch_break
        self.output_dir = output_dir

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Load or create checkpoint
        self.checkpoint_file = os.path.join(output_dir, "checkpoint.json")
        self.checkpoint = self.load_checkpoint()

    def load_checkpoint(self):
        """Load checkpoint to resume from interruption"""
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {
            'total_scraped': 0,
            'last_state': None,
            'last_offset': 0,
            'session_number': 0
        }

    def save_checkpoint(self):
        """Save checkpoint after each batch"""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f, indent=2)

    def get_random_delay(self):
        """Random delay to look more human"""
        return random.uniform(self.delay_min, self.delay_max)

    def scrape_batch(self, state, offset=0):
        """Scrape one batch with production-safe settings"""

        print(f"\n{'='*80}")
        print(f"📦 BATCH {self.checkpoint['session_number'] + 1}")
        print(f"{'='*80}")
        print(f"State: {state}")
        print(f"Offset: {offset}")
        print(f"Batch size: {self.batch_size}")
        print(f"Delay range: {self.delay_min}-{self.delay_max}s per agent")
        print(f"Estimated time: {(self.batch_size * ((self.delay_min + self.delay_max) / 2)) / 60:.1f} minutes")
        print(f"{'='*80}\n")

        try:
            # Use random delay for this batch
            batch_delay = self.get_random_delay()

            agents = scrape_agent(
                state=state,
                limit=self.batch_size,
                offset=offset,
                fetch_profiles=True,
                delay_between_requests=batch_delay,  # Random delay
            )

            if len(agents) > 0:
                # Save this batch immediately
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"agents_{state.lower().replace(' ', '_')}_batch{self.checkpoint['session_number'] + 1}_{timestamp}.csv"
                filepath = os.path.join(self.output_dir, filename)
                agents.to_csv(filepath, index=False)

                print(f"\n✅ Batch complete: {len(agents)} agents saved to {filename}")

                # Update checkpoint
                self.checkpoint['total_scraped'] += len(agents)
                self.checkpoint['last_state'] = state
                self.checkpoint['last_offset'] = offset + self.batch_size
                self.checkpoint['session_number'] += 1
                self.save_checkpoint()

                return len(agents)
            else:
                print("\n⚠️  No more agents found")
                return 0

        except Exception as e:
            print(f"\n❌ Batch failed: {e}")
            return 0

    def run_continuous(self, states, agents_per_state=100):
        """
        Run continuous scraping across multiple states

        Args:
            states: List of states to scrape (e.g., ['California', 'Texas', 'Florida'])
            agents_per_state: Total agents to get per state
        """

        print(f"\n{'='*80}")
        print(f"🚀 STARTING CONTINUOUS SCRAPER")
        print(f"{'='*80}")
        print(f"States: {', '.join(states)}")
        print(f"Target per state: {agents_per_state} agents")
        print(f"Batch size: {self.batch_size}")
        print(f"Delay per agent: {self.delay_min}-{self.delay_max}s")
        print(f"Break between batches: {self.batch_break / 60:.0f} minutes")
        print(f"Estimated rate: {(3600 / ((self.delay_min + self.delay_max) / 2)):.0f} agents/hour")
        print(f"Output directory: {self.output_dir}")
        print(f"\n💾 Progress will be saved after each batch")
        print(f"📊 You can stop (Ctrl+C) and resume anytime")
        print(f"{'='*80}\n")

        input("Press Enter to start scraping (Ctrl+C to cancel)...")

        try:
            for state in states:
                print(f"\n{'='*80}")
                print(f"🗺️  STATE: {state.upper()}")
                print(f"{'='*80}\n")

                offset = 0
                total_for_state = 0

                while total_for_state < agents_per_state:
                    # Scrape one batch
                    scraped = self.scrape_batch(state, offset)

                    if scraped == 0:
                        print(f"\n✅ Finished {state} - no more agents available")
                        break

                    total_for_state += scraped
                    offset += self.batch_size

                    print(f"\n📊 Progress for {state}: {total_for_state}/{agents_per_state}")
                    print(f"📈 Total scraped across all states: {self.checkpoint['total_scraped']}")

                    # Check if we've hit target for this state
                    if total_for_state >= agents_per_state:
                        print(f"\n✅ Target reached for {state}!")
                        break

                    # Take a break between batches
                    print(f"\n⏸️  Taking {self.batch_break / 60:.0f} minute break...")
                    print(f"   (This prevents rate limiting)")
                    print(f"   Next batch starts at: {datetime.fromtimestamp(time.time() + self.batch_break).strftime('%H:%M:%S')}")
                    time.sleep(self.batch_break)

            # Done!
            print(f"\n{'='*80}")
            print(f"🎉 SCRAPING COMPLETE!")
            print(f"{'='*80}")
            print(f"Total agents scraped: {self.checkpoint['total_scraped']}")
            print(f"Output directory: {self.output_dir}")
            print(f"{'='*80}\n")

            # Merge all CSVs
            self.merge_results()

        except KeyboardInterrupt:
            print(f"\n\n{'='*80}")
            print(f"⏸️  PAUSED")
            print(f"{'='*80}")
            print(f"Progress saved!")
            print(f"Total scraped so far: {self.checkpoint['total_scraped']}")
            print(f"Last state: {self.checkpoint['last_state']}")
            print(f"Last offset: {self.checkpoint['last_offset']}")
            print(f"\nTo resume, run this script again - it will continue from where you left off!")
            print(f"{'='*80}\n")

    def merge_results(self):
        """Merge all batch CSVs into one master file"""
        csv_files = [f for f in os.listdir(self.output_dir) if f.endswith('.csv')]

        if not csv_files:
            return

        print(f"\n📦 Merging {len(csv_files)} batch files...")

        all_data = []
        for csv_file in csv_files:
            df = pd.read_csv(os.path.join(self.output_dir, csv_file))
            all_data.append(df)

        merged = pd.concat(all_data, ignore_index=True)

        # Remove duplicates (in case of overlaps)
        merged = merged.drop_duplicates(subset=['agent_id'], keep='first')

        # Save master file
        master_file = os.path.join(self.output_dir, "all_agents_merged.csv")
        merged.to_csv(master_file, index=False)

        print(f"✅ Merged {len(merged)} unique agents into: {master_file}")


# Example usage
if __name__ == "__main__":
    # Production-safe settings
    scraper = SafeContinuousScraper(
        delay_min=10,      # 10 second minimum delay
        delay_max=20,      # 20 second maximum delay
        batch_size=10,     # 10 agents per batch
        batch_break=1800,  # 30 minute break between batches
        output_dir="./scraped_agents"
    )

    # States to scrape
    states = [
        "Nevada",
        "Florida",
        "Texas",
        # Add more states as needed
    ]

    # Run continuously
    scraper.run_continuous(
        states=states,
        agents_per_state=50  # 50 agents per state
    )

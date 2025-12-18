"""
Production Runner - Uses settings from production_config.py
"""

from scrape_safe_continuous import SafeContinuousScraper
from production_config import *

def main():
    print("\n" + "="*80)
    print("🚀 PRODUCTION SCRAPER")
    print("="*80)
    print(f"\nMode: {[k for k, v in globals().items() if v == CURRENT_MODE and k.isupper()][0]}")
    print(f"Delay: {CURRENT_MODE['delay_min']}-{CURRENT_MODE['delay_max']} seconds")
    print(f"Batch size: {CURRENT_MODE['batch_size']} agents")
    print(f"Break time: {CURRENT_MODE['batch_break'] / 60:.0f} minutes")
    print(f"\nStates: {', '.join(STATES)}")
    print(f"Target per state: {AGENTS_PER_STATE} agents")

    # Calculate estimates
    avg_delay = (CURRENT_MODE['delay_min'] + CURRENT_MODE['delay_max']) / 2
    batch_time = CURRENT_MODE['batch_size'] * avg_delay
    total_time_per_batch = batch_time + CURRENT_MODE['batch_break']
    agents_per_hour = 3600 / total_time_per_batch * CURRENT_MODE['batch_size']

    print(f"\nEstimated rate: ~{agents_per_hour:.0f} agents/hour")
    print(f"Total agents: {len(STATES) * AGENTS_PER_STATE}")
    print(f"Estimated completion: {(len(STATES) * AGENTS_PER_STATE / agents_per_hour):.1f} hours")

    if PROXY:
        print(f"\n🌐 Using proxy: {PROXY[:30]}...")

    if any(v is not None for v in FILTERS.values()):
        print(f"\n🔍 Active filters:")
        for k, v in FILTERS.items():
            if v is not None:
                print(f"   {k}: {v}")

    print(f"\n💾 Output: {OUTPUT_DIR}")
    print("="*80 + "\n")

    # Create scraper
    scraper = SafeContinuousScraper(
        delay_min=CURRENT_MODE['delay_min'],
        delay_max=CURRENT_MODE['delay_max'],
        batch_size=CURRENT_MODE['batch_size'],
        batch_break=CURRENT_MODE['batch_break'],
        output_dir=OUTPUT_DIR
    )

    # Run
    scraper.run_continuous(
        states=STATES,
        agents_per_state=AGENTS_PER_STATE
    )

if __name__ == "__main__":
    main()

"""
Example: Search for real estate agents on Zillow
"""

from agentharvest import scrape_agent


def example_basic_search():
    """Basic agent search by state"""
    print("=" * 80)
    print("Example 1: Basic search - Top agents in California")
    print("=" * 80)

    agents = scrape_agent(
        state="California",
        limit=10
    )

    print(f"\n✅ Found {len(agents)} agents")
    print("\nFirst 3 agents:")
    print(agents[['name', 'brokerage_name', 'rating', 'review_count', 'sales_last_12_months']].head(3))

    # Save to CSV
    agents.to_csv("california_agents.csv", index=False)
    print(f"\n💾 Saved to california_agents.csv")


def example_filtered_search():
    """Search with filters"""
    print("\n\n" + "=" * 80)
    print("Example 2: Filtered search - High-performing agents in San Diego")
    print("=" * 80)

    agents = scrape_agent(
        city="San Diego",
        state="CA",
        rating_min=4.5,
        sales_min=20,
        exclude_teams=True,
        limit=10
    )

    print(f"\n✅ Found {len(agents)} agents")

    if len(agents) > 0:
        print("\nAgent details:")
        for i, agent in agents.iterrows():
            print(f"\n{i+1}. {agent['name']}")
            print(f"   Brokerage: {agent['brokerage_name']}")
            print(f"   Rating: {agent['rating']} ⭐ ({agent['review_count']} reviews)")
            print(f"   Sales (12mo): {agent['sales_last_12_months']}")
            print(f"   Price Range: {agent['price_range']}")
            print(f"   Profile: {agent['profile_url']}")


def example_by_zip():
    """Search by ZIP code"""
    print("\n\n" + "=" * 80)
    print("Example 3: Search by ZIP code - New York 10001")
    print("=" * 80)

    agents = scrape_agent(
        zip_code="10001",
        is_top_agent=True,
        limit=5
    )

    print(f"\n✅ Found {len(agents)} top agents")
    print(agents[['name', 'rating', 'sales_last_12_months', 'is_top_agent']])


if __name__ == "__main__":
    # Run examples
    try:
        example_basic_search()
        # example_filtered_search()  # Uncomment to run
        # example_by_zip()            # Uncomment to run

        print("\n\n" + "=" * 80)
        print("✅ All examples completed!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

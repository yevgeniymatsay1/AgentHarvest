"""
AgentHarvest Web UI - Simple interface for scraping Zillow agents
"""

import streamlit as st
import pandas as pd
from agentharvest import scrape_agent
import time

# Page config
st.set_page_config(
    page_title="AgentHarvest - Zillow Agent Scraper",
    page_icon="🏠",
    layout="wide"
)

# Title and description
st.title("🏠 AgentHarvest - Zillow Agent Scraper")
st.markdown("**Search for real estate agents on Zillow and export to CSV**")

# Sidebar for inputs
st.sidebar.header("Search Parameters")

# Location inputs
st.sidebar.subheader("📍 Location (Required)")
state = st.sidebar.text_input("State", placeholder="e.g., California or CA", help="State name or abbreviation")
city = st.sidebar.text_input("City (Optional)", placeholder="e.g., San Diego", help="Leave empty to search entire state")
zip_code = st.sidebar.text_input("ZIP Code (Optional)", placeholder="e.g., 92101", help="Leave empty to search by state/city")

# Filters
st.sidebar.subheader("🔍 Filters (Optional)")
rating_min = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.5, help="Filter agents by minimum rating")
sales_min = st.sidebar.number_input("Minimum Sales (Last 12 Months)", min_value=0, value=0, help="Filter by minimum sales")
agent_type = st.sidebar.selectbox("Agent Type", ["All", "Solo", "Team", "Broker"], help="Filter by agent type")

# Advanced options
with st.sidebar.expander("⚙️ Advanced Options"):
    limit = st.number_input("Maximum Results", min_value=1, max_value=1000, value=50, help="Number of agents to return (can be 500+, will just take longer)")
    fetch_profiles = st.checkbox("Fetch Comprehensive Data (phone/email)", value=True, help="Uses smart batching with random delays - safe for any quantity")
    is_top_agent = st.checkbox("Zillow Premier Agents Only", value=False, help="Only show Zillow Premier Agents")
    exclude_teams = st.checkbox("Exclude Teams", value=False, help="Only show individual agents")

    st.markdown("---")
    st.markdown("**🔄 Duplicate Prevention**")
    skip_scraped = st.checkbox("Skip Previously Scraped Agents", value=True, help="Automatically skip agents from previous runs. Uncheck to allow re-scraping.")
    if skip_scraped:
        st.caption("📝 History stored in: ~/.agentharvest_history.json")

    st.markdown("---")
    st.markdown("**🛡️ Automatic Safety Features**")
    st.info("""
    ✅ Random delays (15-60s between requests)
    ✅ Smart batching (5-15 agents per batch)
    ✅ Random breaks (10-20 min between batches)
    ✅ No detectable patterns - runs safely 24/7
    """)
    st.caption("💡 The system automatically prevents IP blocking with intelligent randomization.")

# Search button
search_button = st.sidebar.button("🔍 Search Agents", type="primary", use_container_width=True)

# Clear history button
st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Clear Scraping History", help="Remove all previously scraped agent IDs. Next search will include all agents."):
    from agentharvest import clear_scraping_history
    clear_scraping_history()
    st.sidebar.success("✅ History cleared! All agents can be scraped again.")

# Main content area
if not search_button:
    # Welcome screen
    st.info("👈 Enter search parameters in the sidebar and click **Search Agents** to get started!")

    st.markdown("### Features")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**📊 Comprehensive Data**")
        st.write("Get phone, email, ratings, sales, and more")

    with col2:
        st.markdown("**🎯 Smart Filters**")
        st.write("Filter by location, rating, sales, agent type")

    with col3:
        st.markdown("**💾 CSV Export**")
        st.write("Download results directly to CSV")

    st.markdown("### Quick Start")
    st.code("""
1. Enter a State (e.g., "California")
2. Optionally add filters (rating, sales, etc.)
3. Click "Search Agents"
4. Download CSV when done!
    """)

else:
    # Validate input
    if not state and not city and not zip_code:
        st.error("❌ Please enter at least one location parameter (State, City, or ZIP Code)")
        st.stop()

    # Show search parameters
    st.subheader("🔍 Searching...")
    search_params = []
    if state:
        search_params.append(f"State: {state}")
    if city:
        search_params.append(f"City: {city}")
    if zip_code:
        search_params.append(f"ZIP: {zip_code}")
    if rating_min > 0:
        search_params.append(f"Rating ≥ {rating_min}")
    if sales_min > 0:
        search_params.append(f"Sales ≥ {sales_min}")
    if agent_type != "All":
        search_params.append(f"Type: {agent_type}")

    st.info("📋 " + " | ".join(search_params))

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    detail_text = st.empty()
    break_text = st.empty()

    # Progress callback function for real-time updates
    def update_progress(data):
        stage = data.get('stage')

        if stage == 'profile_fetch_start':
            total = data.get('total')
            est_min = data.get('estimated_minutes', 0)
            status_text.info(f"🚀 Starting profile fetch for {total} agents (est: {est_min:.0f} min)")
            progress_bar.progress(0)

        elif stage == 'batch_start':
            batch_num = data.get('batch_num')
            batch_size = data.get('batch_size')
            current = data.get('current')
            total = data.get('total')
            status_text.info(f"📦 Batch {batch_num}: Processing {batch_size} agents")
            detail_text.text(f"Progress: {current}/{total} agents ({(current/total*100):.1f}%)")
            progress_bar.progress(current / total)

        elif stage == 'fetching_agent':
            agent_name = data.get('agent_name')
            current = data.get('current')
            total = data.get('total')
            batch_num = data.get('batch_num')
            status_text.info(f"📦 Batch {batch_num}: Fetching agent {current}/{total}")
            detail_text.text(f"👤 {agent_name}")
            progress_bar.progress(current / total)

        elif stage == 'delay':
            delay = data.get('delay_seconds', 0)
            current = data.get('current')
            total = data.get('total')
            detail_text.text(f"⏱️  Waiting {delay:.1f}s before next request...")
            progress_bar.progress(current / total)

        elif stage == 'break_start':
            break_min = data.get('break_minutes', 0)
            resume_time = data.get('resume_time')
            current = data.get('current')
            total = data.get('total')
            progress_pct = data.get('progress_percent', 0)
            status_text.warning(f"⏸️  Taking {break_min:.1f} minute break (anti-detection)")
            detail_text.text(f"Will resume at {resume_time} • {current}/{total} agents complete ({progress_pct:.1f}%)")
            break_text.info(f"⏰ Break in progress... Resuming at {resume_time}")
            progress_bar.progress(current / total)

        elif stage == 'break_progress':
            remaining = data.get('remaining_seconds', 0)
            resume_time = data.get('resume_time')
            current = data.get('current')
            total = data.get('total')
            remaining_min = remaining / 60
            status_text.warning(f"⏸️  Break: {remaining_min:.1f} minutes remaining")
            detail_text.text(f"Will resume at {resume_time} • {current}/{total} agents complete")
            break_text.info(f"⏰ {remaining_min:.1f} min left until resuming...")
            progress_bar.progress(current / total)

        elif stage == 'complete':
            total = data.get('total')
            with_phone = data.get('with_phone')
            with_email = data.get('with_email')
            status_text.success(f"✅ Complete! Fetched {total} agents")
            detail_text.text(f"📞 {with_phone} with phone • 📧 {with_email} with email")
            break_text.empty()
            progress_bar.progress(1.0)

    try:
        status_text.text("Initializing search...")
        progress_bar.progress(10)

        # Convert agent_type to lowercase or None
        agent_type_param = None if agent_type == "All" else agent_type.lower()

        # Run search
        if fetch_profiles:
            # Calculate estimated time with intelligent batching (updated times)
            # Avg delay: 37.5s, Avg batch: 10 agents, Avg break: 15 min (updated from 30)
            avg_delay = 37.5
            avg_batch = 10
            avg_break = 15  # Updated to reflect new 10-20 min range
            num_batches = (limit // avg_batch) + (1 if limit % avg_batch else 0)
            estimated_minutes = (limit * avg_delay / 60) + ((num_batches - 1) * avg_break)
            status_text.text(f"Searching Zillow for agents... (estimated: {estimated_minutes:.0f} min = {estimated_minutes/60:.1f} hours)")
        else:
            status_text.text(f"Searching Zillow for agents... (fast mode)")
        progress_bar.progress(30)

        start_time = time.time()
        agents_df = scrape_agent(
            state=state if state else None,
            city=city if city else None,
            zip_code=zip_code if zip_code else None,
            rating_min=rating_min if rating_min > 0 else None,
            sales_min=sales_min if sales_min > 0 else None,
            agent_type=agent_type_param,
            is_top_agent=is_top_agent if is_top_agent else None,
            exclude_teams=exclude_teams,
            limit=limit,
            fetch_profiles=fetch_profiles,
            skip_scraped=skip_scraped,
            progress_callback=update_progress if fetch_profiles else None,
        )

        elapsed_time = time.time() - start_time

        progress_bar.progress(100)
        status_text.empty()
        detail_text.empty()
        break_text.empty()

        # Display results
        if len(agents_df) == 0:
            st.warning("⚠️ No agents found matching your criteria. Try adjusting your filters.")
        else:
            st.success(f"✅ Found {len(agents_df)} agents in {elapsed_time:.1f} seconds!")

            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Agents", len(agents_df))

            with col2:
                avg_rating = agents_df['rating'].mean()
                st.metric("Avg Rating", f"{avg_rating:.1f}⭐" if pd.notna(avg_rating) else "N/A")

            with col3:
                with_phone = agents_df['phone'].notna().sum()
                st.metric("With Phone", f"{with_phone}/{len(agents_df)}")

            with col4:
                with_email = agents_df['email'].notna().sum()
                st.metric("With Email", f"{with_email}/{len(agents_df)}")

            # Agent type breakdown (if available)
            if fetch_profiles:
                st.subheader("📊 Agent Type Breakdown")
                type_counts = agents_df['agent_type'].value_counts()
                col1, col2, col3 = st.columns(3)

                with col1:
                    solo_count = type_counts.get('solo', 0)
                    st.metric("Solo Agents", solo_count)

                with col2:
                    team_count = type_counts.get('team', 0)
                    st.metric("Teams", team_count)

                with col3:
                    broker_count = type_counts.get('broker', 0)
                    st.metric("Brokers", broker_count)

            # Display table
            st.subheader("📋 Results")

            # Select columns to display
            if fetch_profiles:
                display_columns = ['name', 'agent_type', 'phone', 'email', 'rating', 'review_count',
                                 'sales_last_12_months', 'brokerage_name', 'city', 'state']
            else:
                display_columns = ['name', 'rating', 'review_count', 'sales_last_12_months',
                                 'brokerage_name', 'city', 'state']

            # Filter to available columns
            display_columns = [col for col in display_columns if col in agents_df.columns]

            st.dataframe(
                agents_df[display_columns],
                use_container_width=True,
                height=400
            )

            # Download button
            st.subheader("💾 Export Results")

            # Generate filename
            location_str = state or city or zip_code or "zillow"
            location_str = location_str.replace(" ", "_").lower()
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"agents_{location_str}_{timestamp}.csv"

            # Convert to CSV
            csv = agents_df.to_csv(index=False)

            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=filename,
                mime="text/csv",
                type="primary",
                use_container_width=True
            )

            st.success(f"✨ Click the button above to download **{filename}**")

            # Show sample data
            with st.expander("👁️ Preview Full Data (All Columns)"):
                st.dataframe(agents_df, use_container_width=True)

    except Exception as e:
        progress_bar.empty()
        status_text.empty()

        st.error(f"❌ Error: {str(e)}")

        if "403" in str(e):
            st.warning("""
**Rate Limit Detected**

Zillow has temporarily blocked your IP address. This happens when too many requests are made too quickly.

**Solutions:**
1. Wait 15-30 minutes and try again
2. Use a different network/IP address
3. Reduce the number of results (smaller limit)
            """)
        else:
            st.error("Please check your search parameters and try again.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ using [AgentHarvest](https://github.com)")
st.sidebar.caption("⚠️ Use responsibly and respect Zillow's Terms of Service")

"""
Use Playwright to capture Zillow agent search API calls
Run this script to automatically discover the API structure
"""

from playwright.sync_api import sync_playwright
import json
import time

def capture_zillow_api():
    """Navigate to Zillow agent search and capture network requests"""

    api_calls = []

    with sync_playwright() as p:
        # Launch browser
        print("🚀 Launching browser...")
        browser = p.chromium.launch(headless=False)  # Set to True for headless
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        # Set up network request listener
        def handle_request(request):
            url = request.url
            # Look for API calls (GraphQL, REST, etc.)
            if any(keyword in url.lower() for keyword in ['api', 'graphql', 'agent', 'professional', 'search']):
                if any(ext in url.lower() for ext in ['.js', '.css', '.png', '.jpg', '.gif', '.svg', '.woff']):
                    return  # Skip static resources

                request_data = {
                    'url': url,
                    'method': request.method,
                    'headers': request.headers,
                    'post_data': request.post_data if request.method == 'POST' else None
                }
                api_calls.append(request_data)
                print(f"\n📡 Captured: {request.method} {url[:100]}...")

        def handle_response(response):
            url = response.url
            # Capture responses for API calls
            if any(keyword in url.lower() for keyword in ['api', 'graphql', 'agent', 'professional', 'search']):
                if any(ext in url.lower() for ext in ['.js', '.css', '.png', '.jpg', '.gif', '.svg', '.woff']):
                    return

                try:
                    if response.status == 200:
                        # Try to get JSON response
                        try:
                            body = response.json()
                            # Find the corresponding request
                            for call in api_calls:
                                if call['url'] == url and 'response' not in call:
                                    call['response'] = body
                                    call['status'] = response.status
                                    print(f"✅ Got response for: {url[:100]}...")
                                    break
                        except:
                            # Not JSON or can't parse
                            pass
                except Exception as e:
                    print(f"❌ Error capturing response: {e}")

        page.on('request', handle_request)
        page.on('response', handle_response)

        # Navigate to Zillow professionals page
        print("\n🔍 Navigating to Zillow professionals page...")
        page.goto('https://www.zillow.com/professionals/real-estate-agent-reviews/')
        time.sleep(3)  # Wait for page to load

        # Try to find and fill in search input
        print("\n🔎 Looking for search input...")
        try:
            # Look for location search input (adjust selector as needed)
            search_selectors = [
                'input[name="location"]',
                'input[placeholder*="city"]',
                'input[placeholder*="location"]',
                'input[type="text"]',
                '#location-search',
                '.location-input'
            ]

            search_input = None
            for selector in search_selectors:
                try:
                    search_input = page.query_selector(selector)
                    if search_input and search_input.is_visible():
                        print(f"✅ Found search input: {selector}")
                        break
                except:
                    continue

            if search_input:
                # Enter location
                print("⌨️  Typing 'California'...")
                search_input.fill('California')
                time.sleep(1)

                # Try to submit search
                submit_selectors = [
                    'button[type="submit"]',
                    'button:has-text("Search")',
                    'button:has-text("Find")',
                    '.search-button'
                ]

                for selector in submit_selectors:
                    try:
                        submit_btn = page.query_selector(selector)
                        if submit_btn and submit_btn.is_visible():
                            print(f"🔘 Clicking submit: {selector}")
                            submit_btn.click()
                            break
                    except:
                        continue

                # Wait for results to load
                print("⏳ Waiting for results...")
                time.sleep(5)

                # Try to click "Load More" or pagination
                try:
                    load_more_selectors = [
                        'button:has-text("Load more")',
                        'button:has-text("Show more")',
                        '.pagination button:not([disabled])'
                    ]

                    for selector in load_more_selectors:
                        try:
                            load_more = page.query_selector(selector)
                            if load_more and load_more.is_visible():
                                print(f"🔘 Clicking load more: {selector}")
                                load_more.click()
                                time.sleep(3)
                                break
                        except:
                            continue
                except:
                    pass

            else:
                print("⚠️  Could not find search input. Capturing current page state...")

        except Exception as e:
            print(f"⚠️  Search automation failed: {e}")
            print("Capturing what we can from the current page...")

        # Wait a bit more to capture any delayed requests
        print("\n⏳ Waiting for any delayed requests...")
        time.sleep(3)

        # Take a screenshot for reference
        screenshot_path = 'research/zillow_screenshot.png'
        page.screenshot(path=screenshot_path)
        print(f"\n📸 Screenshot saved to {screenshot_path}")

        # Save page HTML for analysis
        html = page.content()
        with open('research/zillow_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("💾 Page HTML saved to research/zillow_page.html")

        browser.close()

    return api_calls

def analyze_api_calls(api_calls):
    """Analyze captured API calls and generate documentation"""

    print("\n" + "="*80)
    print("API ANALYSIS RESULTS")
    print("="*80)

    if not api_calls:
        print("\n❌ No API calls captured!")
        print("\nPossible reasons:")
        print("1. Zillow uses server-side rendering (data in HTML)")
        print("2. API calls are heavily obfuscated")
        print("3. Need to interact more with the page")
        print("\nCheck research/zillow_page.html for embedded JSON data")
        return

    print(f"\n✅ Captured {len(api_calls)} API calls\n")

    # Group by endpoint
    endpoints = {}
    for call in api_calls:
        url = call['url']
        method = call['method']
        key = f"{method} {url.split('?')[0]}"

        if key not in endpoints:
            endpoints[key] = []
        endpoints[key].append(call)

    # Analyze each endpoint
    for endpoint, calls in endpoints.items():
        print(f"\n{'='*80}")
        print(f"📍 ENDPOINT: {endpoint}")
        print(f"{'='*80}")

        call = calls[0]  # Use first call as example

        print(f"\n🔗 Full URL:")
        print(f"   {call['url']}")

        print(f"\n📤 Method: {call['method']}")

        print(f"\n📋 Headers:")
        for key, value in list(call['headers'].items())[:10]:  # First 10 headers
            if key.lower() not in ['cookie']:  # Skip sensitive data
                print(f"   {key}: {value}")

        if call['post_data']:
            print(f"\n📦 POST Data:")
            try:
                data = json.loads(call['post_data'])
                print(json.dumps(data, indent=2)[:500])  # First 500 chars
            except:
                print(f"   {call['post_data'][:500]}")

        if 'response' in call:
            print(f"\n✅ Response Status: {call.get('status', 'N/A')}")
            print(f"\n📥 Response Sample:")
            response = call['response']
            print(json.dumps(response, indent=2)[:1000])  # First 1000 chars

            # Try to identify agent data structure
            print(f"\n🔍 Looking for agent data in response...")

            def find_agent_arrays(obj, path=""):
                """Recursively find arrays that might contain agent data"""
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        new_path = f"{path}.{key}" if path else key
                        if isinstance(value, list) and len(value) > 0:
                            # Check if it looks like agent data
                            first_item = value[0]
                            if isinstance(first_item, dict):
                                # Look for agent-like fields
                                agent_fields = ['name', 'phone', 'email', 'rating', 'agent', 'professional']
                                if any(field in str(first_item).lower() for field in agent_fields):
                                    print(f"   ✅ Possible agent array at: {new_path}")
                                    print(f"      Length: {len(value)}")
                                    print(f"      Sample keys: {list(first_item.keys())[:10]}")
                        find_agent_arrays(value, new_path)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj[:1]):  # Just check first item
                        find_agent_arrays(item, f"{path}[{i}]")

            find_agent_arrays(response)

    # Save to file
    output_file = 'research/api_calls.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(api_calls, f, indent=2, default=str)
    print(f"\n\n💾 Full API call data saved to {output_file}")

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("1. Review the captured API calls above")
    print("2. Check research/api_calls.json for full details")
    print("3. If no API calls found, check research/zillow_page.html for embedded JSON")
    print("4. Update research/zillow_test.py with the working endpoint")
    print("5. Document findings in docs/zillow_api.md")

def main():
    print("="*80)
    print("ZILLOW API REVERSE ENGINEERING WITH PLAYWRIGHT")
    print("="*80)

    try:
        api_calls = capture_zillow_api()
        analyze_api_calls(api_calls)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure Playwright is installed:")
        print("  pip install playwright")
        print("  playwright install chromium")

if __name__ == "__main__":
    main()

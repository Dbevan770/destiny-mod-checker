import cloudscraper

# Define what page we are accessing.
URL = "https://www.light.gg/"

# Logic for sending get request of light.gg
async def requestPage(log):
    # Using cloudscraper to bypass cloudflare protection on light.gg
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'android',
            'desktop': False
        }
    )
    # Get request
    page = scraper.get(URL)

    # Store the text of the html
    page_content = page.text

    log.AddLine(f"Response from light.gg: {page.status_code}")
    
    # If the GET request returns anything other than a 200 code
    # the request failed, run it again
    if page.status_code != 200:
        return [page.status_code, "Failed to fetch page."]
    else:
        return [page.status_code, page_content]
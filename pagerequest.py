import cloudscraper

# Define what page we are accessing.
URL = "https://www.light.gg/"

# Logic for sending get request of light.gg
async def requestPage(log):
    max_attempts = 3
    attempt = 0
    page = None
    scraper = None
    # Using cloudscraper to bypass cloudflare protection on light.gg
    # If the first attempt fails retry up to 3 times
    while attempt < max_attempts:
        try:
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'android',
                    'desktop': False
                }
            )
            # Get request
            page = scraper.get(URL)
            log.AddLine(f"Response from light.gg: {page.status_code}")
            # Return an array containing the GET response code and the content itself
            return [page.status_code, page.text]
        except Exception as e:
            # Handle the exception
            print(e)
            attempt += 1
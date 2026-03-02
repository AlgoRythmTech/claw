from playwright.sync_api import sync_playwright


class BrowserResearcher:
    def brief_lookup(self, query: str) -> str:
        """Controlled Chromium lookup. Use sparingly for fact verification."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"https://duckduckgo.com/?q={query}", timeout=15000)
            snippet = page.locator("#links .result__snippet").first.inner_text(timeout=5000)
            browser.close()
            return snippet

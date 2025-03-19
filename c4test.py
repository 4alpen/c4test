import asyncio
import csv
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy

# Configuration - CHANGE THESE VALUES AS NEEDED
TARGET_URL = "https://forum.wordreference.com/"  # Change this to your target website
MAX_DEPTH = 2                      # How many levels deep to crawl
MAX_PAGES = 100                     # Maximum number of pages to crawl
KEYWORDS_TO_SEARCH = ["Türk", "Turk", "Turkish", "Turkiye", "Türkiye", "Ottoman"]
OUTPUT_FILE = "keyword_urls.csv"       # Output CSV file name

class KeywordSearcher:
    def __init__(self, url, max_depth, max_pages, keywords, output_file):
        self.url = url
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.keywords = keywords
        self.output_file = output_file
        self.found_keyword_urls = [] # List to store URLs where keywords are found

    async def search_website_for_keywords(self):
        print(f"Starting keyword search from {self.url}")
        print(f"Max depth: {self.max_depth}, Max pages: {self.max_pages}")
        print(f"Searching for keywords: {self.keywords}")

        config = CrawlerRunConfig(
            deep_crawl_strategy=BFSDeepCrawlStrategy(
                max_depth=self.max_depth,
                include_external=False,
                max_pages=self.max_pages
            ),
            scraping_strategy=LXMLWebScrapingStrategy(),
            verbose=True
        )

        async with AsyncWebCrawler() as crawler:
            results = await crawler.arun(self.url, config=config)

            print(f"Crawled {len(results)} pages")
            for result in results:
                if hasattr(result, 'text') and result.text:
                    if self._search_keywords(result.text):
                        print(f"Keywords found on URL: {result.url}")
                        self.found_keyword_urls.append(result.url) # Add URL to the list
                elif hasattr(result, 'html') and result.html:
                    if self._search_keywords(result.html):
                        print(f"Keywords found on URL: {result.url}")
                        self.found_keyword_urls.append(result.url) # Add URL to the list
                elif hasattr(result, 'body') and result.body:
                    if self._search_keywords(result.body):
                        print(f"Keywords found on URL: {result.url}")
                        self.found_keyword_urls.append(result.url) # Add URL to the list
                else:
                    print(f"Warning: No content found in CrawlResult for URL: {result.url}. Available attributes: {result.__dict__.keys()}")

        if self.found_keyword_urls:
            self._save_to_csv() # Save URLs to CSV after crawling
        else:
            print("No URLs with keywords found.")

    def _search_keywords(self, text_content):
        text_lower = text_content.lower()
        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                return True
        return False

    def _save_to_csv(self):
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for url in self.found_keyword_urls:
                writer.writerow({'url': url})

        print(f"URLs with keywords saved to {self.output_file}")


async def main():
    searcher = KeywordSearcher(TARGET_URL, MAX_DEPTH, MAX_PAGES, KEYWORDS_TO_SEARCH, OUTPUT_FILE)
    await searcher.search_website_for_keywords()

if __name__ == "__main__":
    asyncio.run(main())
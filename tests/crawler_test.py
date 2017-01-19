import sys
import os
sys.path.append(os.pardir)

from techcrunch.crawler import TechcrunchCrawler

if __name__ == '__main__':

    TECHCRUNCH_URL = "https://techcrunch.com/page/1"
    crawler = TechcrunchCrawler(TECHCRUNCH_URL)
    crawler.crawl()

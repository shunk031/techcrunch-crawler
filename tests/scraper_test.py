# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.pardir)

from techcrunch.scraper import TechcrunchScraper

if __name__ == '__main__':

    TECHCRUNCH_URL = "https://techcrunch.com/page/1"
    scraper = TechcrunchScraper(TECHCRUNCH_URL, "./dump_files")
    scraper.scrap()

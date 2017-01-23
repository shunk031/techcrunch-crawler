# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.pardir)

from techcrunch.crawler import TechcrunchCrawler
from slacker import Slacker
import json

HOME_DIR = os.path.expanduser("~")

if __name__ == '__main__':

    if os.path.isfile("status.json"):
        with open("status.json", "r") as rf:
            status_dict = json.load(rf)

        TECHCRUNCH_URL = status_dict["target_url"]
        page_count = status_dict["page_count"]

    else:
        TECHCRUNCH_URL = "https://techcrunch.com/page/186"
        page_count = 186

    crawler = TechcrunchCrawler(TECHCRUNCH_URL, "./dump_files", page_count=page_count)

    slacker_config = os.path.join(HOME_DIR, ".slacker.config")
    with open(slacker_config, "r") as rf:
        config = json.load(rf)

    slacker = Slacker(config["token"])

    try:
        finish_crawl = crawler.crawl()
        slacker.chat.post_message("#crawler", "{}: {}".format(crawler.__class__.__name__, finish_crawl))

    except Exception as e:

        trial = 0
        while trial < 3:
            try:
                slacker.chat.post_message("#crawler", "{}: {}".format(crawler.__class__.__name__, e))
            except Exception:
                trial += 1
            else:
                break

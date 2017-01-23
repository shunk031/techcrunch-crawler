import sys
import os
sys.path.append(os.pardir)

from techcrunch.crawler import TechcrunchCrawler
from slacker import Slacker
import json

HOME_DIR = os.path.expanduser("~")

if __name__ == '__main__':

    TECHCRUNCH_URL = "https://techcrunch.com/page/1"
    crawler = TechcrunchCrawler(TECHCRUNCH_URL)

    try:
        crawler.crawl()

    except Exception as e:
        slacker_config = os.path.join(HOME_DIR, ".slacker.config")
        with open(slacker_config, "r") as rf:
            config = json.load(rf)

        slacker = Slacker(config["token"])

        trial = 0
        while trial < 3:
            try:
                slacker.chat.post_message("#crawler", e)
            except Exception:
                trial += 1
            else:
                break

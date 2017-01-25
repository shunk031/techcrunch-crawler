# -*- coding: utf-8 -*-

from __future__ import print_function
from techcrunch.scraper import TechcrunchScraper
from bs4 import BeautifulSoup

import time
import json
import traceback

try:
    from urllib.request import urlopen
    from urllib.parse import urljoin
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import urlopen
    from ullib2 import urljoin
    from urllib2 import HTTPError


class TechcrunchCrawler:

    FINISH_CRAWL = "Finish crawl!"
    base_url = "https://techcrunch.com/"

    def __init__(self, target_url, save_dir="./data", page_count=1):
        self.target_url = target_url
        self.before_url = None
        self.save_dir = save_dir
        self.page_count = page_count

    def _make_soup(self, url):

        max_retries = 3
        retries = 0

        while True:
            try:
                with urlopen(url) as res:
                    html = res.read()
                return BeautifulSoup(html, "lxml")

            except HTTPError as err:
                print("[ EXCEPTION ] in {}#make_soup: {}".format(self.__class__.__name__, err))

                retries += 1
                if retries >= max_retries:
                    raise Exception("Too many retries.")

                wait = 2 ** (retries - 1)
                print("[ RETRY ] Waiting {} seconds...".format(wait))
                time.sleep(wait)

    def get_next_page_link(self, url):

        self.before_url = url
        soup = self._make_soup(self.target_url)

        ol_pagination = soup.find("ol", {"class": "pagination"})
        a_next = ol_pagination.find("li", {"class": "next"}).find("a")

        print("a_next: {}".format(a_next["href"]))

        if a_next is not None and "href" in a_next.attrs:
            abs_next_page_url = a_next["href"]
            next_page_url = urljoin(self.base_url, abs_next_page_url)

            if self.before_url != next_page_url:
                print("[ DEBUG ] Next article list page: {}".format(url))
                return next_page_url

        return None

    def crawl(self):

        try:
            while True:
                start = time.time()
                print("[ DEBUG ] Now page {} PROCESSING".format(self.page_count))
                scraper = TechcrunchScraper(self.target_url, self.save_dir)
                scraper.scrap()
                self.target_url = self.get_next_page_link(self.target_url)

                if self.target_url is None:
                    break

                self.page_count += 1
                time.sleep(2)
                end = time.time()

                elapsed_sec = end - start
                elapsed_min = elapsed_sec / 60

                if elapsed_min < 1:
                    print("[ DEBUG ] Elapsed time: {:.2f} [sec]".format(elapsed_sec))
                else:
                    print("[ DEBUG ] Elapsed time: {:.2f} [min]".format(elapsed_min))

        except Exception as e:

            print("Exception occured: {}".format(e))
            traceback.print_tb(e.__traceback__)

            self.save_status()

        return self.FINISH_CRAWL

    def save_status(self):

        status_dict = {}
        status_dict["target_url"] = self.target_url
        status_dict["page_count"] = self.page_count

        with open("status.json", "w") as wf:
            json.dump(status_dict, wf, indent=2)

        print("[ DUMP ] Dump status.json")

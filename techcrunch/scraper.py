# -*- coding: utf-8 -*-

from __future__ import print_function
from bs4 import BeautifulSoup

import os
import csv
import time
import traceback

try:
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import urlopen
    from urllib2 import HTTPError


class TechcrunchScraper:

    base_url = "https://techcrunch.com/page/1/"

    def __init__(self, target_url, save_dir):
        self.target_url = target_url
        self.save_dir = save_dir

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

    def scrap(self):
        article_detail_url_list = self.get_article_detail_urls()

        article_detail_info = []
        for article_url in article_detail_url_list:
            try:
                article_dict = self.get_article_detail_info_dict(article_url)
                article_detail_info.append(article_dict)
            except Exception as e:
                print(e)

        self.save_article_detail_info_list(article_detail_info)

    def get_article_detail_urls(self):

        soup = self._make_soup(self.target_url)

        # 記事概要のそれぞれのデータを取得する
        div_l_main_containers = soup.find_all("div", {"class": "l-main-container"})
        li_river_blocks_list = []
        for div_l_main_container in div_l_main_containers:
            li_river_blocks = div_l_main_container.find_all("li", {"class": "river-block"})

            for li_river_block in li_river_blocks:
                li_river_blocks_list.append(li_river_block)

        article_detail_url_list = []
        for li_river_block in li_river_blocks_list:
            if "data-permalink" in li_river_block.attrs:
                url = li_river_block["data-permalink"]
            else:
                url = li_river_block.find("a")
                url = url["href"]
            print("[ GET ] Get URL: {}".format(url))

            article_detail_url_list.append(url)

        return article_detail_url_list

    def get_article_detail_info_dict(self, article_url):

        article_dict = {}
        article_dict["url"] = article_url

        detail_soup = self._make_soup(article_url)

        try:
            h1_tweet_title = detail_soup.find("h1", {"class": "tweet-title"})

        except AttributeError as err:
            traceback.print_tb(err.__traceback__)
            h1_tweet_title = detail_soup.find("h1")

        title = h1_tweet_title.get_text().strip()
        print("[ GET ] Title: {}".format(title))

        article_dict["title"] = title

        try:
            div_article_entry = detail_soup.find("div", {"class": "article-entry"})
            p_article_texts = div_article_entry.find_all("p")
            article_content = [p_article_text.get_text() for p_article_text in p_article_texts]
            article_content = " ".join(article_content)

        except AttributeError as err:
            traceback.print_tb(err.__traceback__)
            article_content = None

        article_dict["article"] = article_content

        return article_dict

    def save_article_detail_info_list(self, article_detail_info_list):

        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)

        for article_detail_dict in article_detail_info_list:
            article_title = article_detail_dict["title"]
            csv_filename = self._convert_filename(article_title)
            csv_filename = "{}.csv".format(csv_filename)

            with open(os.path.join(self.save_dir, csv_filename), "w") as wf:
                writer = csv.writer(wf)
                writer.writerow([article_detail_dict["title"],
                                 article_detail_dict["url"],
                                 article_detail_dict["article"]])

    def _convert_filename(self, article_title):

        filename = article_title.replace(" ", "_")
        filename = filename.replace("/", "")
        filename = filename.replace("?", "")

        if len(filename) > 250:
            filename = filename[:250]
        return filename

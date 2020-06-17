"""

Website - General class for websites with the format of Stack Exchange
         (for instance -stack overflow)
         create soup of pages, find last page and create soups for main topic pages

Authors: Nir Barazida and Inbar Shirizly
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import json

# get constant SLEEP_FACTOR for json file
with open("data_mining_constants.txt", "r") as json_file:
    constants_data = json.load(json_file)
SLEEP_FACTOR = constants_data["constants for user"]["SLEEP_FACTOR"]


class Website(object):
    """
    General class for the website crawler with the format of Stack Exchange
    the class bundles several general methods:
    1. create soup for url input and sleep for the request time * factor
    2. get last main topic page for input topic (users/tags etc)
    3. get soups of each input main topic page (that contain X amount of topic domain)
    """

    def __init__(self, website_name):
        """
        initiates parameters of the class
        :param website_name: domain name of the website that is been scrapped (str)
        """
        self._website_name = website_name

    @property
    def website_url(self):
        return f"https://{self._website_name}.com"

    @ staticmethod
    def create_soup(url):
        """
        Static method that return soup from users url
        sleeps between each request according to the time
        that took to the request to be executed * SLEEP FACTOR
        :param url: input url (str)
        :return: soup: content of the url (BeautifulSoup)
        """
        page = requests.get(url)
        time_sleep = page.elapsed.total_seconds()
        time.sleep(time_sleep * SLEEP_FACTOR)
        soup = BeautifulSoup(page.content, "html.parser")
        return soup

    @staticmethod
    def get_num_of_last_page(url):
        """
        Static method that return the number of pages existing in the website
        for the specific topic (i.e users, tags, etc)
        :param url: input url (str)
        :return: number pages for the topic (int)
        """
        soup = Website.create_soup(url)
        pages_path = soup.find_all("a", {"class": "s-pagination--item js-pagination-item"})
        max_num_page = max({int(re.search(r'\d+', new_page["href"]).group()) for new_page in pages_path})
        return max_num_page

    def get_pages_soups(self, topic_url):
        """
        generator which returns soups for all the main topic pages
        uses the link under the "next" bottom in the previous page
        The main topic pages are pages that include a general view about many
        of the topic individuals (users, tags, etc) and from them the child class
        (such as UserAnalysis) extracts the links for each individual
        :param topic_url: first main topic url (str)
        :return: soup of the next main users page
        """
        number_of_last_page = self.get_num_of_last_page(topic_url)
        soup = Website.create_soup(topic_url)
        yield soup

        for i in range(number_of_last_page - 1):
            last_link = self.website_url + soup.find('a', {'rel': 'next'})['href']
            soup = Website.create_soup(last_link)
            yield soup


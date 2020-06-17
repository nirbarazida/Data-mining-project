import requests
from bs4 import BeautifulSoup
import re
import time
import json

with open("data_mining_constants.txt", "r") as json_file:
    constants_data = json.load(json_file)

SLEEP_FACTOR = constants_data["constants for user"]["SLEEP_FACTOR"]

class Website(object):
    """
    General class for the website crawler:
    1. generate website name
    2. create soup for url input (and timing)
    3. get number of pages for an input topic (users/tags etc)
    4. get soups of each input main topic page (that contain X amount of topic domain)
    """

    def __init__(self, website_name):
        self._website_name = website_name
        self._website_url = f"https://{website_name}.com"

    def get_bare_website_url(self):
        return self._website_url

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
        #print(f"request page {url} in {3 * time_sleep} seconds (include sleep)")
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
        these are the pages that include a general view about many
        of the topic individuals (users, tags, etc)
        :param topic_url: first main topic url (str)
        :return: soup of the next main users page
        """
        number_of_last_page = self.get_num_of_last_page(topic_url)
        soup = Website.create_soup(topic_url)
        yield soup

        for i in range(number_of_last_page - 1):
            last_link = self.get_bare_website_url() + soup.find('a', {'rel': 'next'})['href']
            soup = Website.create_soup(last_link)
            yield soup
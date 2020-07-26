"""
Website - General class for websites with the format of Stack Exchange
         (for instance -stack overflow)
         create soup of pages, find last page and create soups for main topic pages
"""

from src import config
import requests
from bs4 import BeautifulSoup
import re
import time


class Website:
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
        self._total_users = None
        self._total_answers = None
        self._total_questions = None
        self._answers_per_minute = None
        self._questions_per_minute = None

    @property
    def website_url(self):
        return f"https://{self._website_name}.com"

    @staticmethod
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
        time.sleep(time_sleep * config.SLEEP_FACTOR)
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

        for _ in range(number_of_last_page - 1):
            last_link = self.website_url + soup.find('a', {'rel': 'next'})['href']
            soup = Website.create_soup(last_link)
            yield soup

    @staticmethod
    def get_api_json_content(base_url, params):
        """
        get json data from the stack exchange api
        :param base_url: url with the basic
        :param params: meta data for the specific api request
        :return: json of the requested api - parsing the items
        """
        page = requests.get(base_url, params=params)
        return page.json()["items"][0]


    def get_website_data_api(self):

        api_url = config.API_WEBSITE_BASE_URL + config.API_TYPE_WEBSITE_DATA
        params = {"site": self._website_name}
        json_content = self.get_api_json_content(api_url, params)
        self._total_users = json_content["total_users"]
        self._total_answers = json_content["total_answers"]
        self._total_questions = json_content["total_questions"]
        self._answers_per_minute = json_content["answers_per_minute"]
        self._questions_per_minute = json_content["questions_per_minute"]

    @property
    def website_info(self):
        """
        getter method to create or update WebsitesT instance.
        :return: information that relevant to WebsitesT (dict)
        """
        return {
            'name': self._website_name,
            'total_users': self._total_users,
            'total_answers': self._total_answers,
            'total_questions': self._total_questions,
            'answers_per_minute': self._answers_per_minute,
            'questions_per_minute': self._questions_per_minute,
        }

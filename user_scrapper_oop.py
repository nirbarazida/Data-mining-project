from bs4 import BeautifulSoup
import requests
import re
import time
from main_file import SLEEP_FACTOR, MIN_NUM_USERS_TO_SCRAP, FIRST_INSTANCE_TO_SCRAP

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


class UserAnalysis(Website):
    """
    Class for user analysis in a website
    contains method to get links for each individual user page
    """
    def __init__(self, website_name, index_first_page, index_first_instance_first_page):
        Website.__init__(self, website_name)
        self._index_first_page = index_first_page
        self._first_users_page_url = self._website_url +\
                                              f'/users?page={index_first_page}&tab=reputation&filter=all'
        self._index_first_instance_first_page = index_first_instance_first_page

    def get_first_url(self):
        return self._first_users_page_url

    def generate_users_links(self):
        """
        generator which return url link for each individual user
        :return:
        """

        for i, soup in enumerate(self.get_pages_soups(self.get_first_url())):
            print(f"website: {self.get_bare_website_url()} ,page {i + self._index_first_page}")
            users_grid = soup.find("div", {"class": "grid-layout"})
            users_info = users_grid.find_all_next("div", {"class": "user-info"})

            first_instance_in_page = self._index_first_instance_first_page - 1 if i == 0 else 0

            for user_info in users_info[first_instance_in_page:]:
                user_details = user_info.find("div", {"class": "user-details"})
                yield self.get_bare_website_url() + user_details.find("a")["href"]


class User(UserAnalysis):
    num_user_dict = {}

    def __init__(self, website_name, user_url):
        Website.__init__(self, website_name)
        soup = Website.create_soup(user_url)

        self._name = soup.find("div", {"class": "grid--cell fw-bold"}).text
        self._reputation = int(soup.find("div", {"class": "grid--cell fs-title fc-dark"}).text.replace(',', ''))
        self._highest_rating_for_one_post = int(soup.find("span", {"class": "grid--cell vote accepted"}).text) # TODO:
        User.num_user_dict[self._website_name] = User.num_user_dict.get(self._website_name, FIRST_INSTANCE_TO_SCRAP - 1) + 1
        self._rank = User.num_user_dict[self._website_name]

    def get_dict(self):
        return {"Website": self._website_name, "#": self._rank, "name": self._name,
                "reputation": self._reputation, "highest_rating_for_one_post": self._highest_rating_for_one_post}

    def __repr__(self):
        return f"{self.get_dict()}"







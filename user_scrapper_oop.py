from bs4 import BeautifulSoup
import requests
import re
import time
from main_file import SLEEP_FACTOR, MIN_NUM_USERS_TO_SCRAP


class Website(object):
    """
    General class for the website crawler:
    1. generate website name
    2. create soup for url input (and timing)
    3. get number of pages for an input topic (users/tags etc)
    4. get soups of each input main topic page (that contain X amount of topic domain)
    """

    def __init__(self, website_name="stackoverflow"):
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
    def get_number_of_pages_needed(url):
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
        number_of_last_page = self.get_number_of_pages_needed(topic_url)
        soup = Website.create_soup(topic_url)
        yield soup

        for i in range(number_of_last_page - 1):
            last_link = self.get_bare_website_url() + soup.find('a', {'rel': 'next'})['href']
            soup = Website.create_soup(last_link)
            yield soup


class TagsAnalysis(Website):

    @property
    def tags_url(self):
        return self._website_url + '/tags'

    def get_tags_high_level_data(self):

        for i, soup in enumerate(self.get_pages_soups(self.tags_url)):

            print(f"website: {self.get_bare_website_url()}, tag page {i + 1}")
            main_bar = soup.find("div", {"id": "mainbar-full"})
            tags = main_bar.find_all("div", {"class": "s-card"})

            for tag in tags:
                cells = tag.find_all("div", {"class": "grid--cell"})
                cells_text_list = [cell.text.strip() for cell in cells]
                yield [cells_text_list[0]] + [re.findall(r'\d+', cell) for cell in cells_text_list[2:]]


class UserAnalysis(Website):
    """
    Class for user analysis in a website
    contains method to get links for each individual user page
    """

    @property
    def users_url(self):
        return self._website_url + '/users'

    def generate_users_links(self):
        """
        generator which return url link for each individual user
        :return:
        """

        for i, soup in enumerate(self.get_pages_soups(self.users_url)):
            print(f"website: {self.get_bare_website_url()} ,page {i + 1}")
            users_grid = soup.find("div", {"class": "grid-layout"})
            users_info = users_grid.find_all_next("div", {"class": "user-info"})

            for user_info in users_info:
                user_details = user_info.find("div", {"class": "user-details"})
                yield self.get_bare_website_url() + user_details.find("a")["href"]


class User(UserAnalysis):
    num_user = 0

    def __init__(self, user_url, website_name):
        Website.__init__(self, website_name)
        self._user_url = user_url
        soup = Website.create_soup(self._user_url)

        self._name = soup.find("div", {"class": "grid--cell fw-bold"}).text
        self._reputation = int(soup.find("div", {"class": "grid--cell fs-title fc-dark"}).text.replace(',', ''))
        self._highest_rating_for_one_post = int(soup.find("span", {"class": "grid--cell vote accepted"}).text)
        User.num_user += 1


    def get_dict(self):
        return {"Website": self.get_bare_website_url(), "#": User.num_user, "name": self._name,
                "reputation": self._reputation, "highest_rating_for_one_post": self._highest_rating_for_one_post}








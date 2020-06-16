from bs4 import BeautifulSoup
import requests
import re
import time
from main_file import SLEEP_FACTOR, MIN_NUM_USERS_TO_SCRAP, FIRST_INSTANCE_TO_SCRAP
from datetime import datetime

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


class User(UserAnalysis, dict):  # :TODO: change first letter to big

    num_user_dict = {}

    """
    inherit all the class website features
    gets also the url of the user
    creats a new user based on the url
    """

    def __init__(self, website_name, url):
        dict.__init__(self)
        Website.__init__(self, website_name)

        self.soup = Website.create_soup(url)

        User.num_user_dict[self._website_name] = User.num_user_dict.get(self._website_name,
                                                                        FIRST_INSTANCE_TO_SCRAP - 1) + 1
        self['rank'] = User.num_user_dict[self._website_name]
        self['name'] = self.soup.find("div", {"class": "grid--cell fw-bold"}).text
        self['location'] = None  # not all users have a location in profile - must keep as default none
        self['member since'] = None
        self['reputation'] = int(self.soup.find("div", {"class": "grid--cell fs-title fc-dark"}).text.replace(',', ''))
        self['total number of answers'] = None
        self['number of people the user reached'] = None
      #  self['highest rating for one post'] = self.soup.find("span", {"class": "grid--cell vote accepted"}).text
        self['top tags names'] = []
        self['top tags scores'] = []
        self['number of posts'] = []


        # All the functions are in __init__ because we're defining new values to class user
        def basic_info(self):
            """
            gets self and defines users name and users location
            not all users have a location - thus location will stay None type
            """
            basic_info_scope = self.soup.find("ul", {"class": "list-reset grid gs8 gsy fd-column fc-medium"})
            basic_info_as_list = basic_info_scope.find_all_next("div", {"class": "grid gs8 gsx ai-center"})
            if basic_info_as_list[0].find('svg', {'aria-hidden': 'true', 'class': 'svg-icon iconLocation'}):
                self['location'] = basic_info_as_list[0].text.strip()
            for i in basic_info_as_list:
                if 'Member for' in i.text:
                    self['member since'] = datetime.strptime(i.find('span')['title'][:10], '%Y-%m-%d').date()
            del basic_info_scope, basic_info_as_list

        def user_comunity(self):
            """
            gets self and defines users number of answers, users people reached
            """
            user_community_info = self.soup.find('div', {'class': 'fc-medium mb16'}).find_all_next \
                ('div', {'class': 'grid--cell fs-body3 fc-dark fw-bold'})
            self['total number of answers'] = user_community_info[0].text
            self['number of people the user reached'] = user_community_info[2].text.strip('~')
            del user_community_info

        def user_tags(self):
            """
            gets self and append the values to the users top_tag_names, top_tag_scores, number_of_posts - that are lists
            """
            top_tag_names, top_tag_scores, number_of_posts = [], [], []
            all_tags_info = self.soup.find("div", {"id": "top-tags"})
            for tag in all_tags_info.find_all_next('a', {"class": "post-tag"}):
                top_tag_names.append(tag.text)
            self['top tags names'] = top_tag_names
            for tag in all_tags_info.find_all_next('div', {"class": "grid jc-end ml-auto"}):
                top_tag_scores.append(tag.text.replace("\n", " ").split()[1])
                number_of_posts.append(tag.text.replace("\n", " ").split()[3])
            self['top tags scores'] = top_tag_scores
            self['number of posts'] = number_of_posts
            del all_tags_info, top_tag_names, top_tag_scores, number_of_posts

        basic_info(self)  # creates: ['location'] , ['member since']
        user_comunity(self)  # creates: ['total number of answers'], ['number of people the user reached']
        user_tags(self)  # creates: ['top tags names'] , ['top tags scores'], ['number of posts']
        del self.soup  # :TODO: change self.soup to variable and not class variable








from bs4 import BeautifulSoup
import requests
import re
import time

MIN_NUM_USERS_TO_SCRAP = 1000
WEBSITE_NAME = "stackoverflow"
SLEEP_FACTOR = 2


class Website(object):
    """
    General class for the website crawler
    generate website name and includes the create_soup func
    """

    def __init__(self, website_name="stackoverflow"):
        self._website_url = f"https://{website_name}.com"

    def get_bare_website_url(self):
        return self._website_url

    @ staticmethod
    def create_soup(url):
        """
        return soup from users url
        :param url: the basic url (str)
        :return: soup: content of the url (BeautifulSoup)
        :return: sleep_time: time for the program to sleep after the request
        """
        page = requests.get(url)
        time_sleep = page.elapsed.total_seconds()
        time.sleep(time_sleep * SLEEP_FACTOR)
        #print(f"request page {url} in {3 * time_sleep} seconds (include sleep)")
        soup = BeautifulSoup(page.content, "html.parser")
        return soup


class UserAnalysis(Website):
    """
    Class for user analysis in a website
    """

    @property
    def users_url(self):
        return self._website_url + '/users'

    def get_number_of_pages_needed(self):
        # get number of pages according to the max number of pages exist in the website

        soup = Website.create_soup(self.users_url)
        pages_path = soup.find_all("a", {"class": "s-pagination--item js-pagination-item"})
        max_num_page = max({int(re.search(r'\d+', new_page["href"]).group()) for new_page in pages_path})
        return max_num_page

    def get_page_links(self):

        number_of_last_page = self.get_number_of_pages_needed()
        soup = Website.create_soup(self.users_url)
        yield soup

        for i in range(number_of_last_page - 1):
            last_link = self.get_bare_website_url() + soup.find('a', {'rel': 'next'})['href']
            soup = Website.create_soup(last_link)
            yield soup

    def generate_users_links(self):

        for i, soup in enumerate(self.get_page_links()):
            print(f"page {i + 1}")
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
        self._highest_rating_for_one_post = soup.find("span", {"class": "grid--cell vote accepted"}).text
        User.num_user += 1

    def get_dict(self):
        return {"number": User.num_user, "name": self._name,
                "reputation": self._reputation, "highest_rating_for_one_post": self._highest_rating_for_one_post}


t1 = time.perf_counter()
user_page = UserAnalysis(WEBSITE_NAME)
print(f"Website: {WEBSITE_NAME} ,number of users to scrap = {MIN_NUM_USERS_TO_SCRAP}, sleep factor = {SLEEP_FACTOR}")
for link in user_page.generate_users_links():
    #print(link)
    user = User(link, WEBSITE_NAME)
    print(user.get_dict())
    if user.num_user == MIN_NUM_USERS_TO_SCRAP:
        print(f"Finished to scrap {MIN_NUM_USERS_TO_SCRAP} users")
        break

t2 = time.perf_counter()
print(f"finished in {t2 - t1} seconds")





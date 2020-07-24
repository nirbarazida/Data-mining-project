"""
UserAnalysis - class that inherits from Website.
                it's main goal is to create a generator of links for 
                each individual user page.

Authors: Nir Barazida and Inbar Shirizly
"""
from src.website import Website


class UserAnalysis(Website):
    """
    Class for user analysis in a website
    contains method to get links for each individual user page
    as well the class supports the feature of scrapping users for chosen index
    (not necessarily from the first user)
    """

    def __init__(self, website_name, index_first_page, index_first_instance_first_page):
        """
        initiates parameters of the class, website name is inherited
        :param website_name: domain name of the website that is been scrapped (str)
        :param index_first_page: first page to scrap - according to the first individual user to scrap (int)
        :param index_first_instance_first_page: index of first individual user in the first page (int)
        """
        Website.__init__(self, website_name)
        self._index_first_page = index_first_page
        self._first_users_page_url = self.website_url +\
                                              f'/users?page={index_first_page}&tab=reputation&filter=all'
        self._index_first_instance_first_page = index_first_instance_first_page

    def get_first_url(self):
        return self._first_users_page_url

    def generate_users_links(self):
        """
        generator which yields url link for each individual user
        1. the generator prints which website and page is been scrapping (for controlling the process, especially in
        the case of threading)
        2. If it's the first page to scrap, the value of the variable: first_instance_in_page will the first index needed
            (to prevent requesting unnecessary pages), else: it starts from the first user link
        3. for loop over the relevant users - retrieving the relevant link per individual user

        :yield: url link for each individual user (str)
        """

        for index, soup in enumerate(self.get_pages_soups(self.get_first_url())):
            users_grid = soup.find("div", {"class": "grid-layout"})
            users_info = users_grid.find_all_next("div", {"class": "user-info"})

            first_instance_in_page = self._index_first_instance_first_page - 1 if index == 0 else 0

            for user_info in users_info[first_instance_in_page:]:
                user_details = user_info.find("div", {"class": "user-details"})
                yield self.website_url + user_details.find("a")["href"]
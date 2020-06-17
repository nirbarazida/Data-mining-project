from website import Website


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
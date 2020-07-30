from src import config, logger
from datetime import datetime, timedelta
import ast
import re
from src.geo_location import create_location
from src.website import Website


class UserScraper:
    # rank holder for users from each website, i.e : {"stackoverflow": 5,"another website":2}
    num_user_dict = {}

    # find indexes of January 1, in the years searched for reputation. get threshold for it (4 years from today)
    threshold_date = datetime.now() - timedelta(days=4 * 365)
    year_indexes = [-(datetime.now() - datetime(year, 1, 1)).days for year in config.REPUTATION_YEARS]

    def __init__(self, url, website, first_instance_to_scrap):

        self._url = url
        self._website_name = website
        self._soup = Website.create_soup(url)

        UserScraper.num_user_dict[self._website_name] = \
            UserScraper.num_user_dict.get(self._website_name, first_instance_to_scrap - 1) + 1

        self._rank = UserScraper.num_user_dict[self._website_name]

        self._name = self._soup.find("div", {"class": "grid--cell fw-bold"}).text
        self._member_since = None
        self._profile_views = 0
        self._answers = None
        self._people_reached = None
        self._country = None  # not all users have a valid location in profile - must keep as default none
        self._continent = None  # same as line above
        self._new_location_name_in_website = None  # flag for adding record to Stack_Exchange_Location table
        self._reputation_now = int(self._soup.find("div", {"class": "grid--cell fs-title fc-dark"}). \
                                   text.replace(',', ''))

        # construct all the None value with methods from the class
        self.professional_info()
        self.personal_info()

        # get value from a method
        self._reputation_hist = self.reputation_hist()
        self._tags = self.create_tags()

    def personal_info(self):
        """
        Defines users name and users location
        not all users have a location (country and continent) - thus location will stay None type
        The function contains a full process for finding location of the user - in GeoLocation class
        """

        basic_info_scope = self._soup.find("ul", {"class": "list-reset grid gs8 gsy fd-column fc-medium"})
        basic_info_as_list = basic_info_scope.find_all_next("div", {"class": "grid gs8 gsx ai-center"})
        if basic_info_as_list[0].find('svg', {'aria-hidden': 'true', 'class': 'svg-icon iconLocation'}):
            location_string = basic_info_as_list[0].text.strip()

            # encode the lactation string to UTF-8
            try:
                config.ENCODE_REGEX.search(str(location_string.encode('utf-8', 'ignore'))).group(2)
            except AttributeError:
                logger.warning(f'Could not encode to UTF-8mb4 the location string:{location_string}'
                             f' for user: {self._name} with url: {self._url}.')
                self._new_location_name_in_website = None

            if location_string:
                temp_location_tuple = create_location(location_string, self._name, self._website_name)
                self._country, self._continent, self._new_location_name_in_website =  temp_location_tuple



        for index in basic_info_as_list:
            if 'Member for' in index.text:
                self._member_since = datetime.strptime(index.find('span')['title'][:-1], '%Y-%m-%d %H:%M:%S')
            if 'profile views' in index.text:
                self._profile_views = int(index.text.strip().split()[0].replace(",", ""))
                break

    def professional_info(self):
        """
        Defines users number of answers and users people reached
        """
        user_community_info = self._soup.find('div', {'class': 'fc-medium mb16'})
        if user_community_info:
            user_community_info = user_community_info.find_all_next('div',
                                                                    {'class': 'grid--cell fs-body3 fc-dark fw-bold'})
            self._answers = int(user_community_info[0].text.replace(",", ""))
            people_reached = user_community_info[2].text.strip('~')
            self._people_reached = int(float(people_reached[:-1]) * (10 ** config.magnitude_dict[people_reached[-1]]))

    def reputation_hist(self):
        """
        user reputation for years: [2017, 2018, 2019 ,2020]
        will evaluate years only for users registered before 2017
        in case that users is registered more then 4 years ago and there is a problem,
        log a warning for checking manually the issue
        :return: reputation for each year (dict) of dict of None's
        """
        if self._member_since < UserScraper.threshold_date:
            soup_activity = Website.create_soup(self._url + "?tab=topactivity")
            source_data = soup_activity.find("div", {"id": "top-cards"}).contents[3].string
            numbers = re.search(config.REPUTATION_REGEX, source_data).group(1)
            reputation_numbers = ast.literal_eval(numbers)
            try:
                return {f"reputation_{config.REPUTATION_YEARS[i]}": reputation_numbers[UserScraper.year_indexes[i]]
                        for i in range(len(config.REPUTATION_YEARS))}

            except IndexError:
                logger.warning(f"website {self._website_name} user {self._name}"
                                           f" is member since more than 4 years but have reputation plot of month")

        return {f"reputation_{config.REPUTATION_YEARS[i]}": None for i in range(len(config.REPUTATION_YEARS))}

    def create_tags(self):
        """
        scraps all tags info from user page
        rapes it in list of tuples [(tag name, tag score, tag answers) ..]
        """
        # create a scoop of tags in all the html soup
        all_tags_info = self._soup.find("div", {"id": "top-tags"})

        # user might not have tags
        if all_tags_info:
            tags = []
            for tag in all_tags_info.find_all_next('a', {"class": "post-tag"}):
                tags.append([tag.text])
            for index, tag in enumerate(all_tags_info.find_all_next('div', {"class": "grid jc-end ml-auto"})):
                tags[index].append(int(tag.text.replace("\n", " ").split()[1].replace(",", "")))
                tags[index].append(int(tag.text.replace("\n", " ").split()[3].replace(",", "")))
            return tags

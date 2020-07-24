from src import config, logger
from datetime import datetime, timedelta
import ast
import re
from src.geo_location import GeoLocation
from src.website import Website


# find indexes of 1 of January in the years searched for reputation. get threshold for it (4 years from today)
now = datetime.now()
threshold_date = now - timedelta(days=4 * 365)
year_indexes = [-(now - datetime(year, 1, 1)).days for year in config.REPUTATION_YEARS]


class UserScraper(GeoLocation):
    # rank holder for users from each website, i.e : {"stackoverflow": 5,"another website":2}
    num_user_dict = {}

    def __init__(self, url, website, first_instance_to_scrap):

        GeoLocation.__init__(self)

        self._url = url
        self._website_name = website
        self._soup = Website.create_soup(url)

        UserScraper.num_user_dict[self._website_name] = \
            UserScraper.num_user_dict.get(self._website_name, first_instance_to_scrap - 1) + 1

        self._rank = UserScraper.num_user_dict[self._website_name]

        self._name = None
        self._member_since = None
        self._profile_views = 0
        self._answers = None
        self._people_reached = None
        self._country = None  # not all users have a valid location in profile - must keep as default none
        self._continent = None  # same as line above
        self._new_location_name_in_website = None  # flag for adding record to Stack_Exchange_Location table
        self._reputation_now = None
        self._reputation_2017 = None
        self._reputation_2018 = None
        self._reputation_2019 = None
        self._reputation_2020 = None
        self._tags = None

    def user_name_and_reputation(self):
        """scrapes the user's name and reputation today"""
        self._reputation_now = int(self._soup.find("div", {"class": "grid--cell fs-title fc-dark"}). \
                                   text.replace(',', ''))
        self._name = self._soup.find("div", {"class": "grid--cell fw-bold"}).text

    def personal_info(self):
        """
        Defines users name and users location
        not all users have a location (country and continent) - thus location will stay None type
        The function contains a full process for finding location of the user (in case he wrote something describes it).
        The process manage the locations with a dynamic programming approach (time over storage)
        1. check if user location description last phrase is part of the known phrases which were filled manually to
        the json file - if yes, allocate them
        2. query in the table of the database that includes phrases in the websites the accepted as describing
            users location, if it finds value in the DB, allocates these values to the user location.
        3. runs an internal function which takes users location description and check it with an api module
        4. If a location have been founded, checks if the phrase of users description can be added to the sql table
        """

        basic_info_scope = self._soup.find("ul", {"class": "list-reset grid gs8 gsy fd-column fc-medium"})
        basic_info_as_list = basic_info_scope.find_all_next("div", {"class": "grid gs8 gsx ai-center"})
        if basic_info_as_list[0].find('svg', {'aria-hidden': 'true', 'class': 'svg-icon iconLocation'}):
            location_string = basic_info_as_list[0].text.strip()
            self._country, self._continent, self._new_location_name_in_website =\
                GeoLocation.create_location(location_string, self._name, self._website_name)

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
        :return: None
        """
        if self._member_since < threshold_date:
            soup_activity = Website.create_soup(self._url + "?tab=topactivity")
            source_data = soup_activity.find("div", {"id": "top-cards"}).contents[3].string
            numbers = re.search(config.REPUTATION_REGEX, source_data).group(1)
            reputation_numbers = ast.literal_eval(numbers)
            try:
                self._reputation_2017 = reputation_numbers[year_indexes[0]]
                self._reputation_2018 = reputation_numbers[year_indexes[1]]
                self._reputation_2019 = reputation_numbers[year_indexes[2]]
                self._reputation_2020 = reputation_numbers[year_indexes[3]]
            except IndexError:
                logger.warning(f"website {self._website_name} user {self._name}"
                                           f" is member since more than 4 years but have reputation plot of month")

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

            self._tags = tags

    def create_user(self):
        self.user_name_and_reputation()
        self.professional_info()
        self.personal_info()
        self.reputation_hist()
        self.create_tags()

from datetime import datetime, timedelta
import ast
from logger import Logger
import conf
import requests
from bs4 import BeautifulSoup
import re
import time
from command_args import args
from GeoLocation import GeoLocation

SLEEP_FACTOR = args.sleep_factor

# find indexes of 1 of January in the years searched for reputation. get threshold for it (4 years from today)
now = datetime.now()
threshold_date = now - timedelta(days=4 * 365)
year_indexes = [-(now - datetime(year, 1, 1)).days for year in conf.REPUTATION_YEARS]

logger_UserScraper = Logger("UserScraper").logger
logger_not_scrapped = Logger("not_scrapped").logger


class UserScraper(GeoLocation):

    def __init__(self, url, website):

        # Website.__init__(self, website_name) # todo : drop
        # self._soup = Website.create_soup(url) # todo : drop
        GeoLocation.__init__(self)

        self._url = url
        self._website = website
        self._soup = UserScraper.create_soup(url)

        # todo: raise error if we don't define this variables
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
        time.sleep(time_sleep * SLEEP_FACTOR)
        soup = BeautifulSoup(page.content, "html.parser")
        return soup

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
            self._location_string = basic_info_as_list[0].text.strip()
            GeoLocation.create_location(self)
            # # finds last phrase after comma of the user location valus.
            # last_word_in_user_location_string = location_string.rsplit(",")[-1].strip()
            # # check if the phrase is part of the known counties phrases which were add manually
            # # in case that ot exists, gives the user location parameters the known values
            # if last_word_in_user_location_string in conf.KNOWN_COUNTRIES:
            #     self._country, self._continent = conf.KNOWN_COUNTRIES[last_word_in_user_location_string]
            #
            # else:
            #     # query in the table of the database that includes phrases in the websites the accepted as describing
            #     # users location, if it finds value in the DB, allocates these values to the user location and skipping
            #     # the api request part
            #     location_row = session.query(Location) \
            #         .join(Stack_Exchange_Location) \
            #         .filter(Stack_Exchange_Location.website_location == last_word_in_user_location_string) \
            #         .first()
            #
            #     if location_row:
            #         self._country, self._continent = location_row.country, location_row.continent
            #
            #     else:
            #         # In this part, no value founded to the counry in our current resources. Thus, implementing function
            #         # that requests location from api
            #         self._country, self._continent = self.get_country_and_continent_from_location(location_string)
            #         # if finds country (user have valid country description), checks if it is valid to add to the
            #         # known phrases (it is title word (we ignore state names such as CA - could be appropriate to
            #         # multiple countries), and it is not part of the phrases we manually
            #         if (self._country) \
            #                 and (last_word_in_user_location_string not in conf.IGNORE_NAME_IN_LOCATION_CACHE_TABLE) \
            #                 and (last_word_in_user_location_string.istitle()):
            #             self._new_location_name_in_website = last_word_in_user_location_string

        for index in basic_info_as_list:
            if 'Member for' in index.text:
                self._member_since = datetime.strptime(index.find('span')['title'][:-1], '%Y-%m-%d %H:%M:%S')
            if 'profile views' in index.text:
                self._profile_views = int(index.text.strip().split()[0].replace(",", ""))
                break

    # def get_country_and_continent_from_location(self, loc_string):
    #     """
    #     finds user location (country and continent) from his location description
    #     because the api sometimes is unavailable (for several reasons) the function works in this form:
    #     1. try first time - in a case of a failure, log a warning and try again (with sleep time for not immediately
    #     try again (could lead to problem again)
    #     2. if there is a second error, log an ERROR message with the user details for scraping his location individually
    #     later (this feature will be completed in milestone 3)
    #     :param loc_string: user location description (str)
    #     :return: country and continent (str, str) or (None, None)
    #     """
    #     country, continent = None, None  # initiate the returned variables
    #     if not re.search(conf.GMT_REGEX, loc_string):  # handle "GMT {-8:00}" - time zone location inputted
    #         try:
    #             country, continent = UserScraper.geolocator_process(loc_string)
    #         except GeocoderUnavailable:
    #             logger_UserScraper.warning(conf.GeocoderUnavailable_WARNING_STRING.format(self._name,
    #                                                                                       self._website, loc_string))
    #
    #             time.sleep(conf.SLEEP_TIME_FOR_LOCATIONS_API)
    #             try:
    #                 country, continent = UserScraper.geolocator_process(loc_string)
    #             except GeocoderUnavailable:
    #                 logger_UserScraper.error(conf.GeocoderUnavailable_ERROR_STRING.format(self._name,
    #                                                                                       self._website, loc_string))
    #
    #     return country, continent
    #
    # @staticmethod
    # def geolocator_process(loc_string):
    #     """
    # user location will be determent by the geo-locator library. it receives the users location as written in the web
    # converts it to  latitude and longitude then it will be called again to convert the latitude and longitude to
    # a global unique name of country and continent.
    #     """
    #     country, continent = None, None  # initiate the returned variables
    #     loc = Website.geolocator.geocode(loc_string)
    #     if loc:
    #         lat, lon = loc.latitude, loc.longitude
    #         time.sleep(conf.SLEEP_TIME_FOR_LOCATIONS_API)
    #         new_loc = Website.geolocator.reverse([lat, lon], language='en')
    #         try:
    #             country = new_loc.raw["address"]["country"]
    #             continent = conf.continents_dict[country_alpha2_to_continent_code(
    #                 country_name_to_country_alpha2(country))]
    #
    #         except KeyError:
    #             if country in conf.KNOWN_COUNTRIES:
    #                 country, continent = conf.KNOWN_COUNTRIES[country]
    #         finally:
    #             time.sleep(conf.SLEEP_TIME_FOR_LOCATIONS_API)
    #     return country, continent

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
            self._people_reached = int(float(people_reached[:-1]) * (10 ** conf.magnitude_dict[people_reached[-1]]))

    def reputation_hist(self):
        """
        user reputation for years: [2017, 2018, 2019 ,2020]
        will evaluate years only for users registered before 2017
        in case that users is registered more then 4 years ago and there is a problem,
        log a warning for checking manually the issue
        :return: None
        """
        if self._member_since < threshold_date:
            soup_activity = UserScraper.create_soup(self._url + "?tab=topactivity")
            source_data = soup_activity.find("div", {"id": "top-cards"}).contents[3].string
            numbers = re.search(conf.REPUTATION_REGEX, source_data).group(1)
            reputation_numbers = ast.literal_eval(numbers)
            try:
                self._reputation_2017 = reputation_numbers[year_indexes[0]]
                self._reputation_2018 = reputation_numbers[year_indexes[1]]
                self._reputation_2019 = reputation_numbers[year_indexes[2]]
                self._reputation_2020 = reputation_numbers[year_indexes[3]]
            except IndexError:
                logger_UserScraper.warning(f"website {self._website} user {self._name}"
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

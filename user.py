from website import Website
from ORM import WebsitesT, UserT, User_Tags, TagsT, Reputation, \
                Location, engine, Base, session, Stack_Exchange_Location
from datetime import datetime, timedelta
import json
import re
import ast
import time
from logger import Logger
from geopy.exc import GeocoderUnavailable  #:TODO: manage maybe another exceptions here
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2

logger_user = Logger("user").logger

# get constants from json file (which contains all the Constants)
JSON_FILE_NAME = "mining_constants.json"

with open(JSON_FILE_NAME, "r") as json_file:
    constants_data = json.load(json_file)

magnitude_dict = constants_data["constants"]["MAGNITUDE_MAP"]
REPUTATION_YEARS = constants_data["constants"]["REPUTATION_YEARS"]
continents_dict = constants_data["constants"]["CONTINENTS_MAP"]

now = datetime.now()
threshold_date = now - timedelta(days=4 * 365)
year_indexes = [-(now - datetime(year, 1, 1)).days for year in REPUTATION_YEARS]

REPUTATION_REGEX = re.compile(r"var\sgraphData\s=\s(\[\S+\])")


class User(Website, dict):
    """
    General: Class User gets the users url, scrapes all the information into class variables
    inheritance: "create_soup" from class Website.

                The idea behind dictionary inheritance is to allow the developer to protect the data that can be
                scraped into the database and prevent a scenario where the data is added / subtracted from the user.
                This feature is ready to deploy on the product demand.

                In addition, dictionary methods allows us to store the data in a structure that can be transfer
                to a Jason file without creating any additional variables. – O(n) time and space complexity.

                for clarity reasons all class variables are being declared at the top of the class. All class
                variables who needs more than one line to scrap the information are being scraped in separate blocks

    milestone 2:
    because we've changed the __init__ method to be shorter - all scraping info that is longer than one line
    will became a method of class user and will be called from main.
    also, soup will become a user feature so other methods will be able to use it and we'll not need to create
    soup from main and send it to all the methods.


    """

    num_user_dict = {}


    def __init__(self, website_name, url, FIRST_INSTANCE_TO_SCRAP):
        dict.__init__(self)
        Website.__init__(self, website_name)

        self._soup = Website.create_soup(url)

        User.num_user_dict[self._website_name] = User.num_user_dict.get(self._website_name,
                                                                        FIRST_INSTANCE_TO_SCRAP - 1) + 1
        self._rank = User.num_user_dict[self._website_name]
        self._name = self._soup.find("div", {"class": "grid--cell fw-bold"}).text
        self._member_since = None
        self._profile_views = 0
        self._answers = None
        self._people_reached = None
        self._country = None  # not all users have a valid location in profile - must keep as default none
        self._continent = None  # same as line above
        self._new_location_name_in_website = None  # add this value as a flag for adding record to Stack_Exchange_Location table
        self._reputation_now = int(
            self._soup.find("div", {"class": "grid--cell fs-title fc-dark"}).text.replace(',', '')) #:TODO - cluster this with the other reputations
        self._reputation_2017 = None
        self._reputation_2018 = None
        self._reputation_2019 = None
        self._reputation_2020 = None
        self._tags = self.create_tags() # TODO: Inbar - I think we can use this way for all the variables


    def personal_info(self):
        """
        Defines users name and users location
        not all users have a location - thus location will stay None type
        """
        basic_info_scope = self._soup.find("ul", {"class": "list-reset grid gs8 gsy fd-column fc-medium"})
        basic_info_as_list = basic_info_scope.find_all_next("div", {"class": "grid gs8 gsx ai-center"})
        if basic_info_as_list[0].find('svg', {'aria-hidden': 'true', 'class': 'svg-icon iconLocation'}):
            location_string = basic_info_as_list[0].text.strip()

            last_word_in_user_location_string = location_string.rsplit(",")[-1].strip()
            check_existing_location = session.query(Stack_Exchange_Location.location_id)\
                                             .filter(Stack_Exchange_Location.website_location == last_word_in_user_location_string.title())\
                                             .first() #: TODO - merge with next query

            if check_existing_location: #: TODO: We should create a list of problematic words that occured (like: University (located to UK)) and write the in the json file
                self._country, self._continent = session.query(Location.country, Location.continent)\
                                                        .join(Stack_Exchange_Location)\
                                                        .filter(Stack_Exchange_Location.location_id == check_existing_location[0])\
                                                        .first()
            else:
                self._country, self._continent = self.get_country_and_continent_from_location(location_string)
                if self._country and last_word_in_user_location_string.istitle():
                    self._new_location_name_in_website = last_word_in_user_location_string

        for i in basic_info_as_list:
            if 'Member for' in i.text:
                self._member_since = datetime.strptime(i.find('span')['title'][:-1], '%Y-%m-%d %H:%M:%S')
            if 'profile views' in i.text:
                self._profile_views = int(i.text.strip().split()[0].replace(",", ""))
                break

    def get_country_and_continent_from_location(self, loc_string):
        country, continent = None, None  # initiate the returned variables
        if not re.search(r"GMT\s[+-]\d", loc_string):  # handle "GMT {-8:00}" - time zone location inputted
            try:
                country, continent = User.geolocator_process(loc_string)
            except GeocoderUnavailable:
                logger_user.warning(f"problem! user {self._name} rank {self._rank} and website {self._website_name}"
                      f" with address {loc_string}, did not scrapped, try to run again")
                time.sleep(1.5) # :TODO - add to json
                try:
                    country, continent = User.geolocator_process(loc_string)
                except GeocoderUnavailable:
                    logger_user.error(f"Failed! user {self._name} rank {self._rank} and website {self._website_name}"
                          f" with address {loc_string}, did not scrapped") # : TODO: add the url of the users, after milestone 2 - update these locations

        return country, continent

    @staticmethod
    def geolocator_process(loc_string):
        country, continent = None, None  # initiate the returned variables
        loc = Website.geolocator.geocode(loc_string)
        if loc:
            lat, lon = loc.latitude, loc.longitude
            time.sleep(1.5)
            new_loc = Website.geolocator.reverse([lat, lon], language='en')
            try:
                country = new_loc.raw["address"]["country"]
                continent = continents_dict[country_alpha2_to_continent_code(
                    country_name_to_country_alpha2(country))]

            except KeyError:  #: TODO: move to json file
                if country == "The Netherlands":
                    country = "Netherlands"
                    continent = "Europe"
            finally:
                time.sleep(1.1)  # :TODO: calculate time to sleep
        return country, continent


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
            self._people_reached = int(float(people_reached[:-1]) * (10 ** magnitude_dict[people_reached[-1]]))

    def reputation_hist(self, url):
        """
        user reputation for years: [2017, 2018, 2019 ,2020]
         will evaluate years only for users registered before 2017
        """
        if self._member_since < threshold_date:
            soup_activity = self.create_soup(url + "?tab=topactivity")
            source_data = soup_activity.find("div", {"id": "top-cards"}).contents[3].string
            numbers = re.search(REPUTATION_REGEX, source_data).group(1)
            reputation_numbers = ast.literal_eval(numbers)
            try:
                self._reputation_2017 = reputation_numbers[year_indexes[0]]
                self._reputation_2018 = reputation_numbers[year_indexes[1]]
                self._reputation_2019 = reputation_numbers[year_indexes[2]]
                self._reputation_2020 = reputation_numbers[year_indexes[3]]
            except IndexError:
                logger_user.warning(f"website {self._website_name} rank {self._rank}"
                      f" user {self._name} is member since more than 4 years but have reputation plot of month")

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
            for i, tag in enumerate(all_tags_info.find_all_next('div', {"class": "grid jc-end ml-auto"})):
                tags[i].append(int(tag.text.replace("\n", " ").split()[1].replace(",", "")))
                tags[i].append(int(tag.text.replace("\n", " ").split()[3].replace(",", "")))
            return tags

    def scrap_info(self, link):
        """
        calls to all the methods of user to scrap information.
        created to decrees amount of lines in main file.
        reputation_hist method most be last - so self['member_since'] will get a value.
        """
        self.professional_info()
        self.personal_info()
        self.reputation_hist(link)

    def get_user_info(self):
        return {
            'rank': self._rank,
            'name': self._name,
            'member_since': self._member_since,
            'profile_views': self._profile_views,
            'answers': self._answers,
            'people_reached': self._people_reached,
        }

    def get_location(self):
        return {
            'country': self._country,
            'continent': self._continent
        }

    def get_reputation(self):
        return {
            'reputation_2017': self._reputation_2017,
            'reputation_2018': self._reputation_2018,
            'reputation_2019': self._reputation_2019,
            'reputation_2020': self._reputation_2020,
            'reputation_now': self._reputation_now
                }

    def insert_user(self):

        # list of variables that we'll add and commit in one shot commit
        commit_list = []
        web = session.query(WebsitesT).filter(WebsitesT.name == self._website_name).first()
        loc = session.query(Location).filter(Location.country == self._country).first()
        if loc is None:
            loc = Location(**self.get_location())

        if self._new_location_name_in_website:
            stack_exchange_loc = Stack_Exchange_Location(location=loc, website_location=self._new_location_name_in_website)
            commit_list.append(stack_exchange_loc)

        # create new user entrance in table and commit it to create PK for user.
        user = UserT(location=loc, website_id=web.id, **self.get_user_info())
        session.add(user)
        session.commit()

        # create user Reputation and connects it to the user.
        rep = Reputation(user_id=user.id, **self.get_reputation())
        commit_list.extend([loc, rep])
        for tag in self._tags:
            new_tag = session.query(TagsT).filter(TagsT.name == tag[0]).first()
            if new_tag is None:
                new_tag = TagsT(name=tag[0])
                commit_list.append(new_tag)
            ass = User_Tags(score=tag[1], posts=tag[2])
            ass.user_id = user.id
            new_tag.users.append(ass)
            commit_list.append(ass)
        # add all new user info to relevant tables and commits it
        session.add_all(commit_list)
        session.commit()



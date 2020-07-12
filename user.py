"""
milestone 2 summery:
    the big change that has been done in this class is the remove of inheritance from dict methods.
    this change came because of 2 main reasons:

        1. the main purpose of inheritance dict methods was to save time and to be able to send the information
        in single instance without creating a new data structure.
        in these mile stone we realized that we don't need all the information about the user at once. thus we
        need to "slice and dice" user to different data sets. to do so we will have to keep a strict order in the code
        of the class variables.
        in our opinion this is very(!) risky and not worth the 1 ms that was saved in creating a new data set.
        memory wise - the data set id deleted after use so it's also negligible

        2. the second purpose of inheritance dict methods was to make sure that no one is changing the class variables.
        in a case of adding class variables after X users that were scrapped, a "hole" will be created in the data base
        and the X first users won't have the added info.
        because we'll be the only two programmers with excess to code, the fact that the data base is not in big scale
        and that we decided not to try and catch programmer error (just user error) - we decided not to
        inheritance dict methods.


    because we've changed the __init__ method to be shorter - all scraping info that is longer than one line
    will became a method of class user and will be called for.

    also, soup will become a user feature so other methods will be able to use it and we'll not need to create
    soup from main and send it to all the methods.

    user location will be determent by the geo-locator library. it receives the users location as written in the web
    converts it to  latitude and longitude then it will be called again to convert the  latitude and longitude to
    a global unique name of country and continent. using a dict that is located in the json file the continents name
    will be converted to a full name ('NA': 'North America').
    HOWEVER, between every request we need to set a sleep factor of 1 sec - thus every country takes more than 2 sec.
    ITS A LOT OF TIME.

    to solve this problem we've created a new table (Stack_Exchange_Location) that store the name of the country from
    the website and connect it ,by a one to many relationship, to the location table. now for every user we will first
    check for a match in the Stack_Exchange_Location table with his country in the website. match - the user will form
    a connection to the location in the Location table. no match - will use geo-locator.

    insert the user to the data base with SQLAlchemy using ORM.
    ORM lets us define tables and relationship using Python classes.
    also provides a system to query and manipulate the database using object-oriented code instead of writing SQL.

    to make as less commits as possible we've created a commit_list that collects all the new instance throughout
    the function and then adds and commits them at once.
    first we get the web site id from the data and check if the user location exists in the data base - if not will
    create a new Location instance.

    before creating any new instances, we must create a UserT instance and commit it to the data base. this way a
    user with a user.id will be created and we will be able to connect it to all other user information in the
    different instances.

    then we'll create an Reputation instance - will happen for every user.
    last but not least will be the tag instance - will check if Tag instance already exist - if not - will create
    new one. if exists would get that instance. then will form a connection between the Tags and a new User_Tags
    instance

    To avid duplication of users in the data base a unique set of ('name', 'rank', 'website_id') was declared.
    also location, tags and website name was declared as unique.
    duo to the above - before every commit an exception of IntegrityError will be raise to avid crash.
    in a case of duplication 2 action will tack place:
    1. if the user was committed - the user will be deleted from the data base.
    2. the user url will be logged in the logger_not_scrapped to check what happened and scrape him latter if needed
     also a warning will be logged in the logger_user

"""

from website import Website
from ORM import WebsitesT, UserT, User_Tags, TagsT, Reputation, \
    Location, session, Stack_Exchange_Location
from datetime import datetime, timedelta
import re
import ast
import time
from sqlalchemy import exc
from logger import Logger
from geopy.exc import GeocoderUnavailable
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
import conf

logger_user = Logger("user").logger
logger_not_scrapped = Logger("not_scrapped").logger


# find indexes of 1 of January in the years searched for reputation. get threshold for it (4 years from today)
now = datetime.now()
threshold_date = now - timedelta(days=4 * 365)
year_indexes = [-(now - datetime(year, 1, 1)).days for year in conf.REPUTATION_YEARS]


class User(Website):
    """
    General: Class User gets the users url, scrapes all the information into class variables
    inheritance: "create_soup" from class Website.

    for clarity reasons all class variables are being declared at the top of the class. All class
    variables who needs more than one line to scrap the information are being scraped in separate blocks
    The class contains as well the methods for adding new rows into the database tables, from the data of the
    instance of the relevant user
    """

    # class variable that contains the current rank of the users for each website, i.e : {"stackoverflow": 5,
    #                                                                                    "another website":2}
    num_user_dict = {}

    def __init__(self, website_name, url, first_instance_to_scrap):
        Website.__init__(self, website_name)

        self._url = url
        self._soup = Website.create_soup(url)

        User.num_user_dict[self._website_name] = User.num_user_dict.get(self._website_name,
                                                                        first_instance_to_scrap - 1) + 1
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
            self._soup.find("div", {"class": "grid--cell fs-title fc-dark"}).text.replace(',',
                                                                                          ''))
        self._reputation_2017 = None
        self._reputation_2018 = None
        self._reputation_2019 = None
        self._reputation_2020 = None
        self._tags = self.create_tags()

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
            # finds last phrase after comma of the user location valus.
            last_word_in_user_location_string = location_string.rsplit(",")[-1].strip()
            # check if the phrase is part of the known counties phrases which were add manually
            # in case that ot exists, gives the user location parameters the known values
            if last_word_in_user_location_string in conf.KNOWN_COUNTRIES:
                self._country, self._continent = conf.KNOWN_COUNTRIES[last_word_in_user_location_string]

            else:
                # query in the table of the database that includes phrases in the websites the accepted as describing
                # users location, if it finds value in the DB, allocates these values to the user location and skipping
                # the api request part
                location_row = session.query(Location) \
                    .join(Stack_Exchange_Location) \
                    .filter(Stack_Exchange_Location.website_location == last_word_in_user_location_string) \
                    .first()

                if location_row:
                    self._country, self._continent = location_row.country, location_row.continent

                else:
                    # In this part, no value founded to the counry in our current resources. Thus, implementing function
                    # that requests location from api
                    self._country, self._continent = self.get_country_and_continent_from_location(location_string)
                    # if finds country (user have valid country description), checks if it is valid to add to the
                    # known phrases (it is title word (we ignore state names such as CA - could be appropriate to
                    # multiple countries), and it is not part of the phrases we manually
                    if (self._country) \
                            and (last_word_in_user_location_string not in conf.IGNORE_NAME_IN_LOCATION_CACHE_TABLE) \
                            and (last_word_in_user_location_string.istitle()):
                        self._new_location_name_in_website = last_word_in_user_location_string

        for index in basic_info_as_list:
            if 'Member for' in index.text:
                self._member_since = datetime.strptime(index.find('span')['title'][:-1], '%Y-%m-%d %H:%M:%S')
            if 'profile views' in index.text:
                self._profile_views = int(index.text.strip().split()[0].replace(",", ""))
                break

    def get_country_and_continent_from_location(self, loc_string):
        """
        finds user location (country and continent) from his location description
        because the api sometimes is unavailable (for several reasons) the function works in this form:
        1. try first time - in a case of a failure, log a warning and try again (with sleep time for not immediately
        try again (could lead to problem again)
        2. if there is a second error, log an ERROR message with the user details for scraping his location individually
        later (this feature will be completed in milestone 3)
        :param loc_string: user location description (str)
        :return: country and continent (str, str) or (None, None)
        """
        country, continent = None, None  # initiate the returned variables
        if not re.search(conf.GMT_REGEX, loc_string):  # handle "GMT {-8:00}" - time zone location inputted
            try:
                country, continent = User.geolocator_process(loc_string)
            except GeocoderUnavailable:
                logger_user.warning(conf.GeocoderUnavailable_WARNING_STRING.format(self._name, self._rank,
                                                                              self._website_name, loc_string))

                time.sleep(conf.SLEEP_TIME_FOR_LOCATIONS_API)
                try:
                    country, continent = User.geolocator_process(loc_string)
                except GeocoderUnavailable:
                    logger_user.error(conf.GeocoderUnavailable_ERROR_STRING.format(self._name, self._rank,
                                                                              self._website_name,
                                                                              loc_string))

        return country, continent

    @staticmethod
    def geolocator_process(loc_string):
        """
    user location will be determent by the geo-locator library. it receives the users location as written in the web
    converts it to  latitude and longitude then it will be called again to convert the latitude and longitude to
    a global unique name of country and continent.
        """
        country, continent = None, None  # initiate the returned variables
        loc = Website.geolocator.geocode(loc_string)
        if loc:
            lat, lon = loc.latitude, loc.longitude
            time.sleep(conf.SLEEP_TIME_FOR_LOCATIONS_API)
            new_loc = Website.geolocator.reverse([lat, lon], language='en')
            try:
                country = new_loc.raw["address"]["country"]
                continent = conf.continents_dict[country_alpha2_to_continent_code(
                    country_name_to_country_alpha2(country))]

            except KeyError:
                if country in conf.KNOWN_COUNTRIES:
                    country, continent = conf.KNOWN_COUNTRIES[country]
            finally:
                time.sleep(conf.SLEEP_TIME_FOR_LOCATIONS_API)
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
            soup_activity = self.create_soup(self._url + "?tab=topactivity")
            source_data = soup_activity.find("div", {"id": "top-cards"}).contents[3].string
            numbers = re.search(conf.REPUTATION_REGEX, source_data).group(1)
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
            for index, tag in enumerate(all_tags_info.find_all_next('div', {"class": "grid jc-end ml-auto"})):
                tags[index].append(int(tag.text.replace("\n", " ").split()[1].replace(",", "")))
                tags[index].append(int(tag.text.replace("\n", " ").split()[3].replace(",", "")))
            return tags

    def scrap_info(self):
        """
        calls to all the methods of user to scrap information.
        created to decrees amount of lines in main file.
        reputation_hist method most be last - so self['member_since'] will get a value.
        """
        self.professional_info()
        self.personal_info()
        self.reputation_hist()

    def get_user_info(self):
        """
        getter method to create a UserT instance.
        return a dict with all self information that relevant to create UserT.
        """
        return {
            'rank': self._rank,
            'name': self._name,
            'member_since': self._member_since,
            'profile_views': self._profile_views,
            'answers': self._answers,
            'people_reached': self._people_reached,
        }

    def get_location(self):
        """
        getter method to create a Location instance.
        return a dict with all self information that relevant to create Location.
        """
        return {
            'country': self._country,
            'continent': self._continent
        }

    def get_reputation(self):
        """
        getter method to create a Reputation instance.
        return a dict with all self information that relevant to create Reputation.
        Reputation
        """
        return {
            'reputation_2017': self._reputation_2017,
            'reputation_2018': self._reputation_2018,
            'reputation_2019': self._reputation_2019,
            'reputation_2020': self._reputation_2020,
            'reputation_now': self._reputation_now
        }

    # noinspection PyUnresolvedReferences
    def insert_user(self):
        """
    insert the user to the data base with SQLAlchemy using ORM.
    ORM lets us define tables and relationship using Python classes.
    also provides a system to query and manipulate the database using object-oriented code instead of writing SQL.

    to make as less commits as possible we've created a commit_list that collects all the new instance throughout
    the function and then adds and commits them at once.
    first we get the web site id from the data and check if the user location exists in the data base - if not will
    create a new Location instance.

    before creating any new instances, we must create a UserT instance and commit it to the data base. this way a
    user with a user.id will be created and we will be able to connect it to all other user information in the
    different instances.

    then we'll create an Reputation instance - will happen for every user.
    last but not least will be the tag instance - will check if Tag instance already exist - if not - will create
    new one. if exists would get that instance. then will form a connection between the Tags and a new User_Tags
    instance

    To avoid duplication of users in the data base a unique set of ('name', 'rank', 'website_id') was declared.
    also location, tags and website name was declared as unique.
    duo to the above - before every commit an exception of IntegrityError will be raise to avid crash.
    in a case of duplication 2 action will tack place:
    1. if the user was committed - the user will be deleted from the data base.
    2. the user url will be logged in the logger_not_scrapped to check what happened and scrape him latter if needed
     also a warning will be logged in the logger_user
        """

        # list of variables that we'll add and commit in one shot commit
        commit_list = []
        web = session.query(WebsitesT).filter(WebsitesT.name == self._website_name).first()
        loc = session.query(Location).filter(Location.country == self._country).first()
        if loc is None:
            loc = Location(**self.get_location())

        if self._new_location_name_in_website:
            stack_exchange_loc = Stack_Exchange_Location(location=loc,
                                                         website_location=self._new_location_name_in_website)
            commit_list.append(stack_exchange_loc)

        # create new user entrance in table and commit it to create PK for user.
        user = UserT(location=loc, website_id=web.id, **self.get_user_info())

        # noinspection PyUnresolvedReferences
        try:
            session.add(user)
            session.commit()

        except exc.IntegrityError:
            session.rollback()
            # log the problem in user logger, Can't print user name with spacial/ unknown characters
            logger_user.warning(f'IntegrityError: "Duplicate entry for key users.name ranked')

            # insert user information to not scrapped users logger, Can't print user name with unknown characters
            logger_not_scrapped.error(f'IntegrityError: "Duplicate entry for key users.name ranked {self._rank} at'
                                f' website {self._website_name} with url: {self._url}" ')
            return None

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
        try:
            session.add_all(commit_list)
            session.commit()

        # duplicat values in DB - can't commit new information
        except exc.IntegrityError as e:
            session.rollback()
            logger_user.warning(e.orig)

            # delete user from data base
            user = session.query(UserT).filter(UserT.name == self._name).first()
            session.delete(user)
            session.commit()

            # insert user information to not scrapped users logger
            logger_not_scrapped.error(e.orig)
            logger_not_scrapped.error(f'{self._name} ranked {self._rank} at'
                                f' website {self._website_name} with url: {self._url}" was not scraped because'
                                f'of IntegrityError in second commit')
            return None

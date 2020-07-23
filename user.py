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

from ORM import WebsitesT, UserT, User_Tags, TagsT, Reputation, \
    Location, session, Stack_Exchange_Location
from datetime import datetime, timedelta
from sqlalchemy import exc
from logger import Logger

import conf
from user_scraper import UserScraper

logger_user = Logger("user").logger
logger_not_scrapped = Logger("not_scrapped").logger

# find indexes of 1 of January in the years searched for reputation. get threshold for it (4 years from today)
now = datetime.now()
threshold_date = now - timedelta(days=4 * 365)
year_indexes = [-(now - datetime(year, 1, 1)).days for year in conf.REPUTATION_YEARS]


class User(UserScraper):
    """
    General: Class User gets the users url, scrapes all the information into class variables
    inheritance: "create_soup" from class Website.

    for clarity reasons all class variables are being declared at the top of the class. All class
    variables who needs more than one line to scrap the information are being scraped in separate blocks
    The class contains as well the methods for adding new rows into the database tables, from the data of the
    instance of the relevant user
    """

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

    def commit_user_to_DB(self, user):
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

        return True

    def commit_user_info_to_DB(self, commit_list):
        # add all new user info to relevant tables and commits it
        try:
            session.add_all(commit_list)
            session.commit()
            return True

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

    def insert_user_to_DB(self):
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
        web = session.query(WebsitesT).filter(
            WebsitesT.name == self._website_name).first()
        loc = session.query(Location).filter(Location.country == self._country).first()
        if loc is None:
            loc = Location(**self.get_location())
            commit_list.append(loc)

        if self._new_location_name_in_website:
            stack_exchange_loc = Stack_Exchange_Location(location=loc,
                                                         website_location=self._new_location_name_in_website)
            commit_list.append(stack_exchange_loc)

        # create new user entrance in table and commit it to create PK for user.
        user = UserT(location=loc, website_id=web.id, **self.get_user_info())

        # commit user to data - if didn't seceded will return None
        if not User.commit_user_to_DB(self, user):
            return None

        # create user Reputation and connects it to the user.
        rep = Reputation(user_id=user.id, **self.get_reputation())
        commit_list.append(rep)

        # create user Reputation and connects it to UserT and User_Tags (many-many relationship)
        if self._tags:
            for tag in self._tags:
                new_tag = session.query(TagsT).filter(TagsT.name == tag[0]).first()
                if new_tag is None:
                    new_tag = TagsT(name=tag[0])
                    commit_list.append(new_tag)
                ass = User_Tags(score=tag[1], posts=tag[2])
                ass.user_id = user.id
                new_tag.users.append(ass)
                commit_list.append(ass)

        # commit all user info to DB - if didn't seceded will return None
        User.commit_user_info_to_DB(self, commit_list)

"""
class User:
1. create dictionaries for each ORM table
2. commits data into the database
"""

from src import logger, config, session
from src.ORM import WebsitesT, UserT, User_Tags, TagsT, Reputation, \
    Location, Stack_Exchange_Location
from sqlalchemy import exc
from src.user_scraper import UserScraper


class User(UserScraper):
    """
    General: Class User gets the users url, scrapes all the information into class variables
    inheritance: "create_soup" from class Website.

    for clarity reasons all class variables are being declared at the top of the class. All class
    variables who needs more than one line to scrap the information are being scraped in separate blocks
    The class contains as well the methods for adding new rows into the database tables, from the data of the
    instance of the relevant user
    """

    @property
    def user_info(self):
        """
        property of user general data for table UserT
        """
        return {
            'rank': self._rank,
            'name': config.ENCODE_REGEX.search(str(self._name.encode('utf-8', 'ignore'))).group(2),
            'member_since': self._member_since,
            'profile_views': self._profile_views,
            'answers': self._answers,
            'people_reached': self._people_reached,
        }

    @property
    def location(self):
        """
        property of user location data
        """
        return {'country': self._country, 'continent': self._continent}

    @property
    def reputation(self):
        """
        property of user reputation data
        """
        return {**self._reputation_hist, 'reputation_now': self._reputation_now}

    def commit_user_to_DB(self, user):
        try:
            session.add(user)
            session.commit()

        except exc.IntegrityError as e:
            logger.error(e)
            session.rollback()
            # # log the problem in user logger, Can't print user name with spacial/ unknown characters
            # logger.warning(f'IntegrityError: "Duplicate entry for key users.name ranked')
            #
            # # insert user information to not scrapped users logger, Can't print user name with unknown characters
            # logger.error(f'IntegrityError: "Duplicate entry for key users.name ranked {self._rank} at'
            #                           f' website {self._website_name} with url: {self._url}" ')
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
            logger.warning(e.orig)

            # delete user from data base
            user = session.query(UserT).filter(UserT.name == self._name).first()
            session.delete(user)
            session.commit()

            # insert user information to not scrapped users logger
            logger.error(e.orig)
            logger.error(f'{self._name} ranked {self._rank} at'
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
            loc = Location(**self.location)
            commit_list.append(loc)

        if self._new_location_name_in_website:
            stack_exchange_loc = Stack_Exchange_Location(location=loc, website_location=config.ENCODE_REGEX.search(
                str(self._new_location_name_in_website.encode('utf-8', 'ignore'))).group(2))

            commit_list.append(stack_exchange_loc)

        # create new user entrance in table and commit it to create PK for user.
        user = UserT(location=loc, website_id=web.id, **self.user_info)

        # commit user to data - if didn't seceded will return None
        if not User.commit_user_to_DB(self, user):
            return None

        # create user Reputation and connects it to the user.
        rep = Reputation(user_id=user.id, **self.reputation)
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
        # User.commit_user_info_to_DB(self, commit_list)
        session.add_all(commit_list)
        session.commit()

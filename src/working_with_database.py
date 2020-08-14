"""
This file manages most of the connections with the database. The file contain the following functions:
create_database() - creates the DB  (if the requested one does not exist yet)
initiate_database() - It initiates a database (generates the tables in the database (creates them if they not exist)
create_table_website - create the website table and add entities according to the new website to scrap
find_last_user_scrapped - finds the last users to scrap from the table
"""

from src import logger, Base, config
from sqlalchemy import create_engine, exc
from src.ORM import WebsitesT, UserT, User_Tags, TagsT, Reputation, \
    Location, Stack_Exchange_Location
import pymysql
from sqlalchemy import func
from sqlalchemy.orm import Session


class Database:

    def __init__(self):
        connection = pymysql.connect(host='localhost', user=config.USER_NAME, password=config.PASSWORD)
        self._cursor_instance = connection.cursor()

        engine = create_engine(f"{config.SQL_EXTENSION}+{config.PYTHON_DBAPI}://{config.USER_NAME}:"
                               f"{config.PASSWORD}@localhost/{config.DB_NAME}")

        # wraps the database connection and transaction.
        # starts as the Session starts and remain open until the Session closed
        self._session = Session(bind=engine)

        # generates the tables in the database (creates them if they not exist))
        self.create_database()

        # Drops all tables. del when DB is ready
        # Base.metadata.drop_all(engine)

        # creates all tables - if exists won't do anything
        Base.metadata.create_all(engine)


    def create_database(self):
        """
        creates the DB  (if not exist yet - if it is, continues).
        checks if connection to the database is valid
        """
        # SQL Statement to check if DB exist
        sql_statement = config.CHECK_DB + config.DB_NAME + '"'

        if self._cursor_instance.execute(sql_statement) == 0:
            # SQL Statement to create a database
            sql_statement = "CREATE DATABASE " + config.DB_NAME
            try:
                # Execute the create database SQL statement through the cursor instance
                self._cursor_instance.execute(sql_statement)
            except pymysql.err.ProgrammingError:
                logger.error(config.DB_NAME_NOT_VALID.format(config.DB_NAME))
                exit()


    def insert_website_to_DB(self, website_dict):
        """
        enters data of website into DB. if the entity already exists, update relevant data
        :param website_dict: parameters of website table (dict)
        """

        web = self._session.query(WebsitesT).filter(WebsitesT.name == website_dict["name"]).first()

        if web:
            web.total_users = website_dict["total_users"]
            web.total_answers = website_dict["total_answers"]
            web.total_questions = website_dict["total_questions"]
            web.answers_per_minute = website_dict["answers_per_minute"]
            web.questions_per_minute = website_dict["questions_per_minute"]

        else:
            web = WebsitesT(**website_dict)
        self._session.add(web)
        self._session.commit()


    def find_last_user_scrapped(self, website_name):
        """
        gets the website name that is being scraped
        checks in the user table what is the last rank that was scraped based on website id
         returns value + 1 as the instance to first scrap. in a case that no records have been
         scrapped, return 1.
        """
        web = self._session.query(WebsitesT).filter(WebsitesT.name == website_name).first()

        try:
            last_scraped = self._session.query(func.max(UserT.rank)).filter(UserT.website_id == web.id).scalar()
            return last_scraped + 1
        except TypeError:
            return 1
        except AttributeError:
            return 1


    def query_location(self, last_word_in_user_location_string):
        location_row = self._session.query(Location) \
            .join(Stack_Exchange_Location) \
            .filter(Stack_Exchange_Location.website_location == last_word_in_user_location_string) \
            .first()
        return location_row


    def commit_user_to_DB(self, user_table):
        try:
            self._session.add(user_table)
            self._session.commit()

        except exc.IntegrityError as e:
            logger.error(e)
            self._session.rollback()
            # # log the problem in user logger, Can't print user name with spacial/ unknown characters
            # logger.warning(f'IntegrityError: "Duplicate entry for key users.name ranked')
            #
            # # insert user information to not scrapped users logger, Can't print user name with unknown characters
            # logger.error(f'IntegrityError: "Duplicate entry for key users.name ranked {self._rank} at'
            #                           f' website {self._website_name} with url: {self._url}" ')
            return None
        return True


    def insert_user_to_DB(self, user):
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
        web = self._session.query(WebsitesT).filter(
            WebsitesT.name == user._website_name).first()
        loc = self._session.query(Location).filter(Location.country == user._country).first()
        if loc is None:
            loc = Location(**user.location)
            commit_list.append(loc)

        if user._new_location_name_in_website:
            stack_exchange_loc = Stack_Exchange_Location(location=loc,
                                                         website_location=user._new_location_name_in_website)
            commit_list.append(stack_exchange_loc)

        # create new user entrance in table and commit it to create PK for user.
        user_table = UserT(location=loc, website_id=web.id, **user.user_info)

        # commit user to data - if didn't seceded will return None
        if not self.commit_user_to_DB(user_table):
            return None

        # create user Reputation and connects it to the user.
        rep = Reputation(user_id=user_table.id, **user.reputation)
        commit_list.append(rep)

        # create user Reputation and connects it to UserT and User_Tags (many-many relationship)
        if user._tags:
            for tag in user._tags:
                new_tag = self._session.query(TagsT).filter(TagsT.name == tag[0]).first()
                if new_tag is None:
                    new_tag = TagsT(name=tag[0])
                    commit_list.append(new_tag)
                ass = User_Tags(score=tag[1], posts=tag[2])
                ass.user_id = user_table.id
                new_tag.users.append(ass)
                commit_list.append(ass)


        self._session.add_all(commit_list)
        self._session.commit()




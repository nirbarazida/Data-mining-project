"""
This file manages most of the connections with the database. The file contain the following functions:
create_database() - creates the DB  (if the requested one does not exist yet)
initiate_database() - It initiates a database (generates the tables in the database (creates them if they not exist)
create_table_website - create the website table and add entities according to the new website to scrap
find_last_user_scrapped - finds the last users to scrap from the table
"""

from ORM import WebsitesT, engine, Base, session,UserT
from command_args import args
import pymysql
from sqlalchemy import func
from logger import Logger
import conf

logger_DB = Logger("working_with_data_base").logger

MIN_LAST_SCRAPED = 0
NUM_USERS_TO_SCRAP = args.num_users
WEBSITE_NAMES = args.web_sites

DB_NAME = args.DB_name


def create_database():
    """
    creates the DB  (if not exist yet - if it is, continues).
    checks if connection to the database is valid
    """
    try:
        connection = pymysql.connect(host='localhost', user=conf.USER_NAME, password=conf.PASSWORD)
    except pymysql.err.OperationalError as err:
        logger_DB.error(conf.CONNECTION_ERROR)
        exit()
    else:
        # Create a cursor object
        try:
            cursor_instance = connection.cursor()
        except pymysql.err.OperationalError:
            logger_DB.error(conf.SERVER_ERROR)
            exit()

        else:
            # SQL Statement to check if DB exist
            sql_statement = conf.CHECK_DB + DB_NAME + '"'

            if cursor_instance.execute(sql_statement) == 0:
                # SQL Statement to create a database
                sql_statement = "CREATE DATABASE " + DB_NAME
                try:
                    # Execute the create database SQL statement through the cursor instance
                    cursor_instance.execute(sql_statement)
                except pymysql.err.ProgrammingError:
                    logger_DB.error(conf.DB_NAME_NOT_VALID.format(DB_NAME))
                    exit()


def initiate_database():
    """
    initiates a database (generates the tables in the database (creates them if they not exist)
    """
    create_database()

    # Drops all tables. del when DB is ready
    Base.metadata.drop_all(engine)

    # creates all tables - if exists won't do anything
    Base.metadata.create_all(engine)

    # create table website for all the websites
    create_table_website(WEBSITE_NAMES)


def create_table_website(web_names):
    """
    get a list of all the websites that the user wants to scrap from
    create new entries in table websites with those names
    """

    # if not engine.dialect.has_table(engine, 'websites'):
    #     logger_DB.error(conf.TABLE_NOT_EXIST)
    #     exit()

    for name in web_names:
        web = session.query(WebsitesT).filter(WebsitesT.name == name).first()
        if web is None:
            logger_DB.info(f"new entity in website table: {web}")
            web = WebsitesT(name=name)
            session.add(web)
            session.commit()



def find_last_user_scrapped(website_name):
    """
    gets the website name that is being scraped
    checks in the user table what is the last rank that was scraped based on website id
     returns value + 1 as the instance to first scrap. in a case that no records have been
     scrapped, return 1.
    """
    web = session.query(WebsitesT).filter(WebsitesT.name == website_name).first()

    last_scraped = session.query(func.max(UserT.rank)).filter(UserT.website_id == web.id).scalar()
    try:
        return last_scraped + 1
    except TypeError:
        return MIN_LAST_SCRAPED + 1

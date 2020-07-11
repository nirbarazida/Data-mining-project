"""
This file manages most of the connections with the database. The file contain the following functions:
create_database() - creates the DB  (if the requested one does not exist yet)
initiate_database() - It initiates a database (generates the tables in the database (creates them if they not exist)
create_table_website - create the website table and add entities according to the new website to scrap
auto_scrap_updates - function for the auto-scrap mode - finds the last users to scrap from the table in start from it
"""

from ORM import WebsitesT, engine, Base, session,UserT
from command_args import args
import os
import pymysql
import json
from sqlalchemy import func


MIN_LAST_SCRAPED = 0
NUM_USERS_TO_SCRAP = args.num_users
WEBSITE_NAMES = args.web_sites

DB_NAME = args.DB_name

JSON_FILE_NAME = "mining_constants.json"
# get constants from json file (which contains all the Constants)

with open(JSON_FILE_NAME, "r") as json_file:
    constants_data = json.load(json_file)

# get authentication values
USER_NAME = os.environ.get(constants_data["constants"]["AUTHENTICATION"]["USER_ENV_NAME"])
PASSWORD = os.environ.get(constants_data["constants"]["AUTHENTICATION"]["PASSWORD_ENV_NAME"])


def create_database():
    """
    creates the DB  (if the requested one does not exist yet).
    checks if connection to the database is valid
    :return:
    """
    try:
        connection = pymysql.connect(host='localhost', user=USER_NAME, password=PASSWORD)
    except pymysql.err.OperationalError as err:
        print('os environ variables are not defined.'
                                           ' for help go to https://www.youtube.com/watch?v=IolxqkL7cD8 ')
        exit()
    else:
        # Create a cursor object
        try:
            cursor_insatnce = connection.cursor()
        except pymysql.err.OperationalError:
            print("couldn't form a connection with server")
            exit()

        else:
            # SQL Statement to check if DB exist
            sql_statement = 'SELECT distinct(SCHEMA_NAME) FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = ' '"' + DB_NAME + '"'

            if cursor_insatnce.execute(sql_statement) == 0:
                # SQL Statement to create a database
                sql_statement = "CREATE DATABASE " + DB_NAME
                try:
                    # Execute the create database SQL statement through the cursor instance
                    cursor_insatnce.execute(sql_statement)
                except pymysql.err.ProgrammingError:
                    print(f"Database name:{DB_NAME} is not valid")
                    exit()

def initiate_database():
    """
    initiates a database (generates the tables in the database (creates them if they not exist)
    :return: None
    """
    if args.create_DB:
        create_database()

    # Drops all tables. del when DB is ready
    # Base.metadata.drop_all(engine)

    # creates all tables - if exists won't do anything
    Base.metadata.create_all(engine)

    # create table website for all the websites
    create_table_website(WEBSITE_NAMES)


def create_table_website(web_names):
    """
    get a list of all the websites that the user wants to scrap from
    create new entries in table websites with those names
    """

    if not engine.dialect.has_table(engine, 'websites'):
        raise print('Table websites not exist in DB')

    for name in web_names:
        web = session.query(WebsitesT).filter(WebsitesT.name == name).first()
        if web is None:
            web = WebsitesT(name=name)
            session.add(web)
            session.commit()



def auto_scrap_updates(website_name):
    """
    gets the website name that is being scraped
    checks in the user table what is the last rank that was scraped based on website id
     returns value + 1 as the instance to first scrap
    """
    web = session.query(WebsitesT).filter(WebsitesT.name == website_name).first()

    last_scraped = session.query(func.max(UserT.rank)).filter(UserT.website_id == web.id).scalar()
    try:
        return last_scraped + 1
    except TypeError:
        return MIN_LAST_SCRAPED + 1

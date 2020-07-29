"""
This file manages most of the connections with the database. The file contain the following functions:
create_database() - creates the DB  (if the requested one does not exist yet)
initiate_database() - It initiates a database (generates the tables in the database (creates them if they not exist)
create_table_website - create the website table and add entities according to the new website to scrap
find_last_user_scrapped - finds the last users to scrap from the table
"""

from src import config, logger, engine, Base, session, cursor_instance
from src.ORM import WebsitesT, UserT
import pymysql
from sqlalchemy import func

def create_database():
    """
    creates the DB  (if not exist yet - if it is, continues).
    checks if connection to the database is valid
    """
    # SQL Statement to check if DB exist
    sql_statement = config.CHECK_DB + config.DB_NAME + '"'

    if cursor_instance.execute(sql_statement) == 0:
        # SQL Statement to create a database
        sql_statement = "CREATE DATABASE " + config.DB_NAME
        try:
            # Execute the create database SQL statement through the cursor instance
            cursor_instance.execute(sql_statement)
        except pymysql.err.ProgrammingError:
            logger.error(config.DB_NAME_NOT_VALID.format(config.DB_NAME))
            exit()


def initiate_database(websites):
    """
    initiates a database (generates the tables in the database (creates them if they not exist)
    """
    create_database()

    # Drops all tables. del when DB is ready
    Base.metadata.drop_all(engine)

    # creates all tables - if exists won't do anything
    Base.metadata.create_all(engine)


def insert_website_to_DB(website_dict):
    """
    enters data of website into DB. if the entity already exists, update relevant data
    :param website_dict: parameters of website table (dict)
    """

    web = session.query(WebsitesT).filter(WebsitesT.name == website_dict["name"]).first()

    if web:
        web.total_users = website_dict["total_users"]
        web.total_answers = website_dict["total_answers"]
        web.total_questions = website_dict["total_questions"]
        web.answers_per_minute = website_dict["answers_per_minute"]
        web.questions_per_minute = website_dict["questions_per_minute"]

    else:
        web = WebsitesT(**website_dict)
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

    try:
        last_scraped = session.query(func.max(UserT.rank)).filter(UserT.website_id == web.id).scalar()
        return last_scraped + 1
    except TypeError:
        return 1
    except AttributeError:
        return 1
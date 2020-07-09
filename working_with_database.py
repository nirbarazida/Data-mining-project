from ORM import WebsitesT, engine, Base, session
from command_args import args
import os
import pymysql

MIN_LAST_SCRAPED = 0
NUM_USERS_TO_SCRAP = args.num_users
WEBSITE_NAMES = args.web_sites
USER_NAME = os.environ.get("MySQL_USER")
PASSWORD = os.environ.get("MySQL_PASS")
DB_NAME = args.DB_name


def initiate_database():

    if args.create_DB:
        create_database()

    # Drops all tables. del when DB is ready
    # Base.metadata.drop_all(engine)

    # creates all tables - if exists won't do anything
    Base.metadata.create_all(engine)

    # create table website for all the websites
    create_table_website(WEBSITE_NAMES)


def create_database():
    # todo NIR: add exceptions

    connection = pymysql.connect(host='localhost', user=USER_NAME, password=PASSWORD)

    # Create a cursor object
    cursor_insatnce = connection.cursor()

    # SQL Statement to check if DB exist
    sql_statement = 'SELECT distinct(SCHEMA_NAME) FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = ' '"' + DB_NAME + '"'

    if cursor_insatnce.execute(sql_statement) == 0:
        # SQL Statement to create a database
        sql_statement = "CREATE DATABASE " + DB_NAME

        # Execute the create database SQL statement through the cursor instance
        cursor_insatnce.execute(sql_statement)


def create_table_website(web_names):
    """
    get a list of all the websites that the user wants to scrap from
    create new entries in table websites with those names
    """

    if not engine.dialect.has_table(engine, 'websites'):
        raise print(f'Table websites not exist in DB')

    for name in web_names:
        web = session.query(WebsitesT).filter(WebsitesT.name == name).first()
        if web is None:
            web = WebsitesT(name=name, last_scraped=MIN_LAST_SCRAPED)
            session.add(web)
            session.commit()


def auto_scrap_updates(website_name):
    web = session.query(WebsitesT).filter(WebsitesT.name == website_name).first()
    first_instance_to_scrap = web.last_scraped + 1
    web.last_scraped += NUM_USERS_TO_SCRAP  # todo BOTH: can cause trouble if program fails before finishing
    return first_instance_to_scrap
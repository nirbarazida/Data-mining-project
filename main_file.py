"""
Data mining project - "Analysis of Stack Exchange Websites"- main file
milestone 1: program implementations:
1. Scraps a list of websites under the Stack Exchange websites
    (such as stack overflow, askUbuntu, etc)
2. Scraps several websites in a loop or concurrently by Multi Process
3. Scraps the websites' individual User pages for requested index (not necessarily from the beginning)
     until the number of sequence(s) requested
4. data for each user is transformed via generators:
    a. generator for sequence of main pages (includes X individual instances in each page)
    b. generator of instances of user object (includes a dictionary of the relevant data which was scrapped)
5. The data of each user for each website is appended to its relevant list (in a dedicated dictionary)
    when the list reaches it's demanded length - it prints all the values in the list and cleans it
    (This is preparation for uploading the data in chunks to the database)
6. When the user index reaches the user last index requested (according to the amount of users to scrap)
    the program prints the last amount of data needed (if there is list of users which have not been printed yet)
    and program breaks from the function (in the case of a loop, it will begin the next website. in the Multi Process case,
    it can happen in en expected ratio - but it assures that each one of the websites will scrap all the requested users
Along with the main file, the program include the following files:
1. website.py - includes the class Website(object) - create soup of pages, find last page and create soups for main topic pages
2. user_analysis.py - includes the class UserAnalysis(Website) - create a generator of links for each individual user page
3. user.py - includes the class User(Website) - extracts the data in the individual user file - creates a dict object
4. data mining_constants.txt - text file in json format which contains the constants for all the program.
                               each file imports the data that is relevant to run the file.
Authors: Nir Barazida and Inbar Shirizly
"""

from command_args import args
import create_DB
import time
from user_analysis import UserAnalysis
from user import User
import json
import concurrent.futures
import logging
from ORM import WebsitesT, engine, Base, session
import pandas as pd
pd.set_option('display.max_columns', 15)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(message)s')
file_handler = logging.FileHandler('main.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)



# implementing the command line arguments into variables
# will not use the arguments directly for flexibility purposes (to using json file for input variables)
WEBSITE_NAMES = args.web_sites
FIRST_INSTANCE_TO_SCRAP = args.first_user
NUM_USERS_TO_SCRAP = args.num_users
RECORDS_IN_CHUNK_OF_DATA = args.chunk_of_data
SLEEP_FACTOR = args.sleep_factor
MULTI_PROCESS = args.multi_process
AUTO_SCRAP = args.auto_scrap

MIN_LAST_SCRAPED = 0

JSON_FILE_NAME = "mining_constants.json"
# get constants from json file (which contains all the Constants)

with open(JSON_FILE_NAME, "r") as json_file:
    constants_data = json.load(json_file)

# constants - Stays always the same
NUM_INSTANCES_IN_PAGE = constants_data["constants"]["NUM_INSTANCES_IN_PAGE"]


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


def scrap_users(website_name):
    """
    receives website name and scrap individual users data (via the classes generators in the related files)
    create a dictionary [website: [user_instance1, user_instance2...] each list has maximum length of
    RECORDS_IN_CHUNK_OF_DATA. when the list reaches this length, it prints the data on each user and cleans the list
    when the user index reaches the last user needed (per website), the function prints the rest of the data (the users
    that are in the last list) in breaking out (on the Multi Process mode, this function runs concurrently on different websites)
    :param website_name: domain name of the website that is been scrapped (str)
    :return: None
    """
    if AUTO_SCRAP:
        web = session.query(WebsitesT).filter(WebsitesT.name == website_name).first()
        FIRST_INSTANCE_TO_SCRAP = web.last_scraped + 1
        web.last_scraped += NUM_USERS_TO_SCRAP  # todo BOTH: can cause trouble if program fails before finishing

    websites_chunk_dict = {website: [] for website in WEBSITE_NAMES}
    index_for_first_page = (FIRST_INSTANCE_TO_SCRAP // NUM_INSTANCES_IN_PAGE) + 1
    index_for_first_instance_in_first_page = FIRST_INSTANCE_TO_SCRAP % NUM_INSTANCES_IN_PAGE

    user_page = UserAnalysis(website_name, index_for_first_page, index_for_first_instance_in_first_page)

    logger.info(f"Website: {website_name} ,number of users to scrap = {NUM_USERS_TO_SCRAP},"
          f" sleep factor = {SLEEP_FACTOR}, first user: {FIRST_INSTANCE_TO_SCRAP},"
          f" last user: {FIRST_INSTANCE_TO_SCRAP + NUM_USERS_TO_SCRAP - 1},"
          f" Multi Process? {MULTI_PROCESS} ")

    # create a new user
    for link in user_page.generate_users_links():
        user = User(website_name, link, FIRST_INSTANCE_TO_SCRAP)
        user.scrap_info(link)

        websites_chunk_dict[website_name].append(user)

        for website_chunk, records in websites_chunk_dict.items():
            if len(records) == RECORDS_IN_CHUNK_OF_DATA:
                logger.info(f"print chunk of {RECORDS_IN_CHUNK_OF_DATA} for website {website_name}")
                for user_i in websites_chunk_dict[website_chunk]:
                    user_i.insert_user()
                    # print(user_i)
                # users_chunk = pd.DataFrame(websites_chunk_dict[website_chunk])
                # print(users_chunk)
                websites_chunk_dict[website_chunk] = []

        if user.num_user_dict[website_name] == FIRST_INSTANCE_TO_SCRAP + NUM_USERS_TO_SCRAP - 1:
            if len(websites_chunk_dict[website_name]) > 0:
                logger.info(f"print chunk of {len(websites_chunk_dict[website_name])} for website {website_name}")
                for user_i in websites_chunk_dict[website_name]:
                    user_i.insert_user()
                    # print(user_i)
                # users_chunk = pd.DataFrame(websites_chunk_dict[website_name])
                # print(users_chunk)
            break


def main():
    t_start = time.perf_counter()

    # Drops all tables. del when DB is ready
    # Base.metadata.drop_all(engine)

    # creates all tables - if exists won't do anything
    Base.metadata.create_all(engine)

    # create table website for all the websites
    create_table_website(WEBSITE_NAMES)

    # Multi Process mode
    if MULTI_PROCESS:
        with concurrent.futures.ProcessPoolExecutor() as executer:
            executer.map(scrap_users, WEBSITE_NAMES)
    # for loop mode
    else:
        for website_name in WEBSITE_NAMES:
            t1 = time.perf_counter()
            scrap_users(website_name)
            t2 = time.perf_counter()
            logger.info(f"Finished to scrap {NUM_USERS_TO_SCRAP} users in {round(t2 - t1, 2)} seconds")

    t_end = time.perf_counter()
    logger.info(f"Finished all the code in {round(t_end - t_start, 2)} seconds")


if __name__ == '__main__':
    main()

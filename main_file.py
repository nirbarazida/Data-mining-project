"""
Data mining project - "Analysis of Stack Exchange Websites"- main file
milestone 1 + 2: program implementations:
1. create DB or use an existing one according to command line specifications.
2. In the DB, create and use tables using ORM (SQLAlchemy)
3. Scraps a list of websites under the Stack Exchange websites
    (such as stack overflow, askUbuntu, etc)
4. Scraps several websites in a loop or concurrently by Multi Process
5. Scraps the websites' individual User pages for requested index (not necessarily from the beginning)
     until the number of sequence(s) requested. The default argument will be 'auto-scrap' that starts to scrap from the
     last user in the data base - per website.
6. data for each user is transformed via generators:
    a. generator for sequence of main pages (includes X individual instances in each page)
    b. generator of instances of user object (includes a dictionary of the relevant data which was scrapped)
7. for each user, the scrapper receives the information and add it to the tables, checking integrity and duplicates.
8. When the user index reaches the user last index requested (according to the amount of users to scrap)
    program breaks from the function (in the case of a loop, it will begin the next website. in the Multi Process case,
    it can happen in en expected ratio - but it assures that each one of the websites will scrap all the requested users
Along with the main file, the program include the following files:
1. command_args - file which arrange the user input from the command line
2. logger - file contains class logger - for general logger format
3. ORM - file that defines schema using ORM - create tables and all relationships between the tables in the database.
4. working_with_database - file that contains most of the function which CRUD with the database
5. website - includes the class Website(object) - create soup of pages, find last page and create soups for main topic pages
6. user_analysis- includes the class UserAnalysis(Website) - create a generator of links for each individual user page
7. user- includes the class User(Website) - extracts the data in the individual user file and add the data to the
relevant tables
8. mining_constants.json - json format file contains the constants for all the program.
                               each file imports the data that is relevant to run the file.
9. requirements.txt - file with all the packages and dependencies of the project
Authors: Nir Barazida and Inbar Shirizly
"""

from command_args import args
import time
from user_analysis import UserAnalysis
from user import User
import json
import concurrent.futures
from logger import Logger
from tqdm import tqdm
from functools import wraps
from working_with_database import initiate_database, create_table_website, auto_scrap_updates
import random

logger_main = Logger("main").logger

# implementing the command line arguments into variables
# will not use the arguments directly for flexibility purposes (to using json file for input variables)
WEBSITE_NAMES = args.web_sites
FIRST_INSTANCE_TO_SCRAP = args.first_user
NUM_USERS_TO_SCRAP = args.num_users
SLEEP_FACTOR = args.sleep_factor
MULTI_PROCESS = args.multi_process
AUTO_SCRAP = args.auto_scrap
DB_NAME = args.DB_name

JSON_FILE_NAME = "mining_constants.json"
# get constants from json file (which contains all the Constants)

with open(JSON_FILE_NAME, "r") as json_file:
    constants_data = json.load(json_file)

# nunber of instances in each page
NUM_INSTANCES_IN_PAGE = constants_data["constants"]["NUM_INSTANCES_IN_PAGE"]

# logger strings
OPENING_STRING = constants_data["constants"]["LOGGER_STRINGS"]["OPENING_STRING"]
SANITY_CHECK_STRING = constants_data["constants"]["LOGGER_STRINGS"]["SANITY_CHECK_STRING"]
WEBSITE_SCRAPP_INFO = constants_data["constants"]["LOGGER_STRINGS"]["WEBSITE_SCRAPP_INFO"]
SELF_SCRAPING_WARNING = constants_data["constants"]["LOGGER_STRINGS"]["SELF_SCRAPING_WARNING"]


def arrange_first_user_to_scrap(website_name):
    """
    get the first instance to scarp for each user. from this variable,
    get the number of the first page and the number of the first user in that page
    :param website_name: the website (str)
    :return: first_instance_to_scrap (int), index_first_page(int), index_first_instance_in_first_page(int)
    """

    first_instance_to_scrap = auto_scrap_updates(website_name)
    if not AUTO_SCRAP or FIRST_INSTANCE_TO_SCRAP:
        print(
            SELF_SCRAPING_WARNING.format("\n", website_name, first_instance_to_scrap - 1, "\n", FIRST_INSTANCE_TO_SCRAP,
                                         first_instance_to_scrap - 1 - FIRST_INSTANCE_TO_SCRAP, ))
        first_instance_to_scrap = FIRST_INSTANCE_TO_SCRAP

    index_first_page = (first_instance_to_scrap // NUM_INSTANCES_IN_PAGE) + 1
    index_first_instance_in_first_page = first_instance_to_scrap % NUM_INSTANCES_IN_PAGE
    return first_instance_to_scrap, index_first_page, index_first_instance_in_first_page


def timer(func):
    """
    time decorator - calculates the time that the checked function ran
    :param func: checked function
    """

    @wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        logger_main.info(f'Finished {func.__name__!r} in  {run_time:.2f} seconds')

    return wrapper_timer


@timer
def scrap_users(website_name):
    """
    receives website name and scrap individual users data (via the classes generators in the related files)
    the information scrapped is inserted to the database.
    the function generates a random user for a sanity check , logs information that can be checked manually
    when the user index reaches the last user needed (per website) finish code.
    on the Multi Process mode, this function runs concurrently on different websites
    :param website_name: domain name of the website that is been scrapped (str)
    :return: None
    """

    first_instance_to_scrap, index_first_page, index_first_instance_in_first_page = arrange_first_user_to_scrap(
        website_name)

    user_page = UserAnalysis(website_name, index_first_page, index_first_instance_in_first_page)

    logger_main.info(WEBSITE_SCRAPP_INFO.format(website_name, first_instance_to_scrap,
                                                first_instance_to_scrap + NUM_USERS_TO_SCRAP - 1))

    random_user_to_check = random.randint(0, NUM_USERS_TO_SCRAP - 1)

    # create a new user
    user_links_generator = user_page.generate_users_links()
    for num_user, link in enumerate(tqdm(user_links_generator, desc=f"{website_name}",
                                         total=NUM_USERS_TO_SCRAP, position=1, leave=False)):
        user = User(website_name, link, first_instance_to_scrap)
        user.scrap_info()
        user.insert_user()

        if num_user == random_user_to_check:
            logger_main.info(SANITY_CHECK_STRING.format(link, website_name,
                                                        user._rank // NUM_INSTANCES_IN_PAGE, user._reputation_now))

        if num_user == NUM_USERS_TO_SCRAP - 1:
            break


@timer
def main():
    initiate_database()
    logger_main.info(OPENING_STRING.format(DB_NAME, NUM_USERS_TO_SCRAP, SLEEP_FACTOR, MULTI_PROCESS))

    # Multi Process mode
    if MULTI_PROCESS:
        with concurrent.futures.ProcessPoolExecutor() as executer:
            executer.map(scrap_users, WEBSITE_NAMES)
    # for loop mode
    else:
        for website_name in tqdm(WEBSITE_NAMES, desc="Websites", position=0):
            scrap_users(website_name)


if __name__ == '__main__':
    main()

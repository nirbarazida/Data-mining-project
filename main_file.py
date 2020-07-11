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

def arrange_first_user_to_scrap(website_name): #: TODO - moved from main function - need to find place for it

    first_instance_to_scrap = auto_scrap_updates(website_name) if AUTO_SCRAP else FIRST_INSTANCE_TO_SCRAP

    index_first_page = (first_instance_to_scrap // NUM_INSTANCES_IN_PAGE) + 1
    index_first_instance_in_first_page = first_instance_to_scrap % NUM_INSTANCES_IN_PAGE
    return first_instance_to_scrap, index_first_page, index_first_instance_in_first_page


def timer(func):
    @wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        logger_main.info(f'Finished {func.__name__!r} in  {run_time:.2f} seconds') #: TODO - print for each website unique string
    return wrapper_timer


@timer
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

    first_instance_to_scrap, index_first_page, index_first_instance_in_first_page = arrange_first_user_to_scrap(website_name)

    user_page = UserAnalysis(website_name, index_first_page, index_first_instance_in_first_page)

    logger_main.info(WEBSITE_SCRAPP_INFO.format(website_name, first_instance_to_scrap,
                                                first_instance_to_scrap + NUM_USERS_TO_SCRAP - 1))

    random_user_to_check = random.randint(0, NUM_USERS_TO_SCRAP - 1)

    # create a new user
    user_links_generator = user_page.generate_users_links()
    for num_user, link in enumerate(tqdm(user_links_generator, desc=f"{website_name}",
                                         total=NUM_USERS_TO_SCRAP, position=1, leave=False)):
        user = User(website_name, link, first_instance_to_scrap)
        user.scrap_info(link)
        user.insert_user()


        if num_user == random_user_to_check: #:TODO - after milstone2 - create here a sanity check - pick random user from the data base and makes sure it corresponds to the website api data
            logger_main.info(SANITY_CHECK_STRING.format(link, website_name,
                                                        user._rank // NUM_INSTANCES_IN_PAGE, user._reputation_now))  #: TODO - add getters for these variables in user

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

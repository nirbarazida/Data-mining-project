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

from src import logger, config, general
import argparse
from src.user_analysis import UserAnalysis
from src.user import User
import concurrent.futures
from tqdm import tqdm
from src.working_with_database import initiate_database
import random
from itertools import repeat


@general.timer
def scrap_users(website_name, num_users_to_scrap):
    """
    receives website name and scrap individual users data (via the classes generators in the related files)
    the information scrapped is inserted to the database.
    the function generates a random user for a sanity check , logs information that can be checked manually
    when the user index reaches the last user needed (per website) finish code.
    on the Multi Process mode, this function runs concurrently on different websites
    :param website_name: domain name of the website that is been scrapped (str)
    :param num_users_to_scrap: number of users to scrap in the following sessiom
    :return: None
    """

    first_instance_to_scrap, index_first_page, index_first_instance_in_first_page = general.arrange_first_user_to_scrap(
        website_name)

    user_page = UserAnalysis(website_name, index_first_page, index_first_instance_in_first_page)

    logger.info(config.WEBSITE_SCRAPP_INFO.format(website_name, first_instance_to_scrap,
                                                first_instance_to_scrap + num_users_to_scrap - 1))

    random_user_to_check = random.randint(0, num_users_to_scrap - 1)

    # create a new user
    user_links_generator = user_page.generate_users_links()
    for num_user, link in enumerate(tqdm(user_links_generator, desc=f"{website_name}",
                                         total=num_users_to_scrap, position=1, leave=False)):
        user = User(link, website_name, first_instance_to_scrap)
        user.create_user()
        user.insert_user_to_DB()

        if num_user == random_user_to_check:
            logger.info(config.SANITY_CHECK_STRING.format(link, website_name,
                                                        user._rank // config.NUM_INSTANCES_IN_PAGE, user._reputation_now))

        if num_user == num_users_to_scrap - 1:
            break


@general.timer
def main():
    # receiving arguments from the command line terminal for the scraping process

    parser = argparse.ArgumentParser(description='Scraping users from Stack Exchange websites')

    parser.add_argument('--db_name', help="database name", type=str, default='stack_exchange_db')
    parser.add_argument('--num_users_to_scrap', help="Number of users to scrap", type=int, default=10)
    parser.add_argument('--websites', help="Which Stack Exchange websites to scrap from", nargs='+',
                        default=['stackoverflow', 'askubuntu', 'math.stackexchange', 'superuser'],
                        choices={'stackoverflow', 'askubuntu', 'math.stackexchange', 'superuser'})
    parser.add_argument("--multi_process",
                        help="To use Multi Process or basic for loop between the different websites, "
                             "default=False "
                        , type=general.bool_converter, default=False)
    args = parser.parse_args()


    initiate_database(args.websites)
    logger.info(config.OPENING_STRING.format(config.DB_NAME, args.num_users_to_scrap, config.SLEEP_FACTOR, args.multi_process))

    # Multi Process mode
    if args.multi_process:
        with concurrent.futures.ProcessPoolExecutor() as executer:
            executer.map(scrap_users, *[args.websites, repeat(args.num_users_to_scrap)])
    # for loop mode
    else:
        for website_name in args.websites:
            scrap_users(website_name, args.num_users_to_scrap)


if __name__ == '__main__':
    main()

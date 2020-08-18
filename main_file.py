"""
Data mining project - "Analysis of Stack Exchange Websites"- main file

1. create databases and tables using ORM with MySQL
2. scrap data from multiple website (with or without multi-proccessing
3. enrich the database with data from an API request
3. insert data into dedicated tables in the database

Authors: Nir Barazida and Inbar Shirizly
"""

from src import logger, config, general, database
import argparse
from API.website_api import WebsiteAPI
from scraper import UserAnalysis
from scraper import UserScraper
import concurrent.futures
from tqdm import tqdm
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
    :param num_users_to_scrap: number of users to scrap in the following session
    :return: None
    """

    first_instance_to_scrap, index_first_page, index_first_instance_in_first_page = general.arrange_first_user_to_scrap(
        website_name)

    # commit website data enrichment from the API
    database.commit_website_to_DB(WebsiteAPI(website_name).website_info)

    logger.info(config.WEBSITE_SCRAPP_INFO.format(website_name, first_instance_to_scrap,
                                                first_instance_to_scrap + num_users_to_scrap - 1))

    random_user_to_check = random.randint(0, num_users_to_scrap - 1)

    # create user link generator
    user_page = UserAnalysis(website_name, index_first_page, index_first_instance_in_first_page)
    user_links_generator = user_page.generate_users_links()
    for num_user, link in enumerate(tqdm(user_links_generator, desc=f"{website_name}",
                                         total=num_users_to_scrap, position=1, leave=False)):
        # create a new user
        user = UserScraper(link, website_name, first_instance_to_scrap)
        # insert user to the database
        database.insert_user_to_DB(user)

        # log a sanity check for a random user
        if num_user == random_user_to_check:
            logger.info(config.SANITY_CHECK_STRING.format(link, website_name,
                                                        user._rank // config.NUM_INSTANCES_IN_PAGE, user._reputation_now))
        # stop when reached to requested number of users
        if num_user == num_users_to_scrap - 1:
            break


@general.timer
def main():
    # receiving arguments from the command line terminal for the scraping process
    parser = argparse.ArgumentParser(description='Scraping users from Stack Exchange websites')

    parser.add_argument('--num_users_to_scrap', help="Number of users to scrap", type=int, default=10)
    parser.add_argument('--websites', help="Which Stack Exchange websites to scrap from", nargs='+',
                        default=['stackoverflow', 'askubuntu', 'math.stackexchange', 'superuser'],
                        choices={'stackoverflow', 'askubuntu', 'math.stackexchange', 'superuser'})
    parser.add_argument("--multi_process",
                        help="To use Multi Process or basic for loop between the different websites, "
                             "default=False "
                        , type=general.bool_converter, default=False)
    args = parser.parse_args()

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

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

import time
from user_analysis import UserAnalysis
from user import User
import json
import concurrent.futures
from command_args import args



# implementing the command line arguments into variables
# will not use the arguments directly for flexibility purposes (to using json file for input variables)
WEBSITE_NAMES = args.web_sites
FIRST_INSTANCE_TO_SCRAP = args.first_user
NUM_USERS_TO_SCRAP = args.num_users
RECORDS_IN_CHUNK_OF_DATA = args.chunk_of_data
SLEEP_FACTOR = args.sleep_factor
MULTI_PROCESS = args.multi_process

# get constants from json file (which contains all the Constants)
with open("data_mining_constants.txt", "r") as json_file:
    constants_data = json.load(json_file)

# constants - Stays always the same
NUM_INSTANCES_IN_PAGE = constants_data["constants"]["NUM_INSTANCES_IN_PAGE"]


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
    websites_chunk_dict = {website: [] for website in WEBSITE_NAMES}
    index_for_first_page = (FIRST_INSTANCE_TO_SCRAP // NUM_INSTANCES_IN_PAGE) + 1
    index_for_first_instance_in_first_page = FIRST_INSTANCE_TO_SCRAP % NUM_INSTANCES_IN_PAGE

    user_page = UserAnalysis(website_name, index_for_first_page, index_for_first_instance_in_first_page)

    print(f"Website: {website_name} ,number of users to scrap = {NUM_USERS_TO_SCRAP},"
          f" sleep factor = {SLEEP_FACTOR}, first user: {FIRST_INSTANCE_TO_SCRAP},"
          f" last user: {FIRST_INSTANCE_TO_SCRAP + NUM_USERS_TO_SCRAP - 1},"
          f" Multi Process? {MULTI_PROCESS} ")

    for link in user_page.generate_users_links():
        user = User(website_name, link)
        websites_chunk_dict[website_name].append(user)

        for website_chunk, records in websites_chunk_dict.items():
            if len(records) == RECORDS_IN_CHUNK_OF_DATA:
                print(f"print chunk of {RECORDS_IN_CHUNK_OF_DATA} for website {website_name}")
                for user_data in websites_chunk_dict[website_chunk]:
                    print(user_data)
                websites_chunk_dict[website_chunk] = []

        if user.num_user_dict[website_name] == FIRST_INSTANCE_TO_SCRAP + NUM_USERS_TO_SCRAP - 1:
            if len(websites_chunk_dict[website_name]) > 0:
                print(f"print chunk of {len(websites_chunk_dict[website_name])} for website {website_name}")
                for user_data in websites_chunk_dict[website_name]:
                    print(user_data)
            break


def main():

    t_start = time.perf_counter()

    # Treading mode
    if MULTI_PROCESS:
        with concurrent.futures.ThreadPoolExecutor() as executer:
            executer.map(scrap_users, WEBSITE_NAMES)
    # for loop mode
    else:
        for website_name in WEBSITE_NAMES:
            t1 = time.perf_counter()
            scrap_users(website_name)
            t2 = time.perf_counter()
            print(f"Finished to scrap {NUM_USERS_TO_SCRAP} users in {round(t2 - t1, 2)} seconds")

    t_end = time.perf_counter()
    print(f"Finished all the code in {round(t_end - t_start, 2)} seconds")


if __name__ == '__main__':
    main()
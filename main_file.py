"""
Authors: Nir Barazida and Inbar Shirizly
"""

import time
import logging
import user_scrapper_oop as s
import concurrent.futures

# constants
MIN_NUM_USERS_TO_SCRAP = 20
WEBSITE_NAMES = ["stackoverflow", "askubuntu", "math.stackexchange", "superuser"]
SLEEP_FACTOR = 1.5


def scrap_users(website_name):

    user_page = s.UserAnalysis(website_name)
    logging.info(f"Website: {website_name} ,number of users to scrap = {MIN_NUM_USERS_TO_SCRAP},"
                 f" sleep factor = {SLEEP_FACTOR}")
    for i, link in enumerate(user_page.generate_users_links()):
        user = s.User(link, website_name)
        logging.info(user.get_dict())
        # if user.num_user == MIN_NUM_USERS_TO_SCRAP - 1:
        #     break
        if i == MIN_NUM_USERS_TO_SCRAP - 1:
            break


def scrap_tags(website_name):

    tags_page = s.TagsAnalysis(website_name)
    for i, tag_name in enumerate(tags_page.get_tags_high_level_data()):
        logging.info(tag_name)
        if i == MIN_NUM_USERS_TO_SCRAP - 1:
            break


def main():
    logging.basicConfig(filename="scrapper.log", level=logging.INFO,
                        format='%(asctime)s : %(name)s : %(message)s')

    t_start = time.perf_counter()
    # with concurrent.futures.ThreadPoolExecutor() as executer:
    #     executer.map(scrap_users, WEBSITE_NAMES)
    #     executer.map(scrap_tags, WEBSITE_NAMES)

    for website_name in WEBSITE_NAMES[:2]:
        t1 = time.perf_counter()
        scrap_users(website_name)
        t2 = time.perf_counter()
        logging.info(f"Finished to scrap {MIN_NUM_USERS_TO_SCRAP} users in {round(t2 - t1, 2)} seconds")

        t1 = time.perf_counter()
        scrap_tags(website_name)
        t2 = time.perf_counter()
        logging.info(f"Finished to scrap {MIN_NUM_USERS_TO_SCRAP} tags in {round(t2 - t1, 2)} seconds")

    t_end = time.perf_counter()
    print(f"Finished all the code in {round(t_end - t_start, 2)} seconds")


if __name__ == '__main__':
    main()
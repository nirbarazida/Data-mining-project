"""
Authors: Nir Barazida and Inbar Shirizly
"""

import time
import logging
import user_scrapper_oop as s
import concurrent.futures

# constants - Stays always the same
NUM_INSTANCES_IN_PAGE = 36

# constants - user might change according to his needs
WEBSITE_NAMES = ["stackoverflow", "askubuntu", "math.stackexchange", "superuser"]
FIRST_INSTANCE_TO_SCRAP = 37
MIN_NUM_USERS_TO_SCRAP = 30
RECORDS_IN_CHUNK_OF_DATA = 10
SLEEP_FACTOR = 1.5




def scrap_users(website_name):

    websites_chunk_dict = {website: [] for website in WEBSITE_NAMES}
    index_for_first_page = (FIRST_INSTANCE_TO_SCRAP // NUM_INSTANCES_IN_PAGE) + 1
    index_for_first_instance_in_first_page = FIRST_INSTANCE_TO_SCRAP % NUM_INSTANCES_IN_PAGE

    user_page = s.UserAnalysis(website_name, index_for_first_page, index_for_first_instance_in_first_page)


    logging.info(f"Website: {website_name} ,number of users to scrap = {MIN_NUM_USERS_TO_SCRAP},"
                 f" sleep factor = {SLEEP_FACTOR}, first user: {FIRST_INSTANCE_TO_SCRAP},"
                 f" last user: {FIRST_INSTANCE_TO_SCRAP + MIN_NUM_USERS_TO_SCRAP - 1}")

    print(f"Website: {website_name} ,number of users to scrap = {MIN_NUM_USERS_TO_SCRAP},"
                 f" sleep factor = {SLEEP_FACTOR}, first user: {FIRST_INSTANCE_TO_SCRAP},"
                 f" last user: {FIRST_INSTANCE_TO_SCRAP + MIN_NUM_USERS_TO_SCRAP - 1}")

    for link in user_page.generate_users_links():
        user = s.User(website_name, link)
        websites_chunk_dict[website_name].append(user)

        for website_chunk, records in websites_chunk_dict.items():
            if len(records) == RECORDS_IN_CHUNK_OF_DATA:
                print(f"print chunk of {RECORDS_IN_CHUNK_OF_DATA} for website {website_name}")
                print(websites_chunk_dict[website_chunk])
                logging.info(websites_chunk_dict[website_chunk])
                websites_chunk_dict[website_chunk] = []

        if user.num_user_dict[website_name] == FIRST_INSTANCE_TO_SCRAP + MIN_NUM_USERS_TO_SCRAP - 1:
            if len(websites_chunk_dict[website_name]) > 0:
                print(f"print chunk of {len(websites_chunk_dict[website_name])} for website {website_name}")
                print(websites_chunk_dict[website_name])
                logging.info(websites_chunk_dict[website_name])
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
    with concurrent.futures.ThreadPoolExecutor() as executer:
        executer.map(scrap_users, WEBSITE_NAMES)
    #     #executer.map(scrap_tags, WEBSITE_NAMES)

    # for website_name in WEBSITE_NAMES[-1:]:
    #     t1 = time.perf_counter()
    #     scrap_users(website_name)
    #     t2 = time.perf_counter()
    #     logging.info(f"Finished to scrap {MIN_NUM_USERS_TO_SCRAP} users in {round(t2 - t1, 2)} seconds")

        # t1 = time.perf_counter()
        # scrap_tags(website_name)
        # t2 = time.perf_counter()
        # logging.info(f"Finished to scrap {MIN_NUM_USERS_TO_SCRAP} tags in {round(t2 - t1, 2)} seconds")

    t_end = time.perf_counter()
    print(f"Finished all the code in {round(t_end - t_start, 2)} seconds")
    logging.info(f"Finished all the code in {round(t_end - t_start, 2)} seconds")

if __name__ == '__main__':
    main()
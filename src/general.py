import time
from functools import wraps
import argparse
from src.working_with_database import find_last_user_scrapped
from src import logger, config


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
        logger.info(f'Finished {func.__name__!r} in  {run_time:.2f} seconds')
    return wrapper_timer


def arrange_first_user_to_scrap(website_name):
    """
    get the first instance to scarp for each user. from this variable,
    get the number of the first page and the number of the first user in that page
    :param website_name: the website (str)
    :return: first_instance_to_scrap (int), index_first_page(int), index_first_instance_in_first_page(int)
    """

    first_instance_to_scrap = find_last_user_scrapped(website_name)
    index_first_page = (first_instance_to_scrap // config.NUM_INSTANCES_IN_PAGE) + 1
    index_first_instance_in_first_page = first_instance_to_scrap % config.NUM_INSTANCES_IN_PAGE
    return first_instance_to_scrap, index_first_page, index_first_instance_in_first_page


def bool_converter(p):
    """ gets the command line argument for Multi Process
        converts it to a boolean variable.
        if not valid - raise a type error
    """
    if p.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif p.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')






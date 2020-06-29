import argparse

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


# receiving arguments from the command line terminal for the scraping process
parser = argparse.ArgumentParser(description='Scraping users from Stack Exchange websites')

parser.add_argument('first_user', help="Position of the first user to scrap", type=int)

parser.add_argument('num_users', help="Number of users to scrap", type=int)

parser.add_argument('--web_sites', help="Which Stack Exchange websites to scrap from", nargs='+',
                    default=['stackoverflow', 'askubuntu', 'math.stackexchange', 'superuser'],
                    choices={'stackoverflow', 'askubuntu', 'math.stackexchange', 'superuser'})

parser.add_argument('--chunk_of_data', help="How many users to store in memory before\
                     uploading to data base, default=10", default=10, type=int)

parser.add_argument('--sleep_factor', help="Sleep factor between requests, default=1.5", default=1.5, type=float)

parser.add_argument("--multi_process", help="To use Multi Process or basic for loop between the different websites, "
                                        "default=False "
                    , type=bool_converter, default=False)

args = parser.parse_args()
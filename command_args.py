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

parser.add_argument('user_name', help="mysql user name", type=str)

parser.add_argument('password', help="mysql user password", type=str)

parser.add_argument('DB_name', help="databse name", type=str)

parser.add_argument('--num_users', help="Number of users to scrap", type=int, default=2)

parser.add_argument('--first_user', help="first user to scrap", type=int, default=2) # todo NIR:check duplicates users

parser.add_argument('--web_sites', help="Which Stack Exchange websites to scrap from", nargs='+',
                    default=['stackoverflow', 'askubuntu', 'math.stackexchange', 'superuser'],
                    choices={'stackoverflow', 'askubuntu', 'math.stackexchange', 'superuser'})

parser.add_argument('--chunk_of_data', help="How many users to store in memory before\
                     uploading to data base, default=10", default=10, type=int)

parser.add_argument('--sleep_factor', help="Sleep factor between requests, default=1.5", default=1.5, type=float)

parser.add_argument("--creat_DB", help="needs to create new DB? default=False "
                    , type=bool_converter, default=False)

parser.add_argument("--auto_scrap", help="start scraping from the last instance default=True "
                    , type=bool_converter, default=True)

parser.add_argument("--multi_process", help="To use Multi Process or basic for loop between the different websites, "
                                            "default=True "
                    , type=bool_converter, default=True)

args = parser.parse_args()

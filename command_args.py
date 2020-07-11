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

parser.add_argument('--DB_name', help="database name", type=str, default='stack_exchange_db') #:TODO - we must check for valid sql name for DB

parser.add_argument('--num_users', help="Number of users to scrap", type=int, default=2)

parser.add_argument('--first_user', help="first user to scrap", type=int, default=2)

parser.add_argument('--web_sites', help="Which Stack Exchange websites to scrap from", nargs='+',
                    default=['stackoverflow', 'askubuntu', 'math.stackexchange', 'superuser'],
                    choices={'stackoverflow', 'askubuntu', 'math.stackexchange', 'superuser'})

parser.add_argument('--sleep_factor', help="Sleep factor between requests, default=1.5", default=1.5, type=float)

parser.add_argument("--create_DB", help="needs to create new DB? default=True "
                    , type=bool_converter, default=True)

parser.add_argument("--auto_scrap", help="start scraping from the last instance default=True "
                    , type=bool_converter, default=True)

parser.add_argument("--multi_process", help="To use Multi Process or basic for loop between the different websites, "
                                            "default=False "
                    , type=bool_converter, default=False)

args = parser.parse_args()

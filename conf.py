"""
config file, generate all important values from json file and
from the command line input
"""

import json
#from command_args import args
import os
import re


JSON_FILE_NAME = "mining_constants.json"

# get constants from json file (which contains all the Constants)

with open(JSON_FILE_NAME, "r") as json_file:
    constants_data = json.load(json_file)

# number of instances in each page
NUM_INSTANCES_IN_PAGE = constants_data["constants"]["NUM_INSTANCES_IN_PAGE"]

# logger strings - main file
OPENING_STRING = constants_data["constants"]["LOGGER_STRINGS"]["OPENING_STRING"]
SANITY_CHECK_STRING = constants_data["constants"]["LOGGER_STRINGS"]["SANITY_CHECK_STRING"]
WEBSITE_SCRAPP_INFO = constants_data["constants"]["LOGGER_STRINGS"]["WEBSITE_SCRAPP_INFO"]
SELF_SCRAPING_WARNING = constants_data["constants"]["LOGGER_STRINGS"]["SELF_SCRAPING_WARNING"]

# logger messages - working with database
CONNECTION_ERROR = constants_data["constants"]["LOGGER_STRINGS"]["CONNECTION_ERROR"]
SERVER_ERROR = constants_data["constants"]["LOGGER_STRINGS"]["SERVER_ERROR"]
DB_NAME_NOT_VALID = constants_data["constants"]["LOGGER_STRINGS"]["DB_NAME_NOT_VALID"]
TABLE_NOT_EXIST = constants_data["constants"]["LOGGER_STRINGS"]["TABLE_NOT_EXIST"]

# get authentication values
USER_NAME = os.environ.get(constants_data["constants"]["AUTHENTICATION"]["USER_ENV_NAME"])
PASSWORD = os.environ.get(constants_data["constants"]["AUTHENTICATION"]["PASSWORD_ENV_NAME"])


# sql statments
CHECK_DB = constants_data["constants"]["SQL_STATEMENTS"]["CHECK_DB"]


# values for parsing magnitude of numbers represented in a string (i.e - 100m = 100 * 10 ^6)
magnitude_dict = constants_data["constants"]["MAGNITUDE_MAP"]

# location handling varibales
continents_dict = constants_data["constants"]["CONTINENTS_MAP"]
KNOWN_COUNTRIES = constants_data["constants"]["KNOWN_COUNTRIES"]
IGNORE_NAME_IN_LOCATION_CACHE_TABLE = constants_data["constants"]["IGNORE_NAME_IN_LOCATION_CACHE_TABLE"]

# regex strings
REPUTATION_REGEX = re.compile(constants_data["constants"]["REGEX_STRINGS"]["REPUTATION_REGEX"])
GMT_REGEX = re.compile(constants_data["constants"]["REGEX_STRINGS"]["GMT_REGEX"])

# logger strings - geolocation exceptions
GeocoderUnavailable_WARNING_STRING = constants_data["constants"]["LOGGER_STRINGS"]["GeocoderUnavailable_WARNING_STRING"]
GeocoderUnavailable_ERROR_STRING = constants_data["constants"]["LOGGER_STRINGS"]["GeocoderUnavailable_ERROR_STRING"]

# Reputation years
REPUTATION_YEARS = constants_data["constants"]["REPUTATION_YEARS"]

# sleep time in seconds for request to locations api
SLEEP_TIME_FOR_LOCATIONS_API = constants_data["constants for user"]["SLEEP_TIME_FOR_LOCATIONS_API"]
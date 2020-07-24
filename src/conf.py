"""
config file, generate all important values from json file and
from the command line input
"""

import json
import re
import os


class Config:
    def __init__(self, JSON_FILE_NAME):
        # get constants from json file (which contains all the Constants)
        with open(JSON_FILE_NAME, "r") as json_file:
            constants_data = json.load(json_file)

        self.DB_NAME = constants_data["constants for user"]["DB_NAME"]
        self.NUM_INSTANCES_IN_PAGE = constants_data["constants"]["NUM_INSTANCES_IN_PAGE"]

        # logger strings - main file
        self.OPENING_STRING = constants_data["constants"]["LOGGER_STRINGS"]["OPENING_STRING"]
        self.SANITY_CHECK_STRING = constants_data["constants"]["LOGGER_STRINGS"]["SANITY_CHECK_STRING"]
        self.WEBSITE_SCRAPP_INFO = constants_data["constants"]["LOGGER_STRINGS"]["WEBSITE_SCRAPP_INFO"]
        self.SELF_SCRAPING_WARNING = constants_data["constants"]["LOGGER_STRINGS"]["SELF_SCRAPING_WARNING"]

        # logger messages - working with database
        self.CONNECTION_ERROR = constants_data["constants"]["LOGGER_STRINGS"]["CONNECTION_ERROR"]
        self.SERVER_ERROR = constants_data["constants"]["LOGGER_STRINGS"]["SERVER_ERROR"]
        self.DB_NAME_NOT_VALID = constants_data["constants"]["LOGGER_STRINGS"]["DB_NAME_NOT_VALID"]
        self.TABLE_NOT_EXIST = constants_data["constants"]["LOGGER_STRINGS"]["TABLE_NOT_EXIST"]

        # get authentication values
        self.USER_NAME = os.environ.get(constants_data["constants"]["AUTHENTICATION"]["USER_ENV_NAME"])
        self.PASSWORD = os.environ.get(constants_data["constants"]["AUTHENTICATION"]["PASSWORD_ENV_NAME"])

        # sql statements
        self.CHECK_DB = constants_data["constants"]["SQL_STATEMENTS"]["CHECK_DB"]

        # ORM string restrictions
        self.COUNTRY_MAX_STRING_LENGTH = constants_data["constants"]["ORM_TABLES_RESTRICTIONS"]["COUNTRY_MAX_STRING_LENGTH"]
        self.CONTINENT_MAX_STRING_LENGTH = constants_data["constants"]["ORM_TABLES_RESTRICTIONS"]["CONTINENT_MAX_STRING_LENGTH"]
        self.NAMES_STRING_LENGTH = constants_data["constants"]["ORM_TABLES_RESTRICTIONS"]["NAMES_STRING_LENGTH"]

        # values for parsing magnitude of numbers represented in a string (i.e - 100m = 100 * 10 ^6)
        self.magnitude_dict = constants_data["constants"]["MAGNITUDE_MAP"]

        # location handling variables
        self.continents_dict = constants_data["constants"]["CONTINENTS_MAP"]
        self.KNOWN_COUNTRIES = constants_data["constants"]["KNOWN_COUNTRIES"]
        self.IGNORE_NAME_IN_LOCATION_CACHE_TABLE = constants_data["constants"]["IGNORE_NAME_IN_LOCATION_CACHE_TABLE"]

        # regex strings
        self.REPUTATION_REGEX = re.compile(constants_data["constants"]["REGEX_STRINGS"]["REPUTATION_REGEX"])
        self.GMT_REGEX = re.compile(constants_data["constants"]["REGEX_STRINGS"]["GMT_REGEX"])

        # logger strings - geolocation exceptions
        self.GeocoderUnavailable_WARNING_STRING = constants_data["constants"]["LOGGER_STRINGS"]["GeocoderUnavailable_WARNING_STRING"]
        self.GeocoderUnavailable_ERROR_STRING = constants_data["constants"]["LOGGER_STRINGS"]["GeocoderUnavailable_ERROR_STRING"]

        # Reputation years
        self.REPUTATION_YEARS = constants_data["constants"]["REPUTATION_YEARS"]

        # sleep factors in seconds for request to the website
        self.SLEEP_FACTOR = constants_data["constants for user"]["SLEEP_FACTOR"]
        # sleep factors in seconds for request to locations api
        self.SLEEP_TIME_FOR_LOCATIONS_API = constants_data["constants for user"]["SLEEP_TIME_FOR_LOCATIONS_API"]





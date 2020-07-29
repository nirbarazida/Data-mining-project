import json

data = {}

data['constants'] = {
    'NUM_INSTANCES_IN_PAGE': 36,
    'CONTINENTS_MAP': {
        'NA': 'North America',
        'SA': 'South America',
        'AS': 'Asia',
        'OC': 'Australia',
        'AF': 'Africa',
        'EU': 'Europe'
    },
    'API_WEBSITE_BASE_URL': "https://api.stackexchange.com/",
    'API_TYPE': {
    'INFO': "info"
    },
    'MAGNITUDE_MAP': {"m": 6, "k": 3},
    'REPUTATION_YEARS': (2017, 2018, 2019, 2020),
    'ORM_TABLES_RESTRICTIONS': {"COUNTRY_MAX_STRING_LENGTH": 112,
                                "CONTINENT_MAX_STRING_LENGTH": 26,
                                "NAMES_STRING_LENGTH": 200},

    'REGEX_STRINGS': {"REPUTATION_REGEX": r"var\sgraphData\s=\s(\[\S+\])",
                      "GMT_REGEX": r"GMT\s[+-]\d",
                      "ENCODE_REGEX": r"(['])([A-Za-z ]+)([\\]*)"},

    'LOGGER_STRINGS': {"OPENING_STRING": "Working on DB: {}, number of users to scrap = {},"
                                         " sleep factor = {}, Multi Process? {}",

                       "SANITY_CHECK_STRING": "Sanity check for link: {}, website: {}, page: {}, reputation: {}",
                       "WEBSITE_SCRAPP_INFO": "Website: {}, first user: {}, last user: {}",

                       "GeocoderUnavailable_WARNING_STRING": r"problem! user {} rank {} and website {}"
                                                             r" with address {}, did not scrapped, try to run again",

                       "GeocoderUnavailable_ERROR_STRING": r"Failed! user {} rank {} and website {} with address {},"
                                                           r" did not scrapped",
                       "CONNECTION_ERROR": "{} \tos environ variables are not defined or not fitting authentication."
                                           " for help check https://www.youtube.com/watch?v=IolxqkL7cD8 "
                                           "another option: couldn't form a connection with server",
                       "DB_NAME_NOT_VALID": r"Database name:{} is not valid",
                       "USER_PROBLEMATIC_COUNTRY": "user location is: '{}' - will be address as None!"
                       },
    'SQL_STATEMENTS': {
        "CHECK_DB": 'SELECT distinct(SCHEMA_NAME) FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = ' '"',

        },
    'KNOWN_COUNTRIES': {"USA": ["United States of America", "North America"],
                        "The Netherlands": ["Netherlands", "Europe"]},

    'IGNORE_NAME_IN_LOCATION_CACHE_TABLE': ["University", "Continental Europe", "Europe", "Flyover Country",
                                            "An Underground Bunker", "Down Under", "America", "World",
                                            "Pacific Ocean", "Central Europe"],

    'AUTHENTICATION': {"USER_ENV_NAME": "MySQL_USER", "PASSWORD_ENV_NAME": "MySQL_PASS"}
}

data['constants for user'] = {
    'SQL_EXTENSION': 'mysql',
    'PYTHON_DBAPI': 'pymysql',
    'DB_NAME': "stack_exchange_db",
    'WEBSITE_NAMES': ["stackoverflow", "askubuntu", "math.stackexchange", "superuser"],
    'SLEEP_FACTOR': 1.5,
    'SLEEP_TIME_FOR_LOCATIONS_API': 1.5,
    'MULTI_PROCESS': True
}

with open('mining_constants.json', 'w') as outfile:
    json.dump(data, outfile, indent=2)

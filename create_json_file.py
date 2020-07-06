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
    'MAGNITUDE_MAP': {"m": 6, "k": 3},
    'REPUTATION_YEARS': (2017, 2018, 2019, 2020)
}

data['constants for user'] = {
    'WEBSITE_NAMES': ["stackoverflow", "askubuntu", "math.stackexchange", "superuser"],
    'FIRST_INSTANCE_TO_SCRAP': 1,
    'MIN_NUM_USERS_TO_SCRAP': 30,
    'RECORDS_IN_CHUNK_OF_DATA': 5,
    'SLEEP_FACTOR': 1.5,
    'MULTI_PROCESS': True
}


with open('mining_constants.json', 'w') as outfile:
    json.dump(data, outfile, indent=2)
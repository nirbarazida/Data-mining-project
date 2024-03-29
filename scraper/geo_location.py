"""
module that uses the Geo-Locator api and generates a country and continent from
users location string that was scraped. using cache table in the database and cache values
in the Json file to avoid redundant requests
"""

from src import logger, config, geolocator, database
from geopy.exc import GeocoderUnavailable
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
import re
import time

class GeoLocation(object):

    @staticmethod
    def create_location(location_string, user_name, website_name):
        """
        workflow:
        1. finds last phrase after comma of the user location values.
        2. check if the phrase is part of the known counties phrases which were add manually
           in case that ot exists, gives the user location parameters the known values. in a case of no existence:
        3. query in database if description of location accepted as describing users location
           if it finds value in the DB, allocates these values to the user location and skipping the api request part
        4. In a case no value founded - implement a function to request location from api
        5. if finds country (user have valid country description) - checks if it is valid to add
           we ignore examples like: state names such as CA - could be appropriate to multiple countries,
            and it is not part of the phrases we manually
        :return:
        """
        new_location_name_in_website = None
        if location_string:

            last_word_in_user_location_string = location_string.rsplit(",")[-1].strip()
            if last_word_in_user_location_string in config.KNOWN_COUNTRIES:
                country, continent = config.KNOWN_COUNTRIES[last_word_in_user_location_string]

            else:
                location_row = database.query_location(last_word_in_user_location_string)

                if location_row:
                    country, continent = location_row.country, location_row.continent

                else:
                    country, continent = GeoLocation.get_country_and_continent_from_location(location_string, user_name, website_name)
                    if country \
                            and (last_word_in_user_location_string not in config.IGNORE_NAME_IN_LOCATION_CACHE_TABLE) \
                            and (last_word_in_user_location_string.istitle()):
                        new_location_name_in_website = last_word_in_user_location_string

            return country, continent, new_location_name_in_website

    @staticmethod
    def get_country_and_continent_from_location(loc_string, user_name, website_name):
        """
        finds user location (country and continent) from his location description
        because the api sometimes is unavailable (for several reasons) the function works in this form:
        1. try first time - in a case of a failure, log a warning and try again (with sleep time for not immediately
        try again (could lead to problem again)
        2. if there is a second error, log an ERROR message with the user details for scraping his location individually
        later (this feature will be completed in milestone 3)
        :param loc_string: user location description (str)
        :return: country and continent (str, str) or (None, None)
        """
        country, continent = None, None  # initiate the returned variables
        if not re.search(config.GMT_REGEX, loc_string):  # handle "GMT {-8:00}" - time zone location inputted
            try:
                country, continent = GeoLocation.geolocator_process(loc_string)
            except GeocoderUnavailable:
                logger.warning(config.GeocoderUnavailable_WARNING_STRING.format(user_name, website_name, loc_string))

                time.sleep(config.SLEEP_TIME_FOR_LOCATIONS_API)
                try:
                    country, continent = GeoLocation.geolocator_process(loc_string)
                except GeocoderUnavailable:
                    logger.error(config.GeocoderUnavailable_ERROR_STRING.format(user_name, website_name, loc_string))

        return country, continent

    @staticmethod
    def geolocator_process(loc_string):
        """
    user location will be determent by the geo-locator library. it receives the users location as written in the web
    converts it to  latitude and longitude then it will be called again to convert the latitude and longitude to
    a global unique name of country and continent.
        """
        country, continent = None, None  # initiate the returned variables
        loc = geolocator.geocode(loc_string)
        if loc:
            lat, lon = loc.latitude, loc.longitude
            time.sleep(config.SLEEP_TIME_FOR_LOCATIONS_API)
            try:
                new_loc = geolocator.reverse([lat, lon], language='en')
                country = new_loc.raw["address"]["country"]
                continent = config.continents_dict[country_alpha2_to_continent_code(
                    country_name_to_country_alpha2(country))]

            except TypeError:
                logger.warning(config.USER_PROBLEMATIC_COUNTRY.format(loc_string))

            except KeyError:
                if country in config.KNOWN_COUNTRIES:
                    country, continent = config.KNOWN_COUNTRIES[country]
            finally:
                time.sleep(config.SLEEP_TIME_FOR_LOCATIONS_API)
        return country, continent

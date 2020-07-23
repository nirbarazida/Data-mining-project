from website import Website
from ORM import Location, session, Stack_Exchange_Location
from logger import Logger
from geopy.exc import GeocoderUnavailable
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
import conf
import re
import time
from geopy.geocoders import Nominatim

logger_GeoLocation = Logger("GeoLocation").logger


class GeoLocation(object):
    geolocator = Nominatim(user_agent="stack_exchange_users", timeout=3)  # TODO : get from conf class

    def __init__(self, location_string=None, name=None, website=None):
        self._location_string = location_string # todo: your call Inbar - drop variables from UserScraper or overwrite?
        self._name = name
        self._website_name = website
        self._country = None
        self._continent = None
        self._new_location_name_in_website = None

    def create_location(self):
        if self._location_string:
            # finds last phrase after comma of the user location valus.
            last_word_in_user_location_string = self._location_string.rsplit(",")[-1].strip()
            # check if the phrase is part of the known counties phrases which were add manually
            # in case that ot exists, gives the user location parameters the known values
            if last_word_in_user_location_string in conf.KNOWN_COUNTRIES:
                self._country, self._continent = conf.KNOWN_COUNTRIES[last_word_in_user_location_string]

            else:
                # query in the table of the database that includes phrases in the websites the accepted as describing
                # users location, if it finds value in the DB, allocates these values to the user location and skipping
                # the api request part
                location_row = session.query(Location) \
                    .join(Stack_Exchange_Location) \
                    .filter(Stack_Exchange_Location.website_location == last_word_in_user_location_string) \
                    .first()

                if location_row:
                    self._country, self._continent = location_row.country, location_row.continent

                else:
                    # In this part, no value founded to the counry in our current resources. Thus, implementing function
                    # that requests location from api
                    self._country, self._continent = self.get_country_and_continent_from_location(self._location_string)
                    # if finds country (user have valid country description), checks if it is valid to add to the
                    # known phrases (it is title word (we ignore state names such as CA - could be appropriate to
                    # multiple countries), and it is not part of the phrases we manually
                    if self._country \
                            and (last_word_in_user_location_string not in conf.IGNORE_NAME_IN_LOCATION_CACHE_TABLE) \
                            and (last_word_in_user_location_string.istitle()):
                        self._new_location_name_in_website = last_word_in_user_location_string
        else:
            logger_GeoLocation.warning("XYZ")  # TODO: if using if else - write a warning in conf file and import here

    def get_country_and_continent_from_location(self, loc_string):
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
        if not re.search(conf.GMT_REGEX, loc_string):  # handle "GMT {-8:00}" - time zone location inputted
            try:
                country, continent = GeoLocation.geolocator_process(loc_string)
            except GeocoderUnavailable:
                logger_GeoLocation.warning(conf.GeocoderUnavailable_WARNING_STRING.format(self._name,
                                                                                          self._website_name, loc_string))

                time.sleep(conf.SLEEP_TIME_FOR_LOCATIONS_API)
                try:
                    country, continent = GeoLocation.geolocator_process(loc_string)
                except GeocoderUnavailable:
                    logger_GeoLocation.error(conf.GeocoderUnavailable_ERROR_STRING.format(self._name,
                                                                                          self._website_name, loc_string))

        return country, continent

    @staticmethod
    def geolocator_process(loc_string):
        """
    user location will be determent by the geo-locator library. it receives the users location as written in the web
    converts it to  latitude and longitude then it will be called again to convert the latitude and longitude to
    a global unique name of country and continent.
        """
        country, continent = None, None  # initiate the returned variables
        loc = Website.geolocator.geocode(loc_string)
        if loc:
            lat, lon = loc.latitude, loc.longitude
            time.sleep(conf.SLEEP_TIME_FOR_LOCATIONS_API)
            new_loc = Website.geolocator.reverse([lat, lon], language='en')
            try:
                country = new_loc.raw["address"]["country"]
                continent = conf.continents_dict[country_alpha2_to_continent_code(
                    country_name_to_country_alpha2(country))]

            except KeyError:
                if country in conf.KNOWN_COUNTRIES:
                    country, continent = conf.KNOWN_COUNTRIES[country]
            finally:
                time.sleep(conf.SLEEP_TIME_FOR_LOCATIONS_API)
        return country, continent

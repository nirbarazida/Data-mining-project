"""

Website - General class for websites with the format of Stack Exchange
         (for instance -stack overflow)
         create soup of pages, find last page and create soups for main topic pages

Authors: Nir Barazida and Inbar Shirizly
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from command_args import args
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable  #:TODO: manage maybe another exceptions here
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
import json

SLEEP_FACTOR = args.sleep_factor

# get constants from json file (which contains all the Constants)
JSON_FILE_NAME = "mining_constants.json"

with open(JSON_FILE_NAME, "r") as json_file:
    constants_data = json.load(json_file)

continents_dict = constants_data["constants"]["CONTINENTS_MAP"]


class Website(object):
    """
    General class for the website crawler with the format of Stack Exchange
    the class bundles several general methods:
    1. create soup for url input and sleep for the request time * factor
    2. get last main topic page for input topic (users/tags etc)
    3. get soups of each input main topic page (that contain X amount of topic domain)
    """
    geolocator = Nominatim(user_agent="stack_exchange_users", timeout=1) # TODO: check the exception - it seems that the crash don't happen even for 1, we should consider hadling error by exiting the code and rerun it

    def __init__(self, website_name):
        """
        initiates parameters of the class
        :param website_name: domain name of the website that is been scrapped (str)
        """
        self._website_name = website_name

    @property
    def website_url(self):
        return f"https://{self._website_name}.com"

    @ staticmethod
    def create_soup(url):
        """
        Static method that return soup from users url
        sleeps between each request according to the time
        that took to the request to be executed * SLEEP FACTOR
        :param url: input url (str)
        :return: soup: content of the url (BeautifulSoup)
        """
        page = requests.get(url)
        time_sleep = page.elapsed.total_seconds()
        time.sleep(time_sleep * SLEEP_FACTOR)
        soup = BeautifulSoup(page.content, "html.parser")
        return soup

    @staticmethod
    def get_num_of_last_page(url):
        """
        Static method that return the number of pages existing in the website
        for the specific topic (i.e users, tags, etc)
        :param url: input url (str)
        :return: number pages for the topic (int)
        """
        soup = Website.create_soup(url)
        pages_path = soup.find_all("a", {"class": "s-pagination--item js-pagination-item"})
        max_num_page = max({int(re.search(r'\d+', new_page["href"]).group()) for new_page in pages_path})
        return max_num_page

    def get_pages_soups(self, topic_url):
        """
        generator which returns soups for all the main topic pages
        uses the link under the "next" bottom in the previous page
        The main topic pages are pages that include a general view about many
        of the topic individuals (users, tags, etc) and from them the child class
        (such as UserAnalysis) extracts the links for each individual
        :param topic_url: first main topic url (str)
        :return: soup of the next main users page
        """
        number_of_last_page = self.get_num_of_last_page(topic_url)
        soup = Website.create_soup(topic_url)
        yield soup

        for i in range(number_of_last_page - 1):
            last_link = self.website_url + soup.find('a', {'rel': 'next'})['href']
            soup = Website.create_soup(last_link)
            yield soup

    @staticmethod
    def get_country_and_continent_from_location(loc_string):  # : TODO: move to user file, maybe cache locations?.
        country, continent = None, None # initiate the returned variables
        if not re.search(r"GMT\s[+-]\d",loc_string): # handle "GMT {-8:00}" - time zone location inputted
            loc = Website.geolocator.geocode(loc_string)
            try:
                lat, lon = loc.latitude, loc.longitude
                time.sleep(1.1) #:TODO - will this solve all the problems?!
                new_loc = Website.geolocator.reverse([lat, lon], language='en')
                country = new_loc.raw["address"]["country"]
                continent = continents_dict[country_alpha2_to_continent_code(
                    country_name_to_country_alpha2(country))]
            except AttributeError:
                pass
            except KeyError: #: TODO: move to json file
                if country == "The Netherlands":
                    country = "Netherlands"
                    continent = "Europe"
            except GeocoderUnavailable:  #:TODO - handle this more gently

                print("problem!")
            finally:
                time.sleep(1) # :TODO: calculate time to sleep
        return country, continent

"""
prepare website info to insert to the database
using an API request of the stack-exchange website
"""

import requests
from src import config


class WebsiteAPI:
    """
    class that prepare website info to insert to the database
    the data enrichment is by an api request of the stack-exchange website
    the data is converted from the json file to a dictionary that will be
    inserted to the website table in the database
    """
    def __init__(self, website_name):
        """
        initiates parameters of the class
        :param website_name: domain name of the website that is been scrapped (str)
        """
        self._website_name = website_name
        self._total_users = None
        self._total_answers = None
        self._total_questions = None
        self._answers_per_minute = None
        self._questions_per_minute = None
        self.get_website_data_api()


    @staticmethod
    def get_api_json_content(base_url, params):
        """
        get json data from the stack exchange api
        :param base_url: url with the basic
        :param params: meta data for the specific api request
        :return: json of the requested api - parsing the items
        """
        page = requests.get(base_url, params=params)
        return page.json()["items"][0]


    def get_website_data_api(self):
        """
        get json file fron the api request and arrange it to
        the instance values
        """
        api_url = config.API_WEBSITE_BASE_URL + config.API_TYPE_WEBSITE_DATA
        params = {"site": self._website_name}
        json_content = self.get_api_json_content(api_url, params)
        self._total_users = json_content["total_users"]
        self._total_answers = json_content["total_answers"]
        self._total_questions = json_content["total_questions"]
        self._answers_per_minute = json_content["answers_per_minute"]
        self._questions_per_minute = json_content["questions_per_minute"]

    @property
    def website_info(self):
        """
        getter method to create or update WebsitesT instance.
        :return: information that relevant to WebsitesT (dict)
        """
        return {
            'name': self._website_name,
            'total_users': self._total_users,
            'total_answers': self._total_answers,
            'total_questions': self._total_questions,
            'answers_per_minute': self._answers_per_minute,
            'questions_per_minute': self._questions_per_minute,
        }
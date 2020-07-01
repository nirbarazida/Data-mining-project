from website import Website
from command_args import args
from geopy.geocoders import Nominatim
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
from datetime import datetime, timedelta
import json
import re
import ast

FIRST_INSTANCE_TO_SCRAP = args.first_user


# get constants from json file (which contains all the Constants)
JSON_FILE_NAME = "mining_constants.json"
# get constants from json file (which contains all the Constants)

with open(JSON_FILE_NAME, "r") as json_file:
    constants_data = json.load(json_file)

continents = constants_data["constants"]["CONTINENTS_MAP"]
magnitude_dict = constants_data["constants"]["MAGNITUDE_MAP"]

now = datetime.now()
threshold_date = now - timedelta(days=4 * 365)
year_indexes = [-(now - datetime(year, 1, 1)).days for year in (2017, 2018, 2019, 2020)]


class User(Website, dict):

    """
    General: Class User gets the users url, scrapes all the information into class variables
    inheritance: "create_soup" from class Website.

                The idea behind dictionary inheritance is to allow the developer to protect the data that can be
                scraped into the database and prevent a scenario where the data is added / subtracted from the user.
                This feature is ready to deploy on the product demand.

                In addition, dictionary methods allows us to store the data in a structure that can be transfer
                to a Jason file without creating any additional variables. – O(n) time and space complexity.

                for clarity reasons all class variables are being declared at the top of the class. All class
                variables who needs more than one line to scrap the information are being scraped in separate blocks


    """

    num_user_dict = {}
    geolocator = Nominatim()

    def __init__(self, website_name, url):
        dict.__init__(self)
        Website.__init__(self, website_name)

        soup = Website.create_soup(url)

        User.num_user_dict[self._website_name] = User.num_user_dict.get(self._website_name,
                                                                        FIRST_INSTANCE_TO_SCRAP - 1) + 1
        self['rank'] = User.num_user_dict[self._website_name]
        self['name'] = soup.find("div", {"class": "grid--cell fw-bold"}).text
        self['country'] = None  # not all users have a valid location in profile - must keep as default none
        self['continent'] = None # same as line above
        self['year'] = None
        self['month'] = None
        #self['reputation'] = int(soup.find("div", {"class": "grid--cell fs-title fc-dark"}).text.replace(',', ''))
        self['profile_views'] = 0
        self['answers'] = None
        self['people_reached'] = None
        self['tags_names'] = []
        self['tags_scores'] = []
        self['posts'] = []
        self['reputation_now'] = int(soup.find("div", {"class": "grid--cell fs-title fc-dark"}).text.replace(',', ''))
        self['reputation_years'] = None


        """
        Defines users name and users location
        not all users have a location - thus location will stay None type
        """
        basic_info_scope = soup.find("ul", {"class": "list-reset grid gs8 gsy fd-column fc-medium"})
        basic_info_as_list = basic_info_scope.find_all_next("div", {"class": "grid gs8 gsx ai-center"})
        if basic_info_as_list[0].find('svg', {'aria-hidden': 'true', 'class': 'svg-icon iconLocation'}):
            loc = User.geolocator.geocode(basic_info_as_list[0].text.strip())
            try:
                lat, lon = loc.latitude, loc.longitude
                new_loc = User.geolocator.reverse([lat, lon], language='en')
                self['country'] = new_loc.raw["address"]["country"]
                self['continent'] = continents[country_alpha2_to_continent_code(country_name_to_country_alpha2(self['country']))]
            except AttributeError:
                pass
            except KeyError:
                if self['country'] == "The Netherlands":
                    self['continent'] = "Europe"

        for i in basic_info_as_list:
            if 'Member for' in i.text:
                member_since = datetime.strptime(i.find('span')['title'][:-1], '%Y-%m-%d %H:%M:%S')
                self["year"] = member_since.year
                self["month"] = member_since.month
            if 'profile views' in i.text:
                self['profile_views'] = int(i.text.strip().split()[0].replace(",", ""))
                break
        del basic_info_scope, basic_info_as_list

        """
        Defines users number of answers, users people reached
        """
        user_community_info = soup.find('div', {'class': 'fc-medium mb16'})
        if user_community_info:
            user_community_info = user_community_info.find_all_next('div',
                                                                    {'class': 'grid--cell fs-body3 fc-dark fw-bold'})
            self['answers'] = int(user_community_info[0].text.replace(",", ""))
            people_reached = user_community_info[2].text.strip('~')
            self['people_reached'] = int(float(people_reached[:-1]) * (10 ** magnitude_dict[people_reached[-1]]))
            del user_community_info

        """
        User tags - append the values to the users top_tag_names, top_tag_scores, number_of_posts - that are lists
        """

        all_tags_info = soup.find("div", {"id": "top-tags"})
        if all_tags_info:
            top_tag_names, top_tag_scores, number_of_posts = [], [], []
            for tag in all_tags_info.find_all_next('a', {"class": "post-tag"}):
                top_tag_names.append(tag.text)
            self['tags_names'] = top_tag_names
            for tag in all_tags_info.find_all_next('div', {"class": "grid jc-end ml-auto"}):
                top_tag_scores.append(int(tag.text.replace("\n", " ").split()[1].replace(",", "")))
                number_of_posts.append(int(tag.text.replace("\n", " ").split()[3].replace(",", "")))
            self['tags_scores'] = top_tag_scores
            self['posts'] = number_of_posts
            del all_tags_info, top_tag_names, top_tag_scores, number_of_posts

        """
        user reputation for years: [2017, 2018, 2019 ,2020]
         will evaluate years only for users registered before 2017
        """
        if self["year"] and member_since < threshold_date:
            soup_activity = self.create_soup(url + "?tab=topactivity")
            source_data = soup_activity.find("div", {"id": "top-cards"}).text
            numbers = re.search(r"var\sgraphData\s=\s(\[\S+\])", source_data)
            reputation_numbers = ast.literal_eval(numbers.group(1))
            self['reputation_years'] = [reputation_numbers[year] for year in year_indexes]


def main():
    import time
    t_start = time.perf_counter()

    url = r"https://superuser.com/users/712185/wesley"
    user_check = User("stackoverflow", url)
    print(user_check)

    t_end = time.perf_counter()
    print(f"Finished in {round(t_end - t_start, 2)} seconds")


if __name__ == '__main__':
    main()

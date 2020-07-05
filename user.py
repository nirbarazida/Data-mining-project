from website import Website
from ORM import WebsitesT, UserT, User_Tags, TagsT, Reputation, Location, engine, Base, session
import logging
from geopy.geocoders import Nominatim
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
from datetime import datetime, timedelta
import json
import re
import ast
import time


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(message)s')
file_handler = logging.FileHandler('user.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# get constants from json file (which contains all the Constants)
JSON_FILE_NAME = "mining_constants.json"

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

    milestone 2:
    because we've changed the __init__ method to be shorter - all scraping info that is longer than one line
    will became a method of class user and will be called from main.
    also, soup will become a user feature so other methods will be able to use it and we'll not need to create
    soup from main and send it to all the methods.


    """

    num_user_dict = {}

    # geolocator = Nominatim(user_agent="my-application")

    def __init__(self, website_name, url, FIRST_INSTANCE_TO_SCRAP):
        dict.__init__(self)
        Website.__init__(self, website_name)

        self._soup = Website.create_soup(url)

        User.num_user_dict[self._website_name] = User.num_user_dict.get(self._website_name,
                                                                        FIRST_INSTANCE_TO_SCRAP - 1) + 1
        self['rank'] = User.num_user_dict[self._website_name]
        self['name'] = self._soup.find("div", {"class": "grid--cell fw-bold"}).text
        self['member_since'] = None
        self['year'] = None
        self['month'] = None
        self['profile_views'] = 0
        self['answers'] = None
        self['people_reached'] = None
        self['country'] = None  # not all users have a valid location in profile - must keep as default none
        self['continent'] = None  # same as line above
        self['reputation_now'] = int(
            self._soup.find("div", {"class": "grid--cell fs-title fc-dark"}).text.replace(',', ''))
        self['reputation_years'] = {}  # must be emty dict so ORM will be able to map it
        self['tags'] = None

    def personal_info(self):
        """
        Defines users name and users location
        not all users have a location - thus location will stay None type
        """
        basic_info_scope = self._soup.find("ul", {"class": "list-reset grid gs8 gsy fd-column fc-medium"})
        basic_info_as_list = basic_info_scope.find_all_next("div", {"class": "grid gs8 gsx ai-center"})
        # if basic_info_as_list[0].find('svg', {'aria-hidden': 'true', 'class': 'svg-icon iconLocation'}):
        # loc = User.geolocator.geocode(basic_info_as_list[0].text.strip())
        # try:
        #     lat, lon = loc.latitude, loc.longitude
        #     new_loc = User.geolocator.reverse([lat, lon], language='en')
        #     self['country'] = new_loc.raw["address"]["country"]
        #     self['continent'] = continents[country_alpha2_to_continent_code(
        #                          country_name_to_country_alpha2(self['country']))]
        # except AttributeError:
        #     pass
        # except KeyError:
        #     if self['country'] == "The Netherlands":
        #         self['continent'] = "Europe"

        for i in basic_info_as_list:
            if 'Member for' in i.text:
                self['member_since'] = datetime.strptime(i.find('span')['title'][:-1], '%Y-%m-%d %H:%M:%S')
                self["year"] = self['member_since'].year
                self["month"] = self['member_since'].month
            if 'profile views' in i.text:
                self['profile_views'] = int(i.text.strip().split()[0].replace(",", ""))
                break

    def professional_info(self):
        """
        Defines users number of answers and users people reached
        """
        user_community_info = self._soup.find('div', {'class': 'fc-medium mb16'})
        if user_community_info:
            user_community_info = user_community_info.find_all_next('div',
                                                                    {'class': 'grid--cell fs-body3 fc-dark fw-bold'})
            self['answers'] = int(user_community_info[0].text.replace(",", ""))
            people_reached = user_community_info[2].text.strip('~')
            self['people_reached'] = int(float(people_reached[:-1]) * (10 ** magnitude_dict[people_reached[-1]]))

    def reputation_hist(self, url):
        """
        user reputation for years: [2017, 2018, 2019 ,2020]
         will evaluate years only for users registered before 2017
        """
        if self['member_since']:
            if self['member_since'] < threshold_date:
                soup_activity = self.create_soup(url + "?tab=topactivity") #todo: INBAR -check url that method gets
                source_data = soup_activity.find("div", {"id": "top-cards"}).text
                numbers = re.search(r"var\sgraphData\s=\s(\[\S+\])", source_data)
                reputation_numbers = ast.literal_eval(numbers.group(1))
                self['reputation_years'] = {'reputation_' + str(year): reputation_numbers[year] for year in
                                            year_indexes}

    def create_tags(self):
        """
        scraps all tags info from user page
        rapes it in list of tuples [(tag name, tag score, tag answers) ..]
        """
        # create a scoop of tags in all the html soup
        all_tags_info = self._soup.find("div", {"id": "top-tags"})

        # user might not have tags
        if all_tags_info:
            tags = []
            for tag in all_tags_info.find_all_next('a', {"class": "post-tag"}):
                tags.append([tag.text])
            for i, tag in enumerate(all_tags_info.find_all_next('div', {"class": "grid jc-end ml-auto"})):
                tags[i].append(int(tag.text.replace("\n", " ").split()[1].replace(",", "")))
                tags[i].append(int(tag.text.replace("\n", " ").split()[3].replace(",", "")))
        self['tags'] = tags

    def scrap_info(self, link): #todo: INBAR -check url that reputation_hist gets
        """
        calls to all the methods of user to scrap information.
        created to decrees amount of lines in main file.
        reputation_hist method most be last - so self['member_since'] will get a value.
        """
        self.create_tags()
        self.professional_info()
        self.personal_info()
        self.reputation_hist(link)

    def get_user_info(self):
        return {
            'rank': self['rank'],
            'name': self['name'],
            'member_since': self['member_since'],
            'year': self['year'],
            'month': self['month'],
            'profile_views': self['profile_views'],
            'answers': self['answers'],
            'people_reached': self['people_reached'],
        }

    def get_location(self):
        return {
            'country': self['country'],
            'continent': self['continent']
        }

    def get_reputation(self):
        return {**{'reputation_now': self['reputation_now']}, **self['reputation_years']}

    def insert_user(self):
        tic = time.perf_counter()
        web = session.query(WebsitesT).filter(WebsitesT.name == self._website_name).first()

        loc = session.query(Location).filter(Location.country == self['country']).first()
        if loc is None:
            loc = Location(**self.get_location())
            session.add(loc)
            session.commit()

        # create new user entrance in table user with location and website and commit it
        user = UserT(location=loc, website_id=web.id, **self.get_user_info())
        session.add(user)
        session.commit()

        # create user Reputation, connects it to the user and commit it. CAN'T do it before committing user
        print(self.get_reputation())
        rep = Reputation(user_id=user.id, **self.get_reputation())
        session.add(rep)
        session.commit()

        for tag in self['tags']:
            new_tag = session.query(TagsT).filter(TagsT.name == tag[0]).first()
            if new_tag is None:
                new_tag = TagsT(name=tag[0])
                session.add(new_tag)
                session.commit()
            ass = User_Tags(score=tag[1], posts=tag[2])
            ass.user_id = user.id
            new_tag.users.append(ass)
            session.commit()

        toc = time.perf_counter()
        logger.info(
            f"Finished insert ( {self['name'].encode('utf-8')} ) to table {self._website_name} in {round(toc - tic, 4)} seconds")


# to be able to work with user.py file undependable from main.py
def create_table_website(web_names):
    """
    get a list of all the websites that the user wants to scrap from
    create new entries in table websites with those names
    """

    for name in web_names:
        web = session.query(WebsitesT).filter(WebsitesT.name == name).first()
        if web is None:
            web = WebsitesT(name=name, last_scraped=0)
            session.add(web)
            session.commit()


def main():
    # Drops all tables. del when DB is ready
    # Base.metadata.drop_all(engine)

    # creates the DB
    Base.metadata.create_all(engine)

    create_table_website(['stackoverflow'])
    import time
    t_start = time.perf_counter()

    url = r"https://stackoverflow.com/users/3962914/ronak-shah"
    user_check = User("stackoverflow", url)

    user_check.create_tags()
    user_check.reputation_hist(url)
    user_check.professional_info()
    user_check.personal_info()
    user_check.insert_user()

    print(user_check)

    t_end = time.perf_counter()
    print(f"Finished in {round(t_end - t_start, 2)} seconds")


if __name__ == '__main__':
    main()

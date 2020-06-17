from website import Website
from user_analysis import UserAnalysis
from datetime import datetime
import json

with open("data_mining_constants.txt", "r") as json_file:
    constants_data = json.load(json_file)

FIRST_INSTANCE_TO_SCRAP = constants_data["constants for user"]["FIRST_INSTANCE_TO_SCRAP"]


class User(UserAnalysis, dict):

    num_user_dict = {}

    """
    inherit all the class website features
    gets also the url of the user
    creats a new user based on the url
    """

    def __init__(self, website_name, url):
        dict.__init__(self)
        Website.__init__(self, website_name)

        self.soup = Website.create_soup(url)

        User.num_user_dict[self._website_name] = User.num_user_dict.get(self._website_name,
                                                                        FIRST_INSTANCE_TO_SCRAP - 1) + 1
        self['rank'] = User.num_user_dict[self._website_name]
        self['name'] = self.soup.find("div", {"class": "grid--cell fw-bold"}).text
        self['location'] = None  # not all users have a location in profile - must keep as default none
        self['member since'] = None
        self['reputation'] = int(self.soup.find("div", {"class": "grid--cell fs-title fc-dark"}).text.replace(',', ''))
        self['total number of answers'] = None
        self['number of people the user reached'] = None
      #  self['highest rating for one post'] = self.soup.find("span", {"class": "grid--cell vote accepted"}).text
        self['top tags names'] = []
        self['top tags scores'] = []
        self['number of posts'] = []


        # All the functions are in __init__ because we're defining new values to class user
        def basic_info(self):
            """
            gets self and defines users name and users location
            not all users have a location - thus location will stay None type
            """
            basic_info_scope = self.soup.find("ul", {"class": "list-reset grid gs8 gsy fd-column fc-medium"})
            basic_info_as_list = basic_info_scope.find_all_next("div", {"class": "grid gs8 gsx ai-center"})
            if basic_info_as_list[0].find('svg', {'aria-hidden': 'true', 'class': 'svg-icon iconLocation'}):
                self['location'] = basic_info_as_list[0].text.strip()
            for i in basic_info_as_list:
                if 'Member for' in i.text:
                    self['member since'] = datetime.strptime(i.find('span')['title'][:10], '%Y-%m-%d').date()
            del basic_info_scope, basic_info_as_list

        def user_comunity(self):
            """
            gets self and defines users number of answers, users people reached
            """
            user_community_info = self.soup.find('div', {'class': 'fc-medium mb16'}).find_all_next \
                ('div', {'class': 'grid--cell fs-body3 fc-dark fw-bold'})
            self['total number of answers'] = user_community_info[0].text
            self['number of people the user reached'] = user_community_info[2].text.strip('~')
            del user_community_info

        def user_tags(self):
            """
            gets self and append the values to the users top_tag_names, top_tag_scores, number_of_posts - that are lists
            """
            top_tag_names, top_tag_scores, number_of_posts = [], [], []
            all_tags_info = self.soup.find("div", {"id": "top-tags"})
            for tag in all_tags_info.find_all_next('a', {"class": "post-tag"}):
                top_tag_names.append(tag.text)
            self['top tags names'] = top_tag_names
            for tag in all_tags_info.find_all_next('div', {"class": "grid jc-end ml-auto"}):
                top_tag_scores.append(tag.text.replace("\n", " ").split()[1])
                number_of_posts.append(tag.text.replace("\n", " ").split()[3])
            self['top tags scores'] = top_tag_scores
            self['number of posts'] = number_of_posts
            del all_tags_info, top_tag_names, top_tag_scores, number_of_posts

        basic_info(self)  # creates: ['location'] , ['member since']
        user_comunity(self)  # creates: ['total number of answers'], ['number of people the user reached']
        user_tags(self)  # creates: ['top tags names'] , ['top tags scores'], ['number of posts']
        del self.soup  # :TODO: change self.soup to variable and not class variable





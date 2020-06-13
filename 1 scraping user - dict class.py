"""
created by: Nir Barazida
Date: 06/11/2020
script goal: create a class named user that scraps all the user info from stackoverflow website
last modification: created a Dict_Methods class; class user inherent from it and becomes a dict
"""

"""
Nir's TODO:
2. החלפה של K וM לאפסים בעזרת רגקס והחלפה למשתנה מסוג מספר
3. בדיקה לשגיאה אם הרשימה בתיוגים קטנה מ6 -בעיה בהכנסה הראשונה
"""

# Import libraries
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from collections.abc import MutableMapping




class Dict_Methods(MutableMapping):
    """
    a class that inherent some of the dict methods by using MutableMapping
    the user class will inherent this class and will become a class with dict methods and must important iterable 
    """
    def __init__(self):
        self.mapping = dict()
        self.update(dict())
        self.allowed_keys = ['name', 'location', 'member since', 'reputation', 'total number of answers',
                    'number of people the user reached', 'highest rating for one post', 'top tags names',
                    'top tags scores', 'number of posts']
        self.keys_r_list = ['top tags names','top tags scores', 'number of posts']

    def __getitem__(self, key):
        """return the user info based on the input key"""
        try:
            return self.mapping[key]
        except KeyError:
            print('No such key')

    def __setitem__(self, key, value):
        """changes the user info based on the input key - only for keys from the list"""
        # if key not in self.allowed_keys:
        #     raise KeyError("please enter a key from: {} or go to class Dict_Methods and cahnge the self.allowed_keys".format(self.allowed_keys))
        # elif key in self.keys_r_list and type(value) != list:
        #     raise ValueError('Tags must be a list')
        # else:
        self.mapping[key] = value

    def __delitem__(self, key):
        """delete users info based on key"""
        # try:
        del self.mapping[key]
        # except:
        #     KeyError ('No such key')

    def __iter__(self):
        return iter(self.mapping)

    def __len__(self):
        """returns the number of keys in user (10) """
        return len(self.mapping)

    def __repr__(self):
        """defining a default format prints the user info in a dict format - class user will change this format"""
        # try:
        return "{} User Information:\n{}".format(self.mapping['name'], self.mapping)
        # except KeyError:
            # print('the user has no name! how could it be?')


class user(Dict_Methods):  # What am I inheriting from website?
    """
    inherit all the class website features
    gets also the url of the user
    creats a new user based on the url
    """

    def __init__(self, url='https://stackoverflow.com/users/22656/jon-skeet'):  # The user soup will not inherited
        Dict_Methods.__init__(self)

        page = requests.get(url)
        self.soup = BeautifulSoup(page.content, "html.parser")

        # some of user class variables will be defined by functions. there is no need for the definition here with None
        # HOWEVER - we'll keep it for "first readers" to better understand the class.
        self['name'] = self.soup.find("div", {"class": "grid--cell fw-bold"}).text
        self['location'] = None  # not all users have a location in profile - must keep as default none
        self['member since'] = None
        self['reputation'] = int(self.soup.find("div", {"class": "grid--cell fs-title fc-dark"}).text.replace(',',''))
        self['total number of answers'] = None
        self['number of people the user reached'] = None
        self['highest rating for one post'] = self.soup.find("span",{"class": "grid--cell vote accepted"}).text
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

        basic_info(self) # creates: ['location'] , ['member since']
        user_comunity(self) # creates: ['total number of answers'], ['number of people the user reached']
        user_tags(self) # creates: ['top tags names'] , ['top tags scores'], ['number of posts']

    def __repr__(self):
        """printing function - changes the inherited repr function """

        return "User name: " + str(self['name']) + "\nUser location: " + str(
            self['location']) + "\nMember since: " + str(self['member since']) \
               + "\nUser reputation: " + str(self['reputation']) + "\nUser total number of answers: " + str(
            self['total number of answers']) \
               + "\nPepole that the user reached: " + str(
            self['number of people the user reached']) + "\nUser top votes for one post: " \
               + str(self['highest rating for one post'])

import time


list_url = ['https://stackoverflow.com/users/22656/jon-skeet', 'https://stackoverflow.com/users/1144035/gordon-linoff', \
            'https://stackoverflow.com/users/6309/vonc', 'https://stackoverflow.com/users/157882/balusc', 'https://stackoverflow.com/users/2084798/christian-matthew',\
            'https://stackoverflow.com/users/3436943/chevy-mark-sunderland', 'https://stackoverflow.com/users/2748531/user2748531']
tot = 0
for j in range (2):
    for i in list_url:
        print('%%%%%')
        # timeit.timeit(f'{user(i)}')
        tic = time.perf_counter()
        print(user(i))
        toc = time.perf_counter()
        print(toc - tic)
        tot += toc - tic

print (tot)

# 152.2925286
# 145.25685280000002 without except
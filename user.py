from website import Website
from command_args import args

FIRST_INSTANCE_TO_SCRAP = args.first_user


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

    def __init__(self, website_name, url):
        dict.__init__(self)
        Website.__init__(self, website_name)

        soup = Website.create_soup(url)

        User.num_user_dict[self._website_name] = User.num_user_dict.get(self._website_name,
                                                                        FIRST_INSTANCE_TO_SCRAP - 1) + 1
        self['rank'] = User.num_user_dict[self._website_name]
        self['name'] = soup.find("div", {"class": "grid--cell fw-bold"}).text
        self['location'] = None  # not all users have a location in profile - must keep as default none
        self['member since'] = None
        self['reputation'] = int(soup.find("div", {"class": "grid--cell fs-title fc-dark"}).text.replace(',', ''))
        self['profile views'] = '0'
        self['total number of answers'] = None
        self['number of people the user reached'] = None
        self['top tags names'] = []
        self['top tags scores'] = []
        self['number of posts'] = []

        """
        Defines users name and users location
        not all users have a location - thus location will stay None type
        """
        basic_info_scope = soup.find("ul", {"class": "list-reset grid gs8 gsy fd-column fc-medium"})
        basic_info_as_list = basic_info_scope.find_all_next("div", {"class": "grid gs8 gsx ai-center"})
        if basic_info_as_list[0].find('svg', {'aria-hidden': 'true', 'class': 'svg-icon iconLocation'}):
            self['location'] = basic_info_as_list[0].text.strip()
        for i in basic_info_as_list:
            if 'Member for' in i.text:
                self['member since'] = (i.find('span')['title'][:10])
            if 'profile views' in i.text:
                self['profile views'] = i.text.strip().split()[0]
                break
        del basic_info_scope, basic_info_as_list

        """
        Defines users number of answers, users people reached
        """
        user_community_info = soup.find('div', {'class': 'fc-medium mb16'})
        if user_community_info:
            user_community_info = user_community_info.find_all_next('div',
                                                                    {'class': 'grid--cell fs-body3 fc-dark fw-bold'})
            self['total number of answers'] = user_community_info[0].text
            self['number of people the user reached'] = user_community_info[2].text.strip('~')
            del user_community_info

        """
        User tags - append the values to the users top_tag_names, top_tag_scores, number_of_posts - that are lists
        """

        all_tags_info = soup.find("div", {"id": "top-tags"})
        if all_tags_info:
            top_tag_names, top_tag_scores, number_of_posts = [], [], []
            for tag in all_tags_info.find_all_next('a', {"class": "post-tag"}):
                top_tag_names.append(tag.text)
            self['top tags names'] = top_tag_names
            for tag in all_tags_info.find_all_next('div', {"class": "grid jc-end ml-auto"}):
                top_tag_scores.append(tag.text.replace("\n", " ").split()[1])
                number_of_posts.append(tag.text.replace("\n", " ").split()[3])
            self['top tags scores'] = top_tag_scores
            self['number of posts'] = number_of_posts
            del all_tags_info, top_tag_names, top_tag_scores, number_of_posts

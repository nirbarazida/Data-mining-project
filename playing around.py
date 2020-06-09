# Import libraries
import requests
from bs4 import BeautifulSoup

def get_user_info(url):
    # Request URL
    page = requests.get(url)

    # Fetch webpage
    soup = BeautifulSoup(page.content, "html.parser")

    # Scraping Data questions grid--cell fl1

    # user profile
    user = {}
    user['user name'] = soup.find("div", {"class": "grid--cell fw-bold"}).text
    user['user location'] = soup.find("div", {"class": "grid--cell fl1"}).text

    user['user reputation'] = soup.find("div", {"class": "grid--cell fs-title fc-dark"}).text

    # users community info
    helper = soup.find('div', {'class': 'fc-medium mb16'})
    user_community_info = helper.find_all_next('div', {'class': 'grid--cell fs-body3 fc-dark fw-bold'})
    user['user number of answers'] = user_community_info[0].text
    user['user people reached'] = user_community_info[2].text.strip('~')

    user['user top post votes'] = soup.find("span", {"class": "grid--cell vote accepted"}).text

    all_tags_info = soup.find("div", {"id": "top-tags"})
    user_tag_names = all_tags_info.find_all_next('a', {"class": "post-tag"})
    for i in range(len(user_tag_names)):
        user_tag_names[i] = user_tag_names[i].text

    user_tag_out_scope = all_tags_info.find_all_next('div', {"class": "grid jc-end ml-auto"})
    user_tag_scores, user_tags_number_of_posts = [], []
    for i in range(len(user_tag_out_scope)):
        user_tag_scores.append(user_tag_out_scope[i].text.replace("\n", " ").split()[1])
        user_tags_number_of_posts.append(user_tag_out_scope[i].text.replace("\n", " ").split()[3])

    for i in range(len(user_tag_names)):
        user[user_tag_names[i] + ' scores'] = user_tag_scores[i]
        user[user_tag_names[i] + ' number of posts'] = user_tags_number_of_posts[i]

    del user_tag_out_scope, helper, user_community_info, all_tags_info



    return user


print(get_user_info('https://stackoverflow.com/users/6309/vonc'))

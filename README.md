# Data-mining-project
ITC - Data mining project - *StackExchange* Analyse. <br />
 main focus - **Stack Overflow**

### Authors
Nir Barazida and Inbar Shirizly

## Goals

This project scrapes websites and analyses the data retrieved.

The websites that are analysed are under the group of [StackExchange](https://stackexchange.com/sites) main websites:
1. https://stackoverflow.com/
2. https://math.stackexchange.com/
3. https://askubuntu.com/
4. https://superuser.com/


The analysis focuses on data retrieved from the top individual users of several websites
 (according to the website's all-time rank (since the website's establishment
 until scrapper was run)).

#### Main insights the program attempts to present:
- Presents insights about each country and continent:
    1. [Reputation](https://stackoverflow.com/help/whats-reputation#:~:text=You%20gain%20reputation%20when%3A,your%20answer%3A%20%2B%20full%20bounty%20amount)
    2. Total answers, profile views and people reached 
    3. [People reached](https://meta.stackoverflow.com/questions/290491/what-does-people-reached-signify-and-how-is-it-calculated#:~:text=2%20Answers&text=The%20people%20reached%20statistic%20is,equivalent%20with%20a%20single%20user.)
    4. [Top tags](https://stackoverflow.com/help/tagging) - posts and score
    5. reputation trends between 2017-2020
    
- Presents the amount of top users over time - according to the registration date
 of **current** top users
 
 


 ## install and usage 
- [Requirements.txt](https://github.com/nirbarazida/Data-mining-project/blob/master/requirements.txt) - The project dependencies can be found in the requirements.txt file in the current repository
- first and foremost - one who is using our program must have a MySQL account. the program create and commit information
 to a MySQL data-base. don't worry if you don't have a dedicated data-base for this information - we'll create it for you.
- To connect to the user MySQL account one has to create environment variables of user name and password. this way
we'll protect your sensitive information and make sure that it won't show on github and/or in the command line argument.\
To create environment variables you can use this guid [Corey Schafer - Environment Variables](https://www.youtube.com/watch?v=IolxqkL7cD8) \
please store the variable with the names:
    1. MySQL_PASS - password. 
    2. MySQL_USER - user name.


## Program work flow

![image](https://github.com/nirbarazida/Data-mining-project/blob/master/figures/Data%20mining%20workflow.jpeg)

For now, this project is in milestone 3, hence the program crawls from the 
input websites and commit the data to the user MySQL data-base. <br/>
In the future, the program will store the data on a remote data base that
is located on a server, and display the insights in a dashboard

## Project implementation
The project implementation plan is to use OOP because of it's diversity and time optimization.\
The opportunity to implement scraping features on different websites, using the same project with minor changes in the HTML page, gives the project a significant advantage.

To approach the diversity problem we decided to create 3 different class:
- **Website**
- **User analysis**
- **UserScraper**
- **User**

 The first two are general and have little dependence on the website HTML.
 The third and fourth class are all dedicated to scraping the information and very much adjusted to the specific website and objects that we are scraping.
  
 ### Class Flow- Chart
 
![image](https://github.com/nirbarazida/Data-mining-project/blob/master/figures/Class%20flow%20chart%20MS3.jpeg)  

- **Class Website:** \
    General class for the website crawler with the format of Stack Exchange

- **Class User analysis:** \
    Class for user analysis in a the website that get links for each individual user page

- **UserScraper:**\
    Receives the users url and scrapes all the information into class variables

- **Class User:** \
    Inherent from class UserScraper the methods to scrap information about a user into class variables.\
    Receives the users url, scrapes all the information into class variables and eventually will commit all the 
    information to a data base using SQLAlchemy ORM.

 In addition to the scraping abilities we added an API ability to receive information about every website that is being scraped using StackExchange API.
 After creating all four class that ables us to scrap the data and the API ability, we'll start working on the data-base that stores
 the information. To crate the data-base we will use SQLAlchemy based on ORM. This way we will be able to query
 and manipulate the database using object-oriented code instead of writing SQL.
 the implantation of the above can be shown in the [ORM.py](https://github.com/nirbarazida/Data-mining-project/blob/master/ORM.py) file
 

## Database  - ERD

![image](https://github.com/nirbarazida/Data-mining-project/blob/master/figures/ERD.JPG)

Tables description:

- `users` - contains information of the indivdual user - contain users from all
the websites together, distinguished by `website_id`.
- `websites` - table related to users (one website to many users) - stores general information about the website from StackExchange API.
- `tags` - name of tag - connected to a relation table `user_tags` - which contains
the score and number of posts of the tag to the each user (`users` - `tags` = many to many)
- `reputation` - reputation of the user, including data from each year between 2017-2020
related to `users` table (one user for one reputation entity)
- `location` - country and continent of users (one location for many users)
- `stack_exchange_location` - table that stores the users last phrase of location 
description, using attitude of *dynamic programming* - using these description to save
api requests (if the description already exists during the scrap process).
(one location_id for many website_location (the description))


## Features

In the command line arguments the user will be able to use the following features:

- **NUM_USERS_TO_SCRAP** - amount of users that will be scrapped in the current execution. default users to scrap is 10

- **WEBSITE_NAMES** - list of websites that the program will scrap. Note that they must be part of StackExchange group.

- **Multiprocessing** - when this mode is on, the program will scrap from each
of the input WEBSITE_NAMES concurrently using Multiprocessing. If the 
mode is turned off  it will run over this list in a loop. default value is False.

- **DB_NAME** - The database name that the user wants to scrap the information to. if one dose not exist the program
 will create one for him with the new name. default name is 'stack_exchange_db'

## Files
- #### **src**:
    - [__init__.py](https://github.com/nirbarazida/Data-mining-project/blob/master/src/__init__.py) - when importing src file to main will initialize general process such set connection, create engine etc.
    - [conf.py](https://github.com/nirbarazida/Data-mining-project/blob/master/src/conf.py) - configuration file, generate all important values from json file and from the command line input
    - [general.py](https://github.com/nirbarazida/Data-mining-project/blob/master/src/general.py) - general function that are being needed in multiple python file.
    - [geo_location.py](https://github.com/nirbarazida/Data-mining-project/blob/master/src/geo_location.py) - file contains three nested function that receives a general location string and retrieves a generic country and continent   
    - [logger.py](https://github.com/nirbarazida/Data-mining-project/blob/master/src/logger.py) - file contains class logger - for general logger format.
    - [ORM.py](https://github.com/nirbarazida/Data-mining-project/blob/master/src/ORM.py) - file that defines schema using ORM - create tables and all relationships between the tables in the database.
    - [user.py](https://github.com/nirbarazida/Data-mining-project/blob/master/src/user.py) - includes the class User(UserScraper) - extracts the data for the individual user and add it to the relevant tables in the data-base.
    - [user_analysis.py](https://github.com/nirbarazida/Data-mining-project/blob/master/src/user_analysis.py) - includes the class UserAnalysis(Website) - create a generator of links for each individual user page.
    - [user_scraper.py](https://github.com/nirbarazida/Data-mining-project/blob/master/src/user_scraper.py) - includes the class UserScraper(Object) - Receives the users url and scrapes all the information into class variables
    - [website.py](https://github.com/nirbarazida/Data-mining-project/blob/master/src/website.py) - includes the class Website(object) - create soup of pages, find last page and create soups for main topic pages.
    - [working_with_database.py](https://github.com/nirbarazida/Data-mining-project/blob/master/src/working_with_database.py) - file that contains most of the function which CRUD with the database.
    
- [create_json_file.py](https://github.com/nirbarazida/Data-mining-project/blob/master/create_json_file.py) - python file that generate the mining_constants.json
- [mining_constants.json](https://github.com/nirbarazida/Data-mining-project/blob/master/mining_constants.json) - json format file contains the constants for all the program.
                               the conf.py parse the json into class variables. The program will only use conf.py to import different variables. 
- [requirements.txt](https://github.com/nirbarazida/Data-mining-project/blob/master/requirements.txt) - file with all the packages and dependencies of the project.

## Sources
##### [Corey Schafer - Python tutorials](https://www.youtube.com/user/schafer5):

- [Python OOP Tutorials - Working with Classes](https://www.youtube.com/watch?v=ZDa-Z5JzLYM&list=PL-osiE80TeTsqhIuOqKhwlXsIBIdSeYtc)
- [Web Scraping with BeautifulSoup and Requests](https://www.youtube.com/watch?v=ng2o98k983k&t=1120s)
- [Generators](https://www.youtube.com/watch?v=bD05uGo_sVI)
- [Multiprocessing](https://www.youtube.com/watch?v=fKl2JW_qrso)

##### Web scraping:

[Web scraping with Python from   A to Z, ITC](https://www.itc.tech/web-scraping-with-python-a-to-z/)

##### Defining schema using ORM:

- [sqlalchemy documentation](https://docs.sqlalchemy.org/en/13/core/engines.html#sqlite)
- [basic orm coverage](https://www.fullstackpython.com/object-relational-mappers-orms.html)
- [defining schema using SQLAlchemy ORM](https://overiq.com/sqlalchemy-101/defining-schema-in-sqlalchemy-orm/)

##### API:
- [StackExchange API](https://api.stackexchange.com/)

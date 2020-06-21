# Data-mining-project
ITC - Data mining project - *StackExchange* Analyse
main focus - **Stack Overflow**

### Authors
Nir Barazida and Inbar Shirizly

## Goals

This project scrapes websites and analyses the data retrieved.

The websites that are analysed are under the group of [StackExchange](https://stackexchange.com/sites) main websites:
1. https://stackoverflow.com/
2. https://math.stackexchange.com/
3. https://askubuntu.com/


The analysis focuses on data retrieved from the top **1000** individual users
 (according to the website's all-time rank (since the website's establishment
 until scrapper was run)) .

#### Main insights the program attempts to present:
- Presents insights about each country:
    1. [Reputation](https://stackoverflow.com/help/whats-reputation#:~:text=You%20gain%20reputation%20when%3A,your%20answer%3A%20%2B%20full%20bounty%20amount)
    2. Total answers 
    3. [People reached](https://meta.stackoverflow.com/questions/290491/what-does-people-reached-signify-and-how-is-it-calculated#:~:text=2%20Answers&text=The%20people%20reached%20statistic%20is,equivalent%20with%20a%20single%20user.)
    4. [Top tags](https://stackoverflow.com/help/tagging) 
    
- Presents the amount of top users over time - according to the registration date
 of **current** top users


 ## install
[Requirements file](https://github.com/nirbarazida/Data-mining-project/blob/master/requirements.txt) \
The project dependencies can be found in the requirements.txt file in the current repository
## Program work flow

![image](https://raw.githubusercontent.com/nirbarazida/Data-mining-project/master/Data%20mining%20workflow.jpeg)

For now, this project is in milestone 1, hence the program crawls from the 
input websites and **prints** each individual user data. <br/>
In the future, the program will store the data which was retrieved and 
upload it to MySQL database, and display the insights in a dashboard

## Project implementation
The project implementation plan is to use OOP because of it's diversity and time optimization.\
The opportunity to implement scraping features on different websites, using the same project with minor changes in the HTML page, gives the project a significant advantage.

To approach the diversity problem we decided to create 3 different class:
- **Website**
- **User analysis**
- **User**

 The first two are general and have little dependence on the website HTML.
 The third class is all dedicated to scraping the information and very much adjusted to the specific website we are scraping.
 
 ### Class Flow- Chart
 
![image](https://raw.githubusercontent.com/nirbarazida/Data-mining-project/master/Class%20flow%20chart.jpeg)  

- **Class Website:** \
    General class for the website crawler with the format of Stack Exchange

- **Class User analysis:** \
    Class for user analysis in a the website that get links for each individual user page

- **Class User** \
    Receives the users url, scrapes all the information into class variables

## Features

In the json file "data_mining_constants.txt", one can find options for 
scrapping the data. It will be referred to as the following features:

- **WEBSITE_NAMES** - list of websites that the program will scrap. Note that they must be part of StackExchange group.

- **FIRST_INSTANCE_TO_SCRAP** - index of the first user that will be 
scrapped. Allows to scrap more users by running the program several times (could be on different computers)
and scrap different users.

- **NUM_USERS_TO_SCRAP** - amount of users that will be scrapped in the current execution

- **RECORDS_IN_CHUNK_OF_DATA** - the chunk of data that will be uploaded to the database in each request (now only prints when it
reaches the chosen amount). This saves a pre-chosen amount of user records on the computer 
between each connection with the database, allowing for more agility
between storage and time efficiency

- **SLEEP_FACTOR** - for preventing crawl blockage each time the program
 requests url from website. It sleeps the same 
amount of time the request took, times this factor. This feature allows
the user to pick  a factor that will allow the program to run as fast
as possible while avoiding blockage.

- **THREADING** - when this mode is on, the program will scrap from each
of the input WEBSITE_NAMES concurrently using threading. If the 
mode is turned off  it will run over this list in a loop


## Sources
[Corey Schafer - Python tutorials](https://www.youtube.com/user/schafer5):

- [Python OOP Tutorials - Working with Classes](https://www.youtube.com/watch?v=ZDa-Z5JzLYM&list=PL-osiE80TeTsqhIuOqKhwlXsIBIdSeYtc)
- [Web Scraping with BeautifulSoup and Requests](https://www.youtube.com/watch?v=ng2o98k983k&t=1120s)
- [Generators](https://www.youtube.com/watch?v=bD05uGo_sVI)
- [Threading](https://www.youtube.com/watch?v=IEEhzQoKtQU)

[Web scraping with Python from   A to Z, ITC](https://www.itc.tech/web-scraping-with-python-a-to-z/)




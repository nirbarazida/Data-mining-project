# Data-mining-project
ITC - Data mining project - StackExchange Analyse
main focus - **Stack Overflow**

### Authors
Nir Barazida and Inbar Shirizly

## Goals
Analyse websites under the group of [StackExchange](https://stackexchange.com/sites) main websites:
1. https://stackoverflow.com/
2. https://math.stackexchange.com/
3. https://askubuntu.com/

The analysis is focusing on data retrieved from the top **1000** individual users
 (according to the website rank for all-time (since the website established
 until running the scrapper)) .

#####Main insights the program attempts to presents:
- Present insight about each country:
    1. [Reputation](https://stackoverflow.com/help/whats-reputation#:~:text=You%20gain%20reputation%20when%3A,your%20answer%3A%20%2B%20full%20bounty%20amount)
    2. Total answers 
    3. [People reached](https://meta.stackoverflow.com/questions/290491/what-does-people-reached-signify-and-how-is-it-calculated#:~:text=2%20Answers&text=The%20people%20reached%20statistic%20is,equivalent%20with%20a%20single%20user.)
    4. [Top tags](https://stackoverflow.com/help/tagging) 
    
- Present amount of top users existing over time - according to registration date
 (when the top users are users that are **now** top users) 


This project is scrapping websites and analysing the data. 


## install

The project dependencies can be found in the requirements.txt file in the current repository

## Program work flow

![image](https://raw.githubusercontent.com/nirbarazida/Data-mining-project/master/Data%20mining%20workflow.jpeg)

For now, this project is in milestone 1, hence the program crawls from the 
input websites and **prints** each individual user data. <br/>
In the future, the program will store the data which was retrieved and 
upload it to MySQL database, and display the insights in a dashboard


## Features

In the json file "data_mining_constants.txt" one can find the options for 
scrapping the data, which will be referred as features:

- **WEBSITE_NAMES** - list of websites that the program will scrap. note that they must be part of StackExchange group.

- **FIRST_INSTANCE_TO_SCRAP** - index of the first user that will be scrapped, allows to scrap more users by running the program several times (could be on different computers)
and scrap different users.

- **MIN_NUM_USERS_TO_SCRAP** - amount of users that will be scrapped in the current execution

- **RECORDS_IN_CHUNK_OF_DATA** - the chunk of data that will be uploaded to the database in each request (now only prints when it
reaches the chosen amount), allows to relay save minimal amount of user records on the computer 
between each connection with the database

- **SLEEP_FACTOR** - for preventing crawl blockage, each time the program requests url from website, it sleeps the same 
amount of time the request took, times this factor. this feature allows
the user to pick factor that will allow crawling in one hand and inspire to run the program as fast as possible

- **THREADING** - when this mode is on, the program will scrap from each
of the input WEBSITE_NAMES concurrently using threading. if not, it will run over
this list in a for loop

## Classes

### Chart-flow


## Sources
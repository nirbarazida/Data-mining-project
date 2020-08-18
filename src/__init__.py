"""
Constructor the generates instances for the program:
1. logger
2. config - instance that contains all the configurations from the Json file
3. Base - SQL-alchemy instance for creating tables in a database
4. database - instance of the Database class that contains all the queries and commit to the DB
5. geolocator - instance of the Geo-locator api
"""

from src.conf import Config
from src.logger import Logger
from sqlalchemy.ext.declarative import declarative_base
from geopy.geocoders import Nominatim
from sqlalchemy import exc
import pymysql


JSON_FILE_NAME = "src/mining_constants.json"

logger = Logger().logger
config = Config(JSON_FILE_NAME)

# mapper & MetaData: maps the subclass to the table and holds all the information about the database
Base = declarative_base()
from database.database import Database


try:
    database = Database()
    geolocator = Nominatim(user_agent=f"{config.DB_NAME}", timeout=3)

except exc.NoSuchModuleError as err:
    print(err._message(), f"\tinput: sql extension= {config.SQL_EXTENSION}, python DBAPI= {config.PYTHON_DBAPI}")
    exit()

except pymysql.err.OperationalError as err:
    logger.error(config.CONNECTION_ERROR.format(err.args[1]))
    exit()


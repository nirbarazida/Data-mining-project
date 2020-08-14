from src.conf import Config
from src.logger import Logger
from sqlalchemy.ext.declarative import declarative_base
from geopy.geocoders import Nominatim
from sqlalchemy import exc
import pymysql


JSON_FILE_NAME = "mining_constants.json"

logger = Logger().logger
config = Config(JSON_FILE_NAME)

# mapper & MetaData: maps the subclass to the table and holds all the information about the database
Base = declarative_base()
from src.working_with_database import Database


try:
    database = Database()
    geolocator = Nominatim(user_agent=f"{config.DB_NAME}", timeout=3)

except exc.NoSuchModuleError as err:
    print(err._message(), f"\tinput: sql extension= {config.SQL_EXTENSION}, python DBAPI= {config.PYTHON_DBAPI}")
    exit()

except pymysql.err.OperationalError as err:
    logger.error(config.CONNECTION_ERROR.format(err.args[1]))
    exit()


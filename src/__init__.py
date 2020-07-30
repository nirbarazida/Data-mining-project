from src.conf import Config
from src.logger import Logger
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from geopy.geocoders import Nominatim
from sqlalchemy import exc
import pymysql

JSON_FILE_NAME = "mining_constants.json"

logger = Logger().logger
config = Config(JSON_FILE_NAME)

try:
    connection = pymysql.connect(host='localhost', user=config.USER_NAME, password=config.PASSWORD,charset='utf8mb4' )
    cursor_instance = connection.cursor()

    engine = create_engine(f"{config.SQL_EXTENSION}+{config.PYTHON_DBAPI}://{config.USER_NAME}:"
                           f"{config.PASSWORD}@localhost/{config.DB_NAME}")

    # mapper & MetaData: maps the subclass to the table and holds all the information about the database
    Base = declarative_base()
    # wraps the database connection and transaction. starts as the Session starts and remain open until the Session closed
    session = Session(bind=engine)
    geolocator = Nominatim(user_agent=f"{config.DB_NAME}", timeout=3)

except exc.NoSuchModuleError as err:
    print(err._message(), f"\tinput: sql extension= {config.SQL_EXTENSION}, python DBAPI= {config.PYTHON_DBAPI}")
    exit()

except pymysql.err.OperationalError as err:
    logger.error(config.CONNECTION_ERROR.format(err.args[1]))
    exit()


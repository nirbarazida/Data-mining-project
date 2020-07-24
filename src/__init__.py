from src.conf import Config
from src.logger import Logger
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from geopy.geocoders import Nominatim


JSON_FILE_NAME = "mining_constants.json"

logger = Logger().logger
config = Config(JSON_FILE_NAME)


engine = create_engine(f"mysql+pymysql://{config.USER_NAME}:{config.PASSWORD}@localhost/{config.DB_NAME}")
# mapper & MetaData: maps the subclass to the table and holds all the information about the database
Base = declarative_base()
# wraps the database connection and transaction. starts as the Session starts and remain open until the Session closed
session = Session(bind=engine)

geolocator = Nominatim(user_agent=f"{config.DB_NAME}", timeout=3)


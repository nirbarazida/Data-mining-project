"""
why using SQLAlchemy ORM:
define tables and relationship using Python classes.
It also provides a system to query and manipulate the database using object-oriented code instead of writing SQL.
"""

from sqlalchemy import create_engine, Integer, String, Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from command_args import args
import os


USER_NAME = os.environ.get("MySQL_USER")
PASSWORD = os.environ.get("MySQL_PASS")
DB_NAME = args.DB_name

engine = create_engine(f"mysql+pymysql://{USER_NAME}:{PASSWORD}@localhost/{DB_NAME}")

# mapper & MetaData: maps the subclass to the table and holds all the information about the database
Base = declarative_base()

# wraps the database connection and transaction. starts as the Session starts and remain open until the Session closed
session = Session(bind=engine)


class WebsitesT(Base):
    """
    stores all the websites
    relationship:
        User - one to many
    """
    __tablename__ = 'websites'
    id = Column(Integer(), primary_key=True)
    name = Column(String(100), nullable=False)
    users = relationship("UserT", backref="website")
    last_scraped = Column(Integer(), nullable=True)


class UserT(Base):
    """
    stores all the users data from all the web-sites.
    relationship:
        WebsitesT - one to many
        User_Tags - one to many (to get many to many with TagsT)
        Reputation - one to one
        Location - one to many
    """
    __tablename__ = 'users' #: TODO - user is a save word in mysql - bad practice
    id = Column(Integer(), primary_key=True)
    rank = Column(Integer())
    name = Column(String(100), nullable=False)
    member_since = Column(DateTime())
    year = Column(Integer())
    month = Column(Integer())
    profile_views = Column(Integer())
    answers = Column(Integer())
    people_reached = Column(Integer())
    location_id = Column(Integer(), ForeignKey('location.id'))
    website_id = Column(Integer(), ForeignKey('websites.id'))
    # uselist - converts it to one-to-one relationship
    reputation = relationship('Reputation', backref='user', uselist=False)
    # lazy='dynamic' - all the users won't be loaded. able to call them using query
    tags = relationship('User_Tags', backref='user', lazy='dynamic')

    # __table_args__ = (UniqueConstraint('name','rank', 'website_id'),)  # todo NIR: create exception to it
                                                                        # todo NIR: check why not scarpping all users


class User_Tags(Base):
    """
    a connection table between User and Tags to form many to many relationship
    was created as a calls and not as a table to store additional data such as score and posts
    relationship:
        User - one to many
        TagsT - one to many
    """
    __tablename__ = 'user_tags'
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey("users.id"))
    tag_id = Column(Integer(), ForeignKey("tags.id"))
    score = Column(Integer())
    posts = Column(Integer())


class TagsT(Base):
    """
    stores all the tags names
    relationship:
        User_Tags - one to many
    """
    __tablename__ = 'tags'
    id = Column(Integer(), primary_key=True)
    name = Column(String(100), nullable=False)
    users = relationship('User_Tags', backref='tag')


class Reputation(Base):
    """
    Stores the reputation of all users.
    not all have reputation since 2017, thus it can be null
    relationship:
        User - one to one
    """
    __tablename__ = 'reputation'
    user_id = Column(Integer(), ForeignKey('users.id'), primary_key=True)
    reputation_now = Column(Integer(), nullable=False)
    reputation_2020 = Column(Integer(), nullable=True)
    reputation_2019 = Column(Integer(), nullable=True)
    reputation_2017 = Column(Integer(), nullable=True)
    reputation_2018 = Column(Integer(), nullable=True)


class Location(Base):
    """
    location of all the users, every location is uniuqe.
    relationship:
        User - one to many
    """
    __tablename__ = 'location'
    id = Column(Integer(), primary_key=True)
    country = Column(String(100), nullable=True)
    continent = Column(String(50), nullable=True)
    users = relationship("UserT", backref="location")

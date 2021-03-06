"""
why using SQLAlchemy ORM:
define tables and relationship using Python classes.
It also provides a system to query and manipulate
the database using object-oriented code instead of writing SQL.
"""

from src import Base, config
from sqlalchemy import Integer, String, Column, DateTime, ForeignKey, UniqueConstraint, Float
from sqlalchemy.orm import relationship


class WebsitesT(Base):
    """
    stores all the websites
    relationship:
        User - one to many
    """
    __tablename__ = 'websites'
    id = Column(Integer(), primary_key=True)
    name = Column(String(config.NAMES_STRING_LENGTH), nullable=False)
    total_users = Column(Integer())
    total_answers = Column(Integer())
    total_questions = Column(Integer())
    answers_per_minute = Column(Float())
    questions_per_minute = Column(Float())
    users = relationship("UserT", backref="website")


class UserT(Base):
    """
    stores all the users data from all the web-sites.
    relationship:
        WebsitesT - one to many
        User_Tags - one to many (to get many to many with TagsT)
        Reputation - one to one
        Location - one to many
    To avid duplication of users in the data base a unique set of ('name', 'rank', 'website_id') was declared.
    """

    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True)
    rank = Column(Integer())
    name = Column(String(config.NAMES_STRING_LENGTH), nullable=False)
    member_since = Column(DateTime())
    profile_views = Column(Integer())
    answers = Column(Integer())
    people_reached = Column(Integer())
    location_id = Column(Integer(), ForeignKey('location.id'))
    website_id = Column(Integer(), ForeignKey('websites.id'))
    reputation = relationship('Reputation', backref='user', uselist=False) # uselist - for one-to-one relationship
    # lazy='dynamic' - all the users won't be loaded. able to call them using query
    tags = relationship('User_Tags', backref='user', lazy='dynamic')

    __table_args__ = (UniqueConstraint('name', 'rank', 'website_id'),)


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
    unique: name
    """
    __tablename__ = 'tags'
    id = Column(Integer(), primary_key=True)
    name = Column(String(config.NAMES_STRING_LENGTH), nullable=False, unique=True)
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
    country = Column(String(config.COUNTRY_MAX_STRING_LENGTH), nullable=True) #, unique=True)
    continent = Column(String(config.CONTINENT_MAX_STRING_LENGTH), nullable=True)
    users = relationship("UserT", backref="location")
    stack_locations = relationship("Stack_Exchange_Location", backref="location")


class Stack_Exchange_Location(Base):
    """
    location of all the users in the way that was writen in the website
    relationship:
        Location - one to many
    for every user will check if his location matches to a location in this table - if yse - will form the same
    connection to the Location. if not - will use geo-locator to find the country and continent
    """
    __tablename__ = 'stack_exchange_location'
    id = Column(Integer(), primary_key=True)
    website_location = Column(String(config.NAMES_STRING_LENGTH), nullable=True) #, unique=True)
    location_id = Column(Integer(), ForeignKey('location.id'))

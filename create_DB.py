import pymysql
from command_args import args
import os


USER_NAME = os.environ.get("MySQL_USER")
PASSWORD = os.environ.get("MySQL_PASS")
DB_NAME = args.DB_name

# todo NIR: add exceptions

if args.create_DB:
    connection = pymysql.connect(host='localhost', user=USER_NAME, password=PASSWORD)

    # Create a cursor object
    cursorInsatnce = connection.cursor()

    # SQL Statement to check if DB exist
    sqlStatement = 'SELECT distinct(SCHEMA_NAME) FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = ' '"' + DB_NAME + '"'

    if cursorInsatnce.execute(sqlStatement) == 0:
        # SQL Statement to create a database
        sqlStatement = "CREATE DATABASE " + DB_NAME

        # Execute the create database SQL statement through the cursor instance
        cursorInsatnce.execute(sqlStatement)



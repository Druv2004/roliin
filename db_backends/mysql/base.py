from django.db.backends.mysql.base import DatabaseWrapper as MySQLDatabaseWrapper
import mysql.connector

class DatabaseWrapper(MySQLDatabaseWrapper):
    vendor = "mysql"
    display_name = "MySQL (mysql-connector-python)"
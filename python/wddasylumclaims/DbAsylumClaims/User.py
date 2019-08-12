import pyodbc
from getpass import getpass
from wddasylumclaims.DbAsylumClaims.Db import DbAsylumClaims

class User(DbAsylumClaims):
    def __init__(self):
        super().__init__()

    def connect(self):
        username = "dbuser"
        password = "AsylumClaims123"
        database = "asylumclaims"
        return(super().connect(database,username,password))
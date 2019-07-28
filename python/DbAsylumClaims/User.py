import pyodbc
from getpass import getpass
from DbAsylumClaims.Db import DbAsylumClaims

class Admin(DbAsylumClaims):
    def __init__(self):
        super().__init__()

    def connect(self):
        #TODO create read-only user in database
        username = "dbuser"
        password = "AsylumClaims123"
        database = "asylumclaims"
        return(super().connect(database,username,password))
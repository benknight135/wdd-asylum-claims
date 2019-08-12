import pyodbc
from getpass import getpass
from wddasylumclaims.DbAsylumClaims.Db import DbAsylumClaims

class Admin(DbAsylumClaims):
    def __init__(self):
        super().__init__()

    def connect(self):
        # Get username and password from user
        username = input("Username: ")
        password = getpass("Password: ")
        database = "asylumclaims"
        # Connect to database with login details
        return(super().connect(database,username,password))

    def createUserLogin(self):
        # Create read-only user login
        username = "dbuser"
        password = "AsylumClaims123"
        return(self.createLogin(username,password))

    def createLogin(self,username,password):
        # Create new login
        if (super().checkConnected()): # check database connection
            # Create new login with sql command
            return(super().sqlCommand("CREATE USER [" + username + "]" + \
                                        "WITH PASSWORD = '" + password + "';" + \
                                        #"ALTER ROLE [db_datareader] ADD MEMBER [" + username + "];"))
                                        "EXEC sp_addrolemember 'db_datareader', '"+username+"';"))
        else:
            return False

    def listUsers(self):
        if (super().checkConnected()): # check database connection
            return(super().sqlCommand("SELECT * from asylumclaims.sys.sql_logins"))
        else:
            return False
        
        
    def resetTables(self):
        if (super().checkConnected()): # check database connection
            # Confirm reset with user
            answer = None
            while answer not in ("y", "n"):
                answer = input("WARNING! Are you sure you want to reset the database? ALL data will be WIPED! (y/n): ")
                if answer == "y":
                    print("ok")
                    # Delete tables
                    success = self.deleteTables()
                    if (not success):
                        print ("Failed to delete some tables (Maybe they did not exist to start with)")
                    # Re-create tables
                    success = self.createTables()
                    if (not success):
                        print ("Database table reset failed. Failed to re-create tables.")
                    else:
                        print ("Tables re-created. Tables reset complete.")
                    return success
                elif answer == "n":
                    print("Database table reset cancelled")
                else:
                    print("Invalid input. Please enter y/n")
        else:
            return False

    def deleteTables(self):
        # Delete all tables
        if (super().checkConnected()): # check database connection
            # delete raw text table
            success1 = self.deleteTable("tblClaimsRawText")
            if (not success1):
                print ("Failed to delete tblClaimsRawText")
            # delete links table
            success2 = self.deleteTable("tblClaimsLinks")
            if (not success2):
                print ("Failed to delete tblClaimsLinks")
            # delete outcomes table
            success3 = self.deleteTable("tblClaimsOutcomes")
            if (not success3):
                print ("Failed to delete tblClaimsOutcomes")
            # check success of deletion
            if (success1 and success2 and success3):
                print ("All tables deleted")
                return True
            else:
                return False
        else:
            return False

    def deleteTable(self,table_name):
        if (super().checkConnected()): # check database connection
            # Confirm deletion of table
            answer = None
            while answer not in ("y", "n"):
                answer = input("WARNING! Are you sure you want to delete the table"+table_name+"? ALL data will be WIPED! (y/n): ")
                if answer == "y":
                    # Run delete table sql command
                    print("Deleting table")
                    return(super().sqlCommand("DROP TABLE "+table_name+";"))
                elif answer == "n":
                    print("Database table reset cancelled")
                else:
                    print("Invalid input. Please enter y/n")
        else:
            return False
            
    def createTables(self):
        if (super().checkConnected()): # check database connection
            # Create raw text table
            sqlValid = super().sqlCommand("CREATE TABLE tblClaimsRawText (\
                                ID int NOT NULL AUTO_INCREMENT,\
                                case_id TEXT,\
                                full_text TEXT,\
                                promulgation_date DATE,\
                                PRIMARY KEY (ID)\
                            );"
                            )
            if (not sqlValid):
                return False
            # Create links table
            sqlValid = super().sqlCommand("CREATE TABLE tblClaimsLinks (\
                                ID int NOT NULL AUTO_INCREMENT,\
                                link TEXT,\
                                PRIMARY KEY (ID)\
                            );"
                            )
            if (not sqlValid):
                return False
            # Create outcomes table
            sqlValid = super().sqlCommand("CREATE TABLE tblClaimsOutcomes (\
                                ID int NOT NULL AUTO_INCREMENT,\
                                case_id TEXT,\
                                promulgation_date DATE,\
                                sogi_case BIT,\
                                unsuccessful BIT,\
                                successful BIT,\
                                ambiguous BIT,\
                                country TEXT,\
                                date_of_birth DATE,\
                                outcome_known BIT,\
                                multiple_outcomes BIT,\
                                no_page_available BIT,\
                                PRIMARY KEY (ID)\
                            );"
                            )
            return sqlValid
        else:
            return False
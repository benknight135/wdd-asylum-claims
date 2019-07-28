import pyodbc

class DbAsylumClaims:
    def __init__(self):
        # initialise database variables
        self.server = 'asylumclaims.database.windows.net'
        self.driver= '{SQL Server}'
        self.isInitialised = False

    def connect(self,database,username,password):
        # Connect to database with credentials
        try:
            # Connect to database
            self.cnxn = pyodbc.connect('DRIVER='+self.driver+';SERVER='+self.server+
                                        ';PORT=1433;DATABASE='+database+';UID='+
                                        username+';PWD='+ password)
            # Setup cursor for sql commands
            self.cursor = self.cnxn.cursor()
            self.isInitialised = True
            return True
        except pyodbc.Error as ex:
            # Failed to connect to database
            print("Database error caught")
            sqlstate = ex.args[1]
            print(sqlstate)
            return False

    def checkConnected(self):
        # Check connection to database
        if (not self.isInitialised):
            print("Not connected to database. Have you run connect() method?")
        return (self.isInitialised)

    def sqlCommand(self,sql):
        if (self.checkConnected()): # check connection to database
            try:
                # Run sql command
                self.cursor.execute(sql)
                return True
            except pyodbc.Error as ex:
                # Failed to run sql command
                print("Database error caught")
                sqlstate = ex.args[1]
                print(sqlstate)
                return False
        else: 
            # Connection to database not initialised
            return False

    def printTables(self):
        if (self.checkConnected()): # check connection to database
            # Print all tables in database
            for row in self.cursor.tables():
                print (row.table_name)
            return True
        else:
            # Connection to database not initialised
            return False

    def close(self):
        if (self.checkConnected()): # check connection to database
            try:
                print ("Closing database connection")
                # Close database connection
                self.cnxn.close()
                self.isInitialised = False
                print ("Database connection closed")
                return True
            except pyodbc.Error as ex:
                # close failed
                print("Database error caught")
                sqlstate = ex.args[1]
                print(sqlstate)
                return False
        else:
            # Connection to database not initialised
            return False


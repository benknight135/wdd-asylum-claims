from wddasylumclaims.DbAsylumClaims.Admin import Admin
from wddasylumclaims.DbAsylumClaims.User import User
import argparse

def get_args():
    
    parser = argparse.ArgumentParser(description='Asylum Claim azsure database test')
    parser.add_argument('-a','--admin',type=str, default=False, help="weather to test admin account (needs login information for access)")
    
    args = vars(parser.parse_args())
    return args

def main():
    args = get_args()

    requestAdmin = args["admin"]

    # Initalise connection sucess returns
    connectSucessUser = False
    connectSucessAdmin = False
    connectSucess = False
    
    # Connected to database as user
    userDb = User()
    connectSucessUser = userDb.connect()

    if (requestAdmin):
        # Connect to database as admin
        adminDb = Admin()
        connectSucessAdmin = adminDb.connect()
        if (connectSucessAdmin and connectSucessUser):
            connectSucess = True
        else:
            connectSucess = False
    
    # Check connection to database
    if(connectSucess):
        if (requestAdmin):
            # Run admin tests
            success = adminDb.printTables()
            if (not success):
                raise Exception("Failed to print database tables as admin")
            # Reset tables in database
            success = adminDb.resetTables()
            if (not success):
                raise Exception("Failed to reset tables in database as admin")
            # Create user login
            #TODO check if user is recreated if already exists or creation fails
            #success = adminDb.createUserLogin()
            #if (not success):
            #    raise Exception("Failed to create user login as admin")
            adminDb.commit_close()
        if (success):
            # Add row to database
            userDb.addRow("tblClaimsLinks","http://www.brainjar.com/java/host/test.html")
            # TODO Delete row from database
            # Commit changes and close connection to database
            userDb.commit_close()
        else:
            # Failed to reset tables. Close connection to database without commiting changes.
            print ("Closing connection to database without commiting changes.")
            adminDb.close()
    else:
        print("Failed to connected to database")

if __name__ == "__main__":
    main()
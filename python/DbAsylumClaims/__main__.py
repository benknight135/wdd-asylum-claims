from DbAsylumClaims.Admin import Admin

def get_args():
    args = None
    return args

def main():
    args = get_args()
    # Initalise admin database class
    adminDb = Admin()
    # Connect to database
    if(adminDb.connect()):
        # Reset tables in database
        #success = adminDb.resetTables()
        # Create user login
        success = adminDb.createUserLogin()
        if (success):
            #TODO Confirm user added by listing users

            # Commit changes and close connection to database
            adminDb.commit_close()
        else:
            # Failed to reset tables. Close connection to database without commiting changes.
            print ("Closing connection to database without commiting changes.")
            adminDb.close()
    else:
        print("Failed to connected to database")

if __name__ == "__main__":
    main()
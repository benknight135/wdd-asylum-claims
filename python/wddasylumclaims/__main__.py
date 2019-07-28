from wddasylumclaims import Keywords, WebScrape
import argparse
import feather
import os
import pandas as pd

def get_args():
    # set to true to set updating offline keywords (stored in packages 'data' folder as keywords.csv)
    default_update_keywords = False

    parser = argparse.ArgumentParser(description='Asylum Claim webscraping')
    parser.add_argument('-k','--keywords',type=str, help="filepath to csv of keywords or url to google sheet")
    parser.add_argument('-u','--update_keywords',type=bool,default=default_update_keywords, help="update offline copy of keywords")
    parser.add_argument('-d','--dataset',type=str, help="filepath to dataset of claims in plain text (see data folder in git repository https://github.com/benknight135/wdd-asylum-claims.git for file synax. Can be csv or feather)")
    parser.add_argument('-l','--links',type=str, help="filepath to dataset of links to claims (see data folder in git repository https://github.com/benknight135/wdd-asylum-claims.git for file synax. Can be csv or feather)")
    parser.add_argument('-r','--results',type=str, help="filepath to dataset of outcomes of claims (see data folder in git repository https://github.com/benknight135/wdd-asylum-claims.git for file synax. Can be csv or feather)")
    parser.add_argument('-i','--index',nargs='*',help="min/max index limits for url pages numbers when searching and case indexs when getting data. Use 0 to grab all the data (e.g. no max or no min). --index MIN_URL_PAGE_INDEX MAX_URL_PAGE_INDEX MIN_CASE_INDEX MAX_CASE_INDEX")
    parser.add_argument('-o','--output',type=str,help="filepath to directory to save results")
    parser.add_argument('-t','--type',type=str,default="both",help="choose filetype to save results as (either 'csv'/'feather'/'both')")
    parser.add_argument('-b','--backup',type=int,default=100,help="how many rows in dataset before a backup is stored (this prevents complete loss of data if there is a problem during a long search but will add a little extra time).")

    args = vars(parser.parse_args())
    return(args)

def main():
    args=get_args()
    # Load output folder from arguments
    output_folder = None
    if (args["output"]):
        if (os.path.exists(args["output"])):
            output_folder = args["output"]
        else:
            raise Exception("Folder directory for output does not exist: {}".format(args["output"]))

    # Load output type from arguments (csv or feather)
    output_type = args["type"]
    if (not (output_type == "both" or output_type == "csv" or output_type == "feather")):
        raise Exception ("Output type MUST be 'csv'/'feather'/'both'")

    # Load backup rate from arguments
    backup_rate = args["backup"]
    if (backup_rate <= 0):
        raise Exception ("MUST be a value greater than 0")

    # Load limits from arguments
    page_limits = None
    url_limits = None
    if (args["index"]):
        if (len(args["index"]) == 4):
            page_limits = [int(args["index"][0]), int(args["index"][1])]
            url_limits = [int(args["index"][2]), int(args["index"][3])]
        else:
            raise Exception ("Invalid number of index values for index. MUST be 4.")

    # Check backup directory is valid exists
    script_dir = os.path.dirname(os.path.realpath(__file__))
    if (os.path.exists(script_dir + "\\data")):
        package_data_dir = script_dir +'\\data'
    elif (os.path.exists(script_dir + "\\..\\data")):
        package_data_dir = script_dir +'\\..\\data'
    else:
        raise Exception ("Script is in unexpected location, cannot locate data folder")

    if (output_folder == None):
        output_folder = package_data_dir

    keyword_filepath = False
    if (args["keywords"]): # keywords filepath defined in arguments
        # get keyword filepath from argument
        keyword_filepath = args["keywords"]

    # get update [true/false] from argument
    update_keywords = args["update_keywords"]
    if (update_keywords):
        # update offline keywords csv with google doc
        if (keyword_filepath == False):
            # change this file if google docs changes (or load from command line and use --keywords)
            keyword_filepath = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8qMS3_t8ibuOkmMwzvJA7CXil3vbeCpbubrCPZByxcPHpCN4eBnsmQslU18E_8uDC6jiuvp5X-aEw/pub?gid=1573361451&single=true&output=csv"
        if ("https://docs.google.com" in keyword_filepath): #filepath is assumed to be a google sheet
            print("Updating keywords document using:")
            print(keyword_filepath)
            # set offline csv to update from google doc (hard coded as loaded from packages 'data' folder in package directory)
            offline_keywords_csv_path = output_folder+'\\keywords.csv'
            # update offline csv with google sheet data
            success = Keywords.update_csv(keyword_filepath,offline_keywords_csv_path)
            if (success):
                print("Offline keywords document updated")
            else:
                raise Exception("Failed to update offline keywords document")
            keyword_filepath = offline_keywords_csv_path
        else:
            raise Exception("Invalid keyword filepath (MUST be url of google sheet for updating offline csv): {}".format(keyword_filepath))

    if (keyword_filepath == False):
        # default load offline csv of keywords from packages 'data' (update from google doc using --keywords [filepath] or --update_keywords)
        keyword_filepath = package_data_dir+'\\keywords.csv'

    # Load filepaths from arguments if provided
    links_filepath = False
    dataset_filepath = False
    outcomes_filepath = False
    if (args["links"]):
        links_filepath = args["links"]
    if (args["dataset"]):
        dataset_filepath = args["dataset"]
    if (args["results"]):
        outcomes_filepath = args["results"]

    # Get keywords from spreadsheet
    if ("http" in keyword_filepath): #filepath is a website so assumed to be google sheet
        print("Loading keywords from google sheet:")
        print(keyword_filepath)
        keywords = Keywords.find_google_sheet(keyword_filepath)
        if (keywords == False):
            raise Exception("Failed to find google sheet")
    elif (".csv" in keyword_filepath): #filepath is not a website so assumed to be a csv
        print("Loading keywords from csv: ")
        print(keyword_filepath)
        keywords = Keywords.find_csv(keyword_filepath)
    else:
        raise Exception("Invalid keyword filepath (MUST be csv or url of google sheet): {}".format(keyword_filepath))

    if (dataset_filepath == False and outcomes_filepath == False):
        if (links_filepath == False):
            # (limit can be added for testing so only a small sample of page numbers are scraped e.g. limit=[4,100])
            feather_urls = WebScrape.scrape_url_list(limit=page_limits,backupFolder=output_folder,backupRate=backup_rate)
            try:
                # Save urls to feather file
                feather_urls_path = output_folder+'\\py_case_links.feather'
                feather.write_dataframe(feather_urls, feather_urls_path)
                # Save urls as csv file
                csv_urls_path = output_folder+'\\py_case_links.csv'
                feather_urls.to_csv(csv_urls_path)
            except IOError as e:
                errno, strerror = e.args
                print("I/O error({0}): {1}".format(errno,strerror))
                print("This is likely due to the file being open. Please make sure it is closed.")
        else:
            try:
                if (".feather" in links_filepath):
                    # Get urls from feather file
                    feather_urls_path = links_filepath
                    feather_urls = feather.read_dataframe(feather_urls_path)
                elif(".csv" in links_filepath):
                    # Get dataset from csv file
                    csv_urls_path = links_filepath
                    feather_urls = pd.read_csv(csv_urls_path,index_col=False)
                else:
                    raise Exception('Invalid file type for url links. MUST be .csv or .feather')
            except IOError as e:
                errno, strerror = e.args
                print("I/O error({0}): {1}".format(errno,strerror))
                print("This is likely due to the file being open. Please make sure it is closed.")
        print (feather_urls)

    if (outcomes_filepath == False):
        if (dataset_filepath == False):
            # Scrap urls for data
            # (limit can be added for testing so only a small sample of the urls are scraped e.g. limit=[4,100])
            print()
            feather_dataset = WebScrape.scrape_urls(feather_urls,limit=url_limits,backupFolder=output_folder,backupRate=backup_rate)
            try:
                # Save dataset as feather file
                feather_dataset_path = output_folder+'\\py_case_text.feather'
                feather.write_dataframe(feather_dataset, feather_dataset_path)
                # Save dataset as csv file
                csv_dataset_path = output_folder+'\\py_case_text.csv'
                feather_dataset.to_csv(csv_dataset_path)
            except IOError as e:
                errno, strerror = e.args
                print("I/O error({0}): {1}".format(errno,strerror))
                print("This is likely due to the file being open. Please make sure it is closed.")
        else:
            try:
                if (".feather" in dataset_filepath):
                    # Get dataset from feather file
                    feather_dataset_path = dataset_filepath
                    feather_dataset = feather.read_dataframe(feather_dataset_path)
                elif(".csv" in dataset_filepath):
                    # Get dataset from csv file
                    csv_dataset_path = dataset_filepath
                    feather_dataset = pd.read_csv(csv_dataset_path,index_col=False)
                else:
                    raise Exception('Invalid file type for dataset. MUST be .csv or .feather')
            except IOError as e:
                errno, strerror = e.args
                print("I/O error({0}): {1}".format(errno,strerror))
                print("This is likely due to the file being open. Please make sure it is closed.")
        print(feather_dataset)

    if (outcomes_filepath == False):
        # Search for keywords in feather dataset
        print()
        feather_outcomes = Keywords.search_all_feather(feather_dataset,keywords,backupRate=backup_rate)
        try:
            # Save outcomes to feather file
            feather_outcomes_path = output_folder+'\\py_case_outcomes.feather'
            feather.write_dataframe(feather_outcomes, feather_outcomes_path)
            # Save outcomes to csv file
            csv_outcomes_path = output_folder+'\\py_case_outcomes.csv'
            feather_outcomes.to_csv(csv_outcomes_path)
        except IOError as e:
            errno, strerror = e.args
            print("I/O error({0}): {1}".format(errno,strerror))
            print("This is likely due to the file being open. Please make sure it is closed.")
    else:
        try:
            if (".feather" in outcomes_filepath):
                # Get outcomes from feather file
                feather_outcomes_path = outcomes_filepath
                feather_outcomes = feather.read_dataframe(feather_dataset_path)
            elif(".csv" in outcomes_filepath):
                # Get dataset from csv file
                csv_outcomes_path = outcomes_filepath
                feather_outcomes = pd.read_csv(csv_outcomes_path,index_col=False)
            else:
                raise Exception('Invalid file type for outcomes. MUST be .csv or .feather')
        except IOError as e:
            errno, strerror = e.args
            print("I/O error({0}): {1}".format(errno,strerror))
            print("This is likely due to the file being open. Please make sure it is closed.")
    print(feather_outcomes)
        
if __name__ == "__main__":
    main()
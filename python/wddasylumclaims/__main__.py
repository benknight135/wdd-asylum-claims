from wddasylumclaims import Keywords, WebScrape
import argparse
import feather
import os
import pandas as pd

def main():
    # set to true to set updating offline keywords (stored in samples folder as keywords.csv)
    default_update_keywords = False

    parser = argparse.ArgumentParser(description='Asylum Claim webscraping')
    parser.add_argument('-k','--keywords',type=str, help="filepath to csv of keywords or url to google sheet")
    parser.add_argument('-u','--update_keywords',type=bool,default=default_update_keywords, help="update offline copy of keywords")
    parser.add_argument('-d','--dataset',type=str, help="filepath to dataset of claims in plain text (see sample folder for file synax. Can be csv or feather)")
    parser.add_argument('-l','--links',type=str, help="filepath to dataset of links to claims (see sample folder for file synax. Can be csv or feather)")
    parser.add_argument('-r','--results',type=str, help="filepath to dataset of outcomes of claims (see sample folder for file synax. Can be csv or feather)")

    args = vars(parser.parse_args())
    test_main(args)

def test_main(args):
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
            keyword_filepath = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8qMS3_t8ibuOkmMwzvJA7CXil3vbeCpbubrCPZByxcPHpCN4eBnsmQslU18E_8uDC6jiuvp5X-aEw/pub?gid=0&single=true&output=csv"
        if ("https://docs.google.com" in keyword_filepath): #filepath is assumed to be a google sheet
            print("Updating keywords document using:")
            print(keyword_filepath)
            # set offline csv to update from google doc (hard coded as loaded from sample folder in package directory)
            offline_keywords_csv_path = os.path.dirname(os.path.realpath(__file__)) +'\\sample\\keywords.csv'
            # update offline csv with google sheet data
            Keywords.update_csv(keyword_filepath,offline_keywords_csv_path)
            print("Offline keywords document updated")
            keyword_filepath = offline_keywords_csv_path
        else:
            raise Exception("Invalid keyword filepath (MUST be url of google sheet for updating offline csv): {}".format(keyword_filepath))

    if (keyword_filepath == False):
        # default load sample offline csv of keywords (update from google doc using --keywords [filepath] or --update_keywords)
        keyword_filepath = os.path.dirname(os.path.realpath(__file__)) +'\\sample\\keywords.csv'

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
    elif (".csv" in keyword_filepath): #filepath is not a website so assumed to be a csv
        print("Loading keywords from csv: ")
        print(keyword_filepath)
        keywords = Keywords.find_csv(keyword_filepath)
    else:
        raise Exception("Invalid keyword filepath (MUST be csv or url of google sheet): {}".format(keyword_filepath))

    if (links_filepath == False):
        # (limit can be added for testing so only a small sample of page numbers are scraped)
        feather_urls = WebScrape.scrape_url_list(limit=1)
        # Save urls to feather file
        feather_urls_path = os.path.dirname(os.path.realpath(__file__)) +'\\sample\\py_case_links.feather'
        feather.write_dataframe(feather_urls, feather_urls_path)
        # Save urls as csv file
        csv_urls_path = os.path.dirname(os.path.realpath(__file__)) +'\\sample\\py_case_links.csv'
        feather_urls.to_csv(csv_urls_path,index_label=False)
    else:
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
    print (feather_urls)

    if (dataset_filepath == False):
        # Scrap urls for data
        # (limit can be added for testing so only a small sample of the urls are scraped)
        print()
        feather_dataset = WebScrape.scrape_urls(feather_urls,limit=5)
        # Save dataset as feather file
        feather_dataset_path = os.path.dirname(os.path.realpath(__file__)) +'\\sample\\py_case_text.feather'
        feather.write_dataframe(feather_dataset, feather_dataset_path)
        # Save dataset as csv file
        csv_dataset_path = os.path.dirname(os.path.realpath(__file__)) +'\\sample\\py_case_text.csv'
        feather_dataset.to_csv(csv_dataset_path)
    else:
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
    print(feather_dataset)

    if (outcomes_filepath == False):
        # Search for keywords in feather dataset
        print()
        feather_outcomes = Keywords.search_all_feather(feather_dataset,keywords)
        # Save outcomes to feather file
        feather_outcomes_path = os.path.dirname(os.path.realpath(__file__)) +'\\sample\\py_case_outcomes.feather'
        feather.write_dataframe(feather_outcomes, feather_outcomes_path)
        # Save outcomes to csv file
        csv_outcomes_path = os.path.dirname(os.path.realpath(__file__)) +'\\sample\\py_case_outcomes.csv'
        feather_outcomes.to_csv(csv_outcomes_path)
    else:
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
    print(feather_outcomes)
        

if __name__ == "__main__":
    main()
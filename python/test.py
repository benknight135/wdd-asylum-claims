from wddasylumclaims import Keywords
import argparse
import feather
import os

def main():
    # initalise default filepaths for data stored in google spread sheet and sample folder
    default_feather_dataset_path = os.path.dirname(os.path.realpath(__file__)) +'\\sample\\case_text_to_5000.feather'
    defaultPath = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8qMS3_t8ibuOkmMwzvJA7CXil3vbeCpbubrCPZByxcPHpCN4eBnsmQslU18E_8uDC6jiuvp5X-aEw/pub?gid=0&single=true&output=csv"
    # uncomment to test loading keywords from csv in sample folder
    #defaultPath = os.path.dirname(os.path.realpath(__file__)) +'\\sample\\keywords.csv'

    parser = argparse.ArgumentParser(description='Asylum Claim webscraping')
    parser.add_argument('-k','--keyword_filepath', default=defaultPath, help="filepath to csv of keywords or url to google sheet")
    parser.add_argument('-f','--feather_dataset',default=default_feather_dataset_path, help="filepath of feather dataset of claims in plain text")

    args = vars(parser.parse_args())
    test_main(args)

def test_main(args):
    keyword_filepath = args["keyword_filepath"]
    feather_dataset_path = args["feather_dataset"]

    # Get keywords from spreadsheet
    if ("http" in keyword_filepath): #filepath is a website so assumed to be google sheet
        keywords = Keywords.find_google_sheet(keyword_filepath)
    elif (".csv" in keyword_filepath): #filepath is not a website so assumed to be a csv
        keywords = Keywords.find_csv(keyword_filepath)
    else:
        raise Exception("Invalid keyword filepath (MUST be csv or url of google sheet): {}".format(keyword_filepath))

    # Search for keywords in all urls in feather
    #feather_urls_path = os.path.dirname(os.path.realpath(__file__)) +'\\sample\\case_links.feather'
    #feather_urls = feather.read_dataframe(feather_urls_path)
    #feather_dataset = Keywords.search_all_urls(feather_urls,keywords)
    # Save feather dataset
    #TODO saving to url scraping to feather dataset

    # Search for keywords in raw feather dataset
    feather_dataset = feather.read_dataframe(feather_dataset_path)
    Keywords.search_all_feather(feather_dataset,keywords)
    
if __name__ == "__main__":
    main()
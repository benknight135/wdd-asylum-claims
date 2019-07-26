from wddasylumclaims import Keywords, WebScrape
import argparse
import feather
import re


def main():

    cases_df = feather.read_dataframe("../case_text_to_500.feather")
    links_df = feather.read_dataframe("../case_links.feather")
    outcomes_df = feather.read_dataframe("../cases_to_500_outcomes.feather")

    urls_to_check = get_URLs_to_check(cases_df, links_df)

    # Cases with no info found. Look for DOC, else PDF (none in 500-sample):

    cases_with_docs = doc_available(urls_to_check)

    defaultPath = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8qMS3_t8ibuOkmMwzvJA7CXil3vbeCpbubrCPZByxcPHpCN4eBnsmQslU18E_8uDC6jiuvp5X-aEw/pub?gid=0&single=true&output=csv"

    parser = argparse.ArgumentParser(description="Asylum Claim webscraping")
    parser.add_argument(
        "-f",
        "--filepath",
        default=defaultPath,
        help="filepath to csv of keywords or url to google sheet",
    )

    args = vars(parser.parse_args())
    cmd_main(args)


def doc_available(url_list):
    doc_list = {}

    # f = open("doc-list.txt", "a")
    # f.write("Now the file has more content!")

    # Scrape html page for decision document
    div_name = "download-links"
    regex = r"https://.*?\.doc"

    for url in url_list:
        decision_doc = WebScrape.scrape(url_list[url], div_name)
        doc_url = re.findall(regex, decision_doc)
        doc_list[url] = doc_url[0]
    # f.close()

    return doc_list


def cmd_main(args):
    csv_filepath = args["filepath"]

    # Get keywords from spreadsheet
    known_headers = [
        "introductory_headings",
        "unsuccessful",
        "successful",
        "ambiguous_outcome",
        "country",
        "dob",
    ]

    # Get keywords from google sheet
    if "http" in csv_filepath:
        keywords = Keywords.find_google_sheet(csv_filepath)
    else:
        keywords = Keywords.find_csv(csv_filepath)

    # Search for keywords in all urls in feather
    # search_all_urls(keywords)

    # Search for keywords in raw feather dataset
    # search_all_feather(keywords)


def get_URLs_to_check(cases_df, links_df):
    url_prefix = "https://tribunalsdecisions.service.gov.uk"
    urls_to_check = {}

    for index, row in cases_df.iterrows():
        if (row["no_page_available"]) == True:
            # urls_to_check.append(url_prefix + links_df.loc[index, "case_links"])
            urls_to_check[index] = url_prefix + links_df.loc[index, "case_links"]

    return urls_to_check


# def search(url, keywords):
# Scrape html page for decision document
# div_name = "decision-inner"
# decision_html = WebScrape.scrape(url, div_name)
# if decision_html:
#     # Find keywords in document
#     keywordLoc, keywordCount = Keywords(decision_html, keywords)
#     return keywordLoc, keywordCount
# else:
#     return False, False

if __name__ == "__main__":
    main()

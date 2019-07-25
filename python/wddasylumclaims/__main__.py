from wddasylumclaims import LoadKeywords, WebScrape
import argparse
import os

def main():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    defaultPath = script_dir+'\\sample\\keywords.csv'
    defaultUrl = "https://tribunalsdecisions.service.gov.uk/utiac/pa-05705-2017-a23c9180-6c47-40f3-9294-67754ec19a04"
    #defaultSearchUrl = "https://tribunalsdecisions.service.gov.uk/utiac?utf8=%E2%9C%93&search%5Bquery%5D=Sexual+orientation&search%5Breported%5D=all&search%5Bcountry%5D=&search%5Bcountry_guideline%5D=0&search%5Bjudge%5D=&search%5Bclaimant%5D="

    parser = argparse.ArgumentParser(description='Asylum Claim webscraping')
    parser.add_argument('-f','--filepath', default=defaultPath, help="filepath to csv of keywords")
    parser.add_argument('-u','--url',default=defaultUrl, help="url to search")

    args = vars(parser.parse_args())
    cmd_main(args)

def cmd_main(args):
    # Get keywords from csv
    known_headers = ["introductory_headings", "unsuccessful", "successful", "ambiguous_outcome", "country","dob"]
    keywords = LoadKeywords.find(args["filepath"],known_headers)

    # Scrape html page for decision document
    div_name = 'decision-inner'
    decision_html = WebScrape.scrape(args["url"],div_name)

    # Find keywords in document
    keywordLoc,keywordCount = WebScrape.findKeywords(decision_html,keywords)
    print()
    print("Keywords found")
    print("--------------")
    for h in keywordCount.keys():
        print ("{}: {}".format(h,keywordCount[h]))

    print()
    print("Keyword locations [LINE_NUM,COL_NUM]")
    print("------------------------------------")
    for h in keywordLoc.keys():
        print ("{}: {}".format(h,keywordLoc[h]))

if __name__ == "__main__":
    main()
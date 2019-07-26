from wddasylumclaims import LoadKeywords, WebScrape
import argparse
import os
import feather

def main():
    defaultPath = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8qMS3_t8ibuOkmMwzvJA7CXil3vbeCpbubrCPZByxcPHpCN4eBnsmQslU18E_8uDC6jiuvp5X-aEw/pub?gid=0&single=true&output=csv"

    parser = argparse.ArgumentParser(description='Asylum Claim webscraping')
    parser.add_argument('-f','--filepath', default=defaultPath, help="filepath to csv of keywords or url to google sheet")

    args = vars(parser.parse_args())
    cmd_main(args)

def search(url,keywords):
    # Scrape html page for decision document
    div_name = 'decision-inner'
    decision_html = WebScrape.scrape(url,div_name)
    if (decision_html):
        # Find keywords in document
        keywordLoc,keywordCount = WebScrape.findKeywords(decision_html,keywords)
        return keywordLoc,keywordCount
    else:
        return False,False

def search_all_urls(keywords):
    path = os.path.dirname(os.path.realpath(__file__)) +'\\sample\\case_links.feather'
 
    df = feather.read_dataframe(path)
    url_prefix = "https://tribunalsdecisions.service.gov.uk"

    rows_count,cols_count = df.shape

    print("Starting process...")
    
    for index, row in df.iterrows():
        # get url from feather data
        url_suffix = row['case_links']
        full_url = url_prefix + url_suffix

        #search for keywords in url
        keywordLoc,keywordCount = search(full_url,keywords)
        if (not keywordCount or not keywordLoc):
            print ("unable to grab from website (maybe missing 'decision-inner' div)")
        else:
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
        
        print("{}/{}".format(index,rows_count))
        
    print("Process complete")

def search_all_feather(keywords):
    path = os.path.dirname(os.path.realpath(__file__)) +'\\sample\\case_text_to_500.feather'
 
    df = feather.read_dataframe(path)

    rows_count,cols_count = df.shape

    print("Starting process...")
    
    for index, row in df.iterrows():
        keywordCount = {}
        keywordLoc = {}
        for h in keywords.keys():
            keywordCount[h] = 0
            keywordLoc[h] = []

        data = row['full_text']
        for h in keywords.keys():
            for k in keywords[h]:
                #for line_num,line in enumerate(data):
                if (data):
                    idx = data.find(k)
                    if (idx != None):
                        if (idx > -1):
                            print(h)
                            keywordLoc.setdefault(h, []).append([idx])
                            keywordCount[h] = keywordCount[h] + 1
        
        print("Keywords found")
        print("--------------")
        for h in keywordCount.keys():
            print ("{}: {}".format(h,keywordCount[h]))

        print()
        print("Keyword locations [LINE_NUM,COL_NUM]")
        print("------------------------------------")
        for h in keywordLoc.keys():
            print ("{}: {}".format(h,keywordLoc[h]))
        
    print("Process complete")


def cmd_main(args):
    csv_filepath = args["filepath"]

     # Get keywords from spreadsheet
    known_headers = ["introductory_headings", "unsuccessful", "successful", "ambiguous_outcome", "country","dob"]

    # Get keywords from google sheet
    if ("http" in csv_filepath):
        keywords = LoadKeywords.find_google_sheet(csv_filepath,known_headers)
    else:
        keywords = LoadKeywords.find(csv_filepath,known_headers)

    # Search for keywords in all urls in feather
    #search_all_urls(keywords)

    # Search for keywords in raw feather dataset
    search_all_feather(keywords)
    

if __name__ == "__main__":
    main()
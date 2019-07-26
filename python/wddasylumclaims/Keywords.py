import csv
import os
import requests
import feather
from wddasylumclaims import WebScrape
from collections import defaultdict

def find_csv(csv_filepath):
    #initialise keywords dictionary with known headings

    with open(csv_filepath, mode='r') as csv_file:
        #read csv
        csv_reader = csv.DictReader(csv_file, delimiter=',')

        known_headers = csv_reader.fieldnames
        keywords = {}
        for h in known_headers:
            keywords[h] = []

        #load data into dictionary using headers
        for row in csv_reader:
            for h in known_headers:
                if (row[h]):
                    keywords.setdefault(h, []).append(row[h])
    return keywords

def find_google_sheet(url):
    response = requests.get(url)
    csv_reader = csv.DictReader(response.iter_lines(decode_unicode='utf-8'),delimiter=',')

    known_headers = csv_reader.fieldnames
    keywords = {}
    for h in known_headers:
        keywords[h] = []

    for row in csv_reader:
        for h in known_headers:
            if (row[h]):
                keywords.setdefault(h, []).append(row[h])
    return keywords

def findKeywordsFeather(feather_dataframe,keywords):
    
    df = feather_dataframe

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
        
        print("{}/{}".format(index,rows_count))
        
    print("Process complete")

    #TODO create outcomes dictionary
    outcomes = {}
    return outcomes

def findKeywordsDiv(div,keywords):
    keywordCount = {}
    keywordLoc = {}
    for h in keywords.keys():
        keywordCount[h] = 0
        keywordLoc[h] = []

    for h in keywords.keys():
        for k in keywords[h]:
            for line_num,line in enumerate(div):
                idx = line.find(k)
                if (idx != None):
                    if (idx > -1):
                        keywordLoc.setdefault(h, []).append([line_num,idx])
                        keywordCount[h] = keywordCount[h] + 1
    return keywordLoc,keywordCount

def createFeatherOutcomes(output_filepath,outcomes):
    pass

def search_all_urls(feather_urls,keywords):
    url_prefix = "https://tribunalsdecisions.service.gov.uk"

    rows_count,cols_count = feather_urls.shape

    print("Searching for keywords in urls...")
    
    for index, row in feather_urls.iterrows():
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

    #TODO create outcomes dictionary
    outcomes = {}
    return outcomes

def search_all_feather(feather_dataset,keywords):
    outcomes = findKeywordsFeather(feather_dataset,keywords)
    return outcomes

def search(url,keywords):
    # Scrape html page for decision document
    div_name = 'decision-inner'
    decision_html = WebScrape.scrape(url,div_name)
    if (decision_html):
        # Find keywords in document
        keywordLoc,keywordCount = findKeywordsDiv(decision_html,keywords)
        return keywordLoc,keywordCount
    else:
        return False,False
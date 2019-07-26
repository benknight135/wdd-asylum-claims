import csv
import os
import requests
import feather
from wddasylumclaims import WebScrape
from collections import defaultdict


def find_csv(csv_filepath):
    # initialise keywords dictionary with known headings

    with open(csv_filepath, mode='r') as csv_file:
        # read csv
        csv_reader = csv.DictReader(csv_file, delimiter=',')

        known_headers = csv_reader.fieldnames
        keywords = {}
        for h in known_headers:
            keywords[h] = []

        # load data into dictionary using headers
        for row in csv_reader:
            for h in known_headers:
                if (row[h]):
                    keywords.setdefault(h, []).append(row[h])
    return keywords


def find_google_sheet(url):
    response = requests.get(url)
    csv_reader = csv.DictReader(response.iter_lines(
        decode_unicode='utf-8'), delimiter=',')

    known_headers = csv_reader.fieldnames
    keywords = {}
    for h in known_headers:
        keywords[h] = []

    for row in csv_reader:
        for h in known_headers:
            if (row[h]):
                keywords.setdefault(h, []).append(row[h])
    return keywords


def findKeywordsFeather(feather_dataframe, keywords):
    rows_count, cols_count = feather_dataframe.shape

    outcomes = []

    print("Searching feather dataset for keywords...")

    for index, row in feather_dataframe.iterrows():
        keywordCount = {}
        keywordLoc = {}
        for h in keywords.keys():
            keywordCount[h] = 0
            keywordLoc[h] = []

        data = row['full_text']
        case_id = row['case_id']
        for h in keywords.keys():
            for k in keywords[h]:
                if (data):
                    idx = data.find(k)
                    if (idx != None):
                        if (idx > -1):
                            keywordLoc.setdefault(h, []).append([idx])
                            keywordCount[h] = keywordCount[h] + 1

        print("{}/{}".format(index, rows_count))

        outcomes.append(
            {'id': case_id, 'keywordCount': keywordCount, 'keywordLoc': keywordLoc})

    print("Process complete")
    return outcomes


def findKeywordsDiv(div, keywords):
    keywordCount = {}
    keywordLoc = {}
    for h in keywords.keys():
        keywordCount[h] = 0
        keywordLoc[h] = []

    for h in keywords.keys():
        for k in keywords[h]:
            for line_num, line in enumerate(div):
                idx = line.find(k)
                if (idx != None):
                    if (idx > -1):
                        keywordLoc.setdefault(h, []).append([line_num, idx])
                        keywordCount[h] = keywordCount[h] + 1
    return keywordLoc, keywordCount


def search_all_feather(feather_dataset, keywords):
    outcomes_raw = findKeywordsFeather(feather_dataset, keywords)
    outcomes = {
        'case_id': [], 'promulgation_date': [], 'sogi_case': [],
        'unsuccessful': [], 'successful': [], 'ambiguous': [],
        'country': [], 'date_of_birth': [], 'outcome_known': [],
        'multiple_outcomes': [], 'no_page_available': []
    }

    for index, row in feather_dataset.iterrows():
        raw_data = row['full_text']
        case_id = outcomes_raw[index]['id']

        keywordCount = outcomes_raw[index]['keywordCount']
        keywordLoc = outcomes_raw[index]['keywordCount']

        promulgation_date = ""
        sogi_case = ""
        country = ""
        date_of_birth = ""
        if (keywordCount['country'] > 0):
            #country found
            pass
        if (keywordCount['dob'] > 0):
            #dob found
            pass
        if (keywordCount['sexual_orientation_case'] > 0):
            #sexual_orientation_case found
            pass
        if (keywordCount['gender_identity_case'] > 0):
            #gender_identity_case found
            pass

        unsuccessful = ""
        successful = ""
        ambiguous = ""
        outcome_known = ""
        multiple_outcomes = ""
        if (keywordCount['unsuccessful'] > 0):
            unsuccessful = True
        if (keywordCount['successful'] > 0):
            successful = True
        if (keywordCount['ambiguous_outcome'] > 0):
            ambiguous = True

        no_page_available = True
        if raw_data == False:
            no_page_available = False

        outcomes.setdefault('case_id', []).append(case_id)
        outcomes.setdefault('promulgation_date', []).append(promulgation_date)
        outcomes.setdefault('sogi_case', []).append(sogi_case)
        outcomes.setdefault('unsuccessful', []).append(unsuccessful)
        outcomes.setdefault('successful', []).append(successful)
        outcomes.setdefault('ambiguous', []).append(ambiguous)
        outcomes.setdefault('country', []).append(country)
        outcomes.setdefault('date_of_birth', []).append(date_of_birth)
        outcomes.setdefault('outcome_known', []).append(outcome_known)
        outcomes.setdefault('multiple_outcomes', []).append(multiple_outcomes)
        outcomes.setdefault('no_page_available', []).append(no_page_available)

    outcomes = outcomes_raw
    return outcomes


def search(url, keywords):
    # Scrape html page for decision document
    div_name = 'decision-inner'
    decision_html = WebScrape.scrape(url, div_name)
    if (decision_html):
        # Find keywords in document
        keywordLoc, keywordCount = findKeywordsDiv(decision_html, keywords)
        return keywordLoc, keywordCount
    else:
        return False, False

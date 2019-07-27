from wddasylumclaims import WebScrape
import pandas as pd
import csv
import os
import requests
import feather
import re

def update_csv(url_google_sheet,csv_filepath):
    with open(csv_filepath, mode='w',encoding="utf-8",newline="") as csv_file:
        response = requests.get(url_google_sheet)
        csv_reader = csv.DictReader(response.iter_lines(decode_unicode='utf-8'), delimiter=',')
        fieldnames = csv_reader.fieldnames
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        known_headers = csv_reader.fieldnames
        keywords = {}
        for h in known_headers:
            keywords[h] = []

        for row in csv_reader:
            newRow = {}
            for h in known_headers:
                if (row[h]):
                    newRow[h] = row[h]
            writer.writerow(newRow)

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
    csv_reader = csv.DictReader(response.iter_lines(decode_unicode='utf-8'), delimiter=',')

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
                    regex = r"\b"+re.escape(k)+r"\b"
                    if h == "country":
                        regex = r"\b"+re.escape(k)+r"\b[ ]['A-Z']"
                    idx = re.search(regex,data)
                    #idx = data.find(k)
                    if (idx != None):
                        idx = idx.start()
                        if (idx > -1):
                            keywordLoc.setdefault(h, []).append([idx,idx+len(k)])
                            keywordCount[h] = keywordCount[h] + 1

        print("{}/{}".format(index+1, rows_count))

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
        promulgation_date = row['promulgation_date']
        case_id = outcomes_raw[index]['id']

        keywordCount = outcomes_raw[index]['keywordCount']
        keywordLoc = outcomes_raw[index]['keywordLoc']

        sogi_case = ""
        country = ""
        date_of_birth = ""
        unsuccessful = ""
        successful = ""
        ambiguous = ""
        outcome_known = ""
        multiple_outcomes = ""

        if (keywordCount['country'] > 0):
            #country found
            charIndexStart = int(keywordLoc['country'][0][1])
            charIndexEnd = len(raw_data)
            if (len(raw_data) > charIndexStart + 50):
                charIndexEnd = charIndexStart + 50
            slicetext = raw_data[charIndexStart:charIndexEnd]

            regex = r"\b[A-Za-z]+\b"
            matches = re.findall(regex,slicetext)
            if len(matches) > 0:
                country = matches[0]

        if (keywordCount['dob'] > 0):
            #dob found
            charIndexStart = int(keywordLoc['dob'][0][1]) + 1
            charIndexEnd = len(raw_data)
            if (len(raw_data) > charIndexStart + 50):
                charIndexEnd = charIndexStart + 50
            slicetext = raw_data[charIndexStart:charIndexEnd]

            regex = r".*?\d{4}"
            matches = re.findall(regex,slicetext)
            if len(matches) > 0:
                date_of_birth = matches[0]

        if (keywordCount['sexual_orientation_case'] > 0 or keywordCount['gender_identity_case'] > 0 or  keywordCount['unknown_sogi_case'] > 0):
            #sexual_orientation_case found
            sogi_case = True
        elif (keywordCount['sexual_orientation_case'] == 0 or keywordCount['gender_identity_case'] == 0 or keywordCount['unknown_sogi_case'] == 0):
            sogi_case = False

        outcome_multi_count = 0

        if (keywordCount['unsuccessful'] > 0):
            unsuccessful = True
            outcome_multi_count = outcome_multi_count + 1
        elif (keywordCount['unsuccessful'] == 0):
            unsuccessful = False
        if (keywordCount['successful'] > 0):
            successful = True
            outcome_multi_count = outcome_multi_count + 1
        elif (keywordCount['successful'] == 0):
            successful = False
        if (keywordCount['ambiguous_outcome'] > 0):
            ambiguous = True
            outcome_multi_count = outcome_multi_count + 1
        elif (keywordCount['ambiguous_outcome'] == 0):
            ambiguous = False

        if ((not ambiguous == "") or (not successful == "") or (not unsuccessful == "")):
            outcome_known = True
            if (outcome_multi_count > 1):
                multiple_outcomes = True
            else:
                multiple_outcomes = False
        else:
            outcome_known = False

        no_page_available = False
        if raw_data == False:
            no_page_available = True

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

    feather_outcomes = pd.DataFrame(outcomes)
    return feather_outcomes

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

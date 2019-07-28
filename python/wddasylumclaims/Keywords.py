from wddasylumclaims import WebScrape
import pandas as pd
import csv
import os
import requests
import feather
import re

def update_csv(url_google_sheet,csv_filepath):
    with open(csv_filepath, mode='w',encoding="utf-8",newline="") as csv_file:
        try:
            resp = requests.get(url_google_sheet,timeout=3)
            resp.raise_for_status()
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else",err)
            return False
        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
            return False
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
            return False
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
            return False
        csv_reader = csv.DictReader(resp.iter_lines(decode_unicode='utf-8'), delimiter=',')
        fieldnames = csv_reader.fieldnames
        try:
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
        except IOError as e:
            errno, strerror = e.args
            print("I/O error({0}): {1}".format(errno,strerror))
            print("This is likely due to the file being open. Please make sure it is closed.")
            return False
        
    return True

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
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)
        return False
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
        return False
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
        return False
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
        return False
        
    csv_reader = csv.DictReader(resp.iter_lines(decode_unicode='utf-8'), delimiter=',')

    known_headers = csv_reader.fieldnames
    keywords = {}
    for h in known_headers:
        keywords[h] = []

    for row in csv_reader:
        for h in known_headers:
            if (row[h]):
                keywords.setdefault(h, []).append(row[h])
    return keywords

def search_all_feather(feather_dataset, keywords, backupFolder=None, backupRate=50):
    print("Organising results...")

    #outcomes_raw = findKeywordsFeather(feather_dataset, keywords)
    outcomes = {
        'case_id': [], 'promulgation_date': [], 'sogi_case': [],
        'unsuccessful': [], 'successful': [], 'ambiguous': [],
        'country': [], 'date_of_birth': [], 'outcome_known': [],
        'multiple_outcomes': [], 'no_page_available': []
    }

    backup_count = 0
    backup_count_max = backupRate # backup every n rows

    rows_count,cols_count = feather_dataset.shape

    for index, row in feather_dataset.iterrows():
        raw_data = row['full_text']
        promulgation_date = row['promulgation_date']

        keywordCount = {}
        keywordLoc = {}
        for h in keywords.keys():
            keywordCount[h] = 0
            keywordLoc[h] = []

        case_id = row['case_id']
        for h in keywords.keys():
            for k in keywords[h]:
                if (raw_data):
                    regex = r"(?i)\b"+re.escape(k)+r"\b"
                    if h == "country":
                        regex = r"(?i)\b"+re.escape(k)+r"\b[ ]['A-Z']"
                    idx = re.search(regex,raw_data)
                    if (idx != None):
                        idx = idx.start()
                        if (idx > -1):
                            #print("found {} at {}".format(k,idx))
                            keywordLoc.setdefault(h, []).append([idx,idx+len(k)])
                            keywordCount[h] = keywordCount[h] + 1

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
            if (outcome_multi_count > 1):
                multiple_outcomes = True
                outcome_known = False
            else:
                multiple_outcomes = False
                if(outcome_multi_count == 1):
                    outcome_known = True
                else:
                    outcome_known = False
        else:
            outcome_known = False

        if (outcome_known == False):
            print(case_id)
            if unsuccessful:
                charIndexStart = int(keywordLoc['unsuccessful'][0][0])
                charIndexEnd = len(raw_data)
                if (len(raw_data) > charIndexStart + 50):
                    charIndexEnd = charIndexStart + 50
                slicetext = raw_data[charIndexStart:charIndexEnd]
                print (slicetext)
            if successful:
                charIndexStart = int(keywordLoc['successful'][0][0])
                charIndexEnd = len(raw_data)
                if (len(raw_data) > charIndexStart + 50):
                    charIndexEnd = charIndexStart + 50
                slicetext = raw_data[charIndexStart:charIndexEnd]
                print (slicetext)
            if ambiguous:
                charIndexStart = int(keywordLoc['ambiguous_outcome'][0][0])
                charIndexEnd = len(raw_data)
                if (len(raw_data) > charIndexStart + 50):
                    charIndexEnd = charIndexStart + 50
                slicetext = raw_data[charIndexStart:charIndexEnd]
                print (slicetext)
            
            if (ambiguous or successful or unsuccessful):
                #TODO check reason for aposing decisions found
                print ("aposing decisions found")
            else:
                #TODO check reason decision not found
                print("no descision found")
                '''
                known_ignore_case_ids = ['[2019] UKUT 217']
                known_ignore_case = False
                for k_id in known_ignore_case_ids:
                    if (k_id == case_id):
                        known_ignore_case = True
                        break
                if (not known_ignore_case):
                    print("new case id with unknown decision not found")
                else:
                    print("ignored case id with unknown decision as desision was marked as ")
                '''
                    
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

        backup_count = backup_count + 1
        if backup_count > backup_count_max:
            print ("Saving backup...")
            # store temperary csv and feather files after each row to backup data
            feather_outcomes = pd.DataFrame(outcomes)

            if (not backupFolder == None):
                # check backup data exists
                if (os.path.exists(backupFolder)):
                    feather_outcomes_path = backupFolder + '\\py_tmp_case_outcomes.feather'
                    csv_outcomes_path = backupFolder + '\\py_tmp_case_outcomes.csv'
                else:
                    raise Exception ("Backup folder does not exist: {}".format(backupFolder))
            try:
                # Save backup feather file
                feather.write_dataframe(feather_outcomes, feather_outcomes_path)
                # Save backup csv file
                feather_outcomes.to_csv(csv_outcomes_path,index_label=False)
                print ("Backup saved")
                backup_count = 0
            except IOError as e:
                errno, strerror = e.args
                print("I/O error({0}): {1}".format(errno,strerror))
                print("This is likely due to the file being open. Please make sure it is closed.")

        print("{}/{}".format(index+1, rows_count))

    feather_outcomes = pd.DataFrame(outcomes)
    return feather_outcomes

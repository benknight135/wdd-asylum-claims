import csv
import os
import requests
from collections import defaultdict

from contextlib import closing

def find(csv_filepath,known_headers=["introductory_headings", "unsuccessful", "successful", "ambiguous_outcome", "country","dob"]):
    #initialise keywords dictionary with known headings
    keywords = {}
    for h in known_headers:
        keywords[h] = []

    with open(csv_filepath, mode='r') as csv_file:
        #read csv
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        #load data into dictionary using headers
        for row in csv_reader:
            for h in known_headers:
                if (row[h]):
                    keywords.setdefault(h, []).append(row[h])
    return keywords

def find_google_sheet(url,known_headers=["introductory_headings", "unsuccessful", "successful", "ambiguous_outcome", "country","dob"]):
    keywords = {}
    for h in known_headers:
        keywords[h] = []

    response = requests.get(url)
    csv_reader = csv.DictReader(response.iter_lines(decode_unicode='utf-8'),delimiter=',')
    for row in csv_reader:
        for h in known_headers:
            if (row[h]):
                keywords.setdefault(h, []).append(row[h])
    return keywords
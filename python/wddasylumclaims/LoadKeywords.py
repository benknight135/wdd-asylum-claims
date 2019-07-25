import csv
import os
from collections import defaultdict

def find(csv_filepath,known_headers=["introductory_headings", "unsuccessful", "successful", "ambiguous_outcome", "country","dob"]):
    #initialise keywords dictionary with known headings
    keywords = {}
    for h in known_headers:
        keywords[h] = []

    with open(csv_filepath, mode='r') as csv_file:
        #read csv
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        #load data into dictionary using headers
        col_headers = []
        line_count = 0
        for row in csv_reader:
            for i,h in enumerate(known_headers):
                if (row[h]):
                    keywords.setdefault(h, []).append(row[h])

    return keywords
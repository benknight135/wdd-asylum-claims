from bs4 import BeautifulSoup
import requests
import csv

def scrape(url,div_name):
    resp = requests.get(url)

    soup = BeautifulSoup(resp.content,features="html.parser")

    for div in soup.find_all("div"):
        if (div.get("class") == [div_name]):
            return div

    return False

def findKeywords(div,keywords):
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

if __name__ == "__main__":
    url = "https://tribunalsdecisions.service.gov.uk/utiac/pa-05705-2017-a23c9180-6c47-40f3-9294-67754ec19a04"
    div_name = 'decision-inner'
    div_data = scrape(url,div_name)
    print(div_data)
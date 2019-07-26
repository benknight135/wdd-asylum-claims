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

if __name__ == "__main__":
    url = "https://tribunalsdecisions.service.gov.uk/utiac/pa-05705-2017-a23c9180-6c47-40f3-9294-67754ec19a04"
    div_name = 'decision-inner'
    div_data = scrape(url,div_name)
    print(div_data)
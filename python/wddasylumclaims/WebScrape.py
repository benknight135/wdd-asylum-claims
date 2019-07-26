from zipfile import ZipFile
from io import BytesIO
from bs4 import BeautifulSoup
import requests
import csv
import pandas as pd
import re

def scrape(url, div_name):
    resp = requests.get(url)

    soup = BeautifulSoup(resp.content, features="html.parser")

    for div in soup.find_all("div"):
        if (div.get("class") == [div_name]):
            return str(div)
    return False


def scrape_decision(url):
    resp = requests.get(url)

    soup = BeautifulSoup(resp.content, features="html.parser")

    for div in soup.find_all("div"):
        if (div.get("class") == ["decision-inner"]):
            print ("decisin-inner found")
            return str(div)
    for div in soup.find_all("div"):
        if (div.get("class") == ["download-links"]):
            regex = r"https://.*?\.doc"
            doc_url = re.findall(regex, str(div))
            val = get_doc_data(doc_url)
            print ("doc found")
            return(val)
    return False


def get_doc_data(url):
    # TODO get doc data from url
    url = "https://moj-tribunals-documents-prod.s3.amazonaws.com/decision/doc_file/65881/00217_ukut_iac_2019__ns_ijr.doc"

    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, features="html.parser")
    
    return soup.get_text()


def scrape_promulgation_date(url):
    resp = requests.get(url)

    soup = BeautifulSoup(resp.content, features="html.parser")

    for i, div in enumerate(soup.find_all("li")):
        if i == 5:
            div.find_all('time')
            for res in div.find_all('time'):
                res2 = res.get('timedate')
                return str(res2)
    return False


def scrape_feather_urls(feather_urls, limit=-1, div_name="decision-inner", url_prefix="https://tribunalsdecisions.service.gov.uk"):
    rows_count, cols_count = feather_urls.shape

    dataset = {'case_id': [], 'full_text': [], 'promulgation_date': []}

    print("Scrapping data in urls...")

    for index, row in feather_urls.iterrows():
        # get url from feather data
        url_suffix = row['case_links']
        full_url = url_prefix + url_suffix

        decision_html = scrape_decision(full_url)
        promulgation_date = scrape_promulgation_date(full_url)

        dataset.setdefault('case_id', []).append(full_url)
        dataset.setdefault('full_text', []).append(decision_html)
        dataset.setdefault('promulgation_date', []).append(promulgation_date)

        if ((index > limit) and not (limit == -1)):
            break

        print("{}/{}".format(index, rows_count))

    feather_dataset = pd.DataFrame(dataset)

    print("Process complete")

    return feather_dataset


if __name__ == "__main__":
    url = "https://tribunalsdecisions.service.gov.uk/utiac/pa-05705-2017-a23c9180-6c47-40f3-9294-67754ec19a04"
    div_name = 'decision-inner'
    div_data = scrape(url, div_name)
    print(div_data)

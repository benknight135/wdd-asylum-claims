from bs4 import BeautifulSoup
import requests
import csv
import pandas as pd
import re
import os
import win32com.client

def scrape_url_list(limit=-1,url_pre="https://tribunalsdecisions.service.gov.uk/utiac?page=", url_post="&search%5Bclaimant%5D=&search%5Bcountry%5D=&search%5Bcountry_guideline%5D=&search%5Bjudge%5D=&search%5Bquery%5D=&search%5Breported%5D=all&utf8=%E2%9C%93"):
    print ("Starting grabbing url list from search url...")

    urls = {'case_links':[]}

    max_pages = 935
    if (limit > 0):
        max_pages = limit+1
    for p in range(1,max_pages):
        page = url_pre + str(p) + url_post
        resp = requests.get(page)
        soup = BeautifulSoup(resp.content, features="html.parser")
        
        tds = soup.find_all("td")
        for td in tds:
            if (td.get("class") == ["reported"] or td.get("class") == ["unreported"]):
                a = td.find_all("a")[0]
                link = a.get("href")
                urls.setdefault('case_links', []).append(link)

        print("{}/{}".format(p, 935))

        

    feather_urls = pd.DataFrame(urls)
    print ("Process complete")
    return feather_urls

def scrape(url, div_name):
    resp = requests.get(url)

    soup = BeautifulSoup(resp.content, features="html.parser")

    for div in soup.find_all("a"):
        if (div.get("class") == [div_name]):
            return str(div)
    return False


def scrape_decision(url):
    resp = requests.get(url)

    soup = BeautifulSoup(resp.content, features="html.parser")

    for div in soup.find_all("div"):
        if (div.get("class") == ["decision-inner"]):
            print ("decision-inner found")
            data = div.get_text()
            data = ' '.join(data.split())
            return data
    for div in soup.find_all("div"):
        if (div.get("class") == ["download-links"]):
            regex = r"https://.*?\.doc"
            doc_url = re.findall(regex, str(div))
            if (len(doc_url)>0):
                print ("doc found")
                val = get_doc_data(doc_url[0])
                return(val)
    return False


def get_doc_data(url):
    # Download word document to sample folder temperaraly
    print("Downloading document...")
    resp = requests.get(url,stream=True)
    doc_filepath = os.path.dirname(os.path.realpath(__file__)) +'\\..\\sample\\tmp_web.doc'
    with open(doc_filepath, 'wb') as f:
        for chunk in resp.iter_content(1024 * 1024 * 2):
            f.write(chunk)
    
    # Load data from saved word document
    # CURRENT WINDOWS ONLY AS REQUIRED WIN32
    # NEEDS OFFICE INSTALLED
    # Open word application
    print("Reading document...")
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    wb = word.Documents.Open(doc_filepath)
    doc = word.ActiveDocument
    data = doc.Range().Text
    
    # close word
    doc.Close()
    word.Quit()

    print("done.")

    if os.path.exists(doc_filepath):
        os.remove(doc_filepath)
    else:
        print("Doc file does not exist")

    # TODO load data from word document without needing office installed
    # TODO load word docmument directly without saving to file first

    data = ' '.join(data.split())
    return data


def scrape_promulgation_date(url):
    resp = requests.get(url)

    soup = BeautifulSoup(resp.content, features="html.parser")

    for i, div in enumerate(soup.find_all("li")):
        if i == 5:
            for res in div.find_all('time'):
                res2 = res.get('timedate')
                return str(res2)
    return False

def scrape_header(url):
    resp = requests.get(url)

    soup = BeautifulSoup(resp.content, features="html.parser")

    if (soup.h1):
        return(soup.h1.get_text())

    return False

def scrape_urls(feather_urls, limit=-1, div_name="decision-inner", url_prefix="https://tribunalsdecisions.service.gov.uk"):
    rows_count, cols_count = feather_urls.shape

    dataset = {'case_id': [], 'full_text': [], 'promulgation_date': []}

    print("Scrapping data from urls...")

    for index, row in feather_urls.iterrows():
        # get url from feather data
        url_suffix = row['case_links']
        full_url = url_prefix + url_suffix

        header_html = scrape_header(full_url)
        decision_html = scrape_decision(full_url)
        promulgation_date = scrape_promulgation_date(full_url)

        dataset.setdefault('case_id', []).append(header_html)
        dataset.setdefault('full_text', []).append(decision_html)
        dataset.setdefault('promulgation_date', []).append(promulgation_date)

        if ((index > (limit+1)) and not (limit == -1)):
            break

        print("{}/{}".format(index+1, rows_count))

    feather_dataset = pd.DataFrame(dataset)

    print("Process complete")

    return feather_dataset


if __name__ == "__main__":
    url = "https://tribunalsdecisions.service.gov.uk/utiac/pa-05705-2017-a23c9180-6c47-40f3-9294-67754ec19a04"
    div_name = 'decision-inner'
    div_data = scrape(url, div_name)
    print(div_data)

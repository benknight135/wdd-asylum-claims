from bs4 import BeautifulSoup
import requests
import csv
import pandas as pd

def scrape(url,div_name):
    resp = requests.get(url)

    soup = BeautifulSoup(resp.content,features="html.parser")

    for div in soup.find_all("div"):
        if (div.get("class") == [div_name]):
            return str(div)

    return False

def scrape_feather_urls(feather_urls,limit=-1,div_name="decision-inner",url_prefix="https://tribunalsdecisions.service.gov.uk"):
    rows_count,cols_count = feather_urls.shape

    dataset = {'case_id':[],'full_text':[]}
    print("Scrapping data in urls...")
    
    for index, row in feather_urls.iterrows():
        # get url from feather data
        url_suffix = row['case_links']
        full_url = url_prefix + url_suffix

        decision_html = scrape(full_url,div_name)

        dataset.setdefault('case_id', []).append(full_url)
        dataset.setdefault('full_text', []).append(decision_html)

        if ((index > limit) and not (limit == -1)):
            break

        print("{}/{}".format(index,rows_count))
        
    feather_dataset = pd.DataFrame(dataset)
        
    print("Process complete")

    return feather_dataset

if __name__ == "__main__":
    url = "https://tribunalsdecisions.service.gov.uk/utiac/pa-05705-2017-a23c9180-6c47-40f3-9294-67754ec19a04"
    div_name = 'decision-inner'
    div_data = scrape(url,div_name)
    print(div_data)
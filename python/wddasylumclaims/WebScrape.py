from bs4 import BeautifulSoup
import requests
import csv
import pandas as pd
import re
import os
import feather
import win32com.client


def scrape_url_list(limit=None, backupFolder=None, backupRate=5, url_pre="https://tribunalsdecisions.service.gov.uk/utiac?page=", url_post="&search%5Bclaimant%5D=&search%5Bcountry%5D=&search%5Bcountry_guideline%5D=&search%5Bjudge%5D=&search%5Bquery%5D=&search%5Breported%5D=all&utf8=%E2%9C%93"):
    print("Starting grabbing url list from search url...")

    urls = {'case_links': []}

    backup_count = 0
    backup_count_max = backupRate  # backup every n pages

    max_pages = 935

    prevArrLen = 0

    startIdx = 1
    if (not limit == None):
        if (limit[0] > 0):
            startIdx = limit[0]

        if (limit[1] > 0):
            max_pages = limit[1]+1

    for p in range(startIdx, max_pages):
        page = url_pre + str(p) + url_post
        isConnectionSuccess = True
        try:
            resp = requests.get(page, timeout=3)
            resp.raise_for_status()
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
            isConnectionSuccess = False
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
            isConnectionSuccess = False
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
            isConnectionSuccess = False
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
            isConnectionSuccess = False

        if (not isConnectionSuccess):
            urls.setdefault('case_links', []).append("")
        else:
            soup = BeautifulSoup(resp.content, features="html.parser")

            tds = soup.find_all("td")
            for td in tds:
                if (td.get("class") == ["reported"] or td.get("class") == ["unreported"]):
                    a = td.find_all("a")[0]
                    link = a.get("href")
                    urls.setdefault('case_links', []).append(link)

            print("{}/{}".format(p, max_pages-1))

        newLinksCount = len(urls['case_links']) - prevArrLen
        prevArrLen = len(urls['case_links'])
        print("new links added: {}".format(newLinksCount))

        backup_count = backup_count + newLinksCount

        if backup_count > backup_count_max:
            print("Saving backup...")
            # store temperary csv and feather files after each page to backup data
            feather_urls = pd.DataFrame(urls)

            if (not backupFolder == None):
                # Check backup folder exists
                if (os.path.exists(backupFolder)):
                    feather_urls_path = backupFolder + '\\py_tmp_case_links.feather'
                    csv_urls_path = backupFolder + '\\py_tmp_case_links.csv'
                else:
                    raise Exception(
                        "Backup folder does not exist: {}".format(backupFolder))

            try:
                # Save backup feather file
                feather.write_dataframe(feather_urls, feather_urls_path)
                # Save backup csv file
                feather_urls.to_csv(csv_urls_path)
                print("Backup saved")
                backup_count = 0
            except IOError as e:
                errno, strerror = e.args
                print("I/O error({0}): {1}".format(errno, strerror))
                print(
                    "This is likely due to the file being open. Please make sure it is closed.")

    feather_urls = pd.DataFrame(urls)
    print("Process complete")
    return feather_urls


def scrape(url, div_name):
    try:
        resp = requests.get(url, timeout=3)
        resp.raise_for_status()
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
        return False
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
        return False
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
        return False
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        return False

    soup = BeautifulSoup(resp.content, features="html.parser")

    for div in soup.find_all("a"):
        if (div.get("class") == [div_name]):
            return str(div)
    return False


def scrape_decision(url):
    try:
        resp = requests.get(url, timeout=3)
        resp.raise_for_status()
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
        return False
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
        return False
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
        return False
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        return False

    soup = BeautifulSoup(resp.content, features="html.parser")

    for div in soup.find_all("div"):
        if (div.get("class") == ["decision-inner"]):
            print("html found")
            data = div.get_text()
            data = ' '.join(data.split())
            return data
    for div in soup.find_all("div"):
        if (div.get("class") == ["download-links"]):
            regex = r"https://.*?\.doc"
            doc_url = re.findall(regex, str(div))
            if (len(doc_url) > 0):
                print("doc found")
                val = get_doc_data(doc_url[0])
                if (val == False):
                    return False
                return(val)
    return False


def get_doc_data(url):
    # Download word document to packages 'data' folder temperaraly
    print("Downloading document...")
    try:
        resp = requests.get(url, stream=True, timeout=3)
        resp.raise_for_status()
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
        return False
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
        return False
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
        return False
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        return False

    # Check backup directory is valid exists
    script_dir = os.path.dirname(os.path.realpath(__file__))
    if (os.path.exists(script_dir + "\\data")):
        doc_filepath = script_dir + '\\data\\tmp_web.doc'
    elif (os.path.exists(script_dir + "\\..\\data")):
        doc_filepath = script_dir + '\\..\\data\\tmp_web.doc'
    else:
        raise Exception(
            "Script is in unexpected location, cannot locate packages 'data' folder")

    try:
        with open(doc_filepath, 'wb') as f:
            for chunk in resp.iter_content(1024 * 1024 * 2):
                f.write(chunk)

        # Load data from saved word document
        # CURRENT WINDOWS ONLY AS REQUIRED WIN32
        # NEEDS OFFICE INSTALLED
        # Open word application
        try:
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
        except Exception as e:
            print(e)
            return False
    except IOError as e:
        errno, strerror = e.args
        print("I/O error({0}): {1}".format(errno, strerror))
        print("This is likely due to the file being open. Please make sure it is closed.")
        return False

    if os.path.exists(doc_filepath):
        os.remove(doc_filepath)
    else:
        print("Doc file does not exist")

    # TODO load data from word document without needing office installed
    # TODO load word docmument directly without saving to file first

    data = ' '.join(data.split())
    # TODO fix issue with encoding of data from word document (current doesn't save the csv properly)
    return data


def scrape_promulgation_date(url):
    try:
        resp = requests.get(url, timeout=3)
        resp.raise_for_status()
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
        return False
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
        return False
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
        return False
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        return False

    soup = BeautifulSoup(resp.content, features="html.parser")

    for i, div in enumerate(soup.find_all("li")):
        if i == 5:
            for res in div.find_all('time'):
                res2 = res.get('timedate')
                return str(res2)
    return False


def scrape_header(url):
    try:
        resp = requests.get(url, timeout=3)
        resp.raise_for_status()
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
        return False
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
        return False
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
        return False
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        return False

    soup = BeautifulSoup(resp.content, features="html.parser")

    if (soup.h1):
        return(soup.h1.get_text())

    return False


def scrape_urls(feather_urls, limit=None, backupFolder=None, backupRate=50, div_name="decision-inner", url_prefix="https://tribunalsdecisions.service.gov.uk"):
    rows_count, cols_count = feather_urls.shape
    if (not limit == None):
        if (limit[1] > 0 and limit[1] < rows_count):
            rows_count = limit[1]

    dataset = {'case_id': [], 'full_text': [], 'promulgation_date': []}

    print("Scrapping data from urls...")

    backup_count = 0
    backup_count_max = backupRate  # backup every n rows

    for index, row in feather_urls.iterrows():
        if (not limit == None):
            if ((index < (limit[0]-1)) and (limit[0] > 0)):
                continue

        # get url from feather data
        url_suffix = row['case_links']
        if (url_suffix == ""):
            print("invalid url")
            continue
        else:
            full_url = url_prefix + url_suffix

            header_html = scrape_header(full_url)
            decision_html = scrape_decision(full_url)
            promulgation_date = scrape_promulgation_date(full_url)

            if (header_html == False or decision_html == False or promulgation_date == False):
                continue

            dataset.setdefault('case_id', []).append(header_html)
            dataset.setdefault('full_text', []).append(decision_html)
            dataset.setdefault('promulgation_date', []
                               ).append(promulgation_date)

        backup_count = backup_count + 1
        if backup_count > backup_count_max:
            print("Saving backup...")
            # store temperary csv and feather files after each row to backup data
            feather_dataset = pd.DataFrame(dataset)

            if (not backupFolder == None):
                # Check backup folder exists
                if (os.path.exists(backupFolder)):
                    feather_dataset_path = backupFolder + '\\py_tmp_case_text.feather'
                    csv_dataset_path = backupFolder + '\\py_tmp_case_text.csv'
                else:
                    raise Exception(
                        "Backup folder does not exist: {}".format(backupFolder))

            try:
                # Save backup feather file
                feather.write_dataframe(feather_dataset, feather_dataset_path)
                # Save backup csv file
                feather_dataset.to_csv(csv_dataset_path)
                print("Backup saved")
                backup_count = 0
            except IOError as e:
                errno, strerror = e.args
                print("I/O error({0}): {1}".format(errno, strerror))
                print(
                    "This is likely due to the file being open. Please make sure it is closed.")

        print("{}/{}".format(index+1, rows_count))

        if (not limit == None):
            if ((index >= limit[1]-1) and (limit[1] > 0)):
                break

    feather_dataset = pd.DataFrame(dataset)

    print("Process complete")

    return feather_dataset


if __name__ == "__main__":
    url = "https://tribunalsdecisions.service.gov.uk/utiac/pa-05705-2017-a23c9180-6c47-40f3-9294-67754ec19a04"
    div_name = 'decision-inner'
    div_data = scrape(url, div_name)
    print(div_data)

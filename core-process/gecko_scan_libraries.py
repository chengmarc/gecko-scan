# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import re, io, os, sys, time, datetime, configparser, getpass, threading, random
from urllib.parse import urlparse

try:
    import tkinter
    import requests
    import pandas as pd
    from bs4 import BeautifulSoup as bs
    print("SYSTEM: Core modules imported.")

except ImportError as e:
    print(f"SYSTEM: The module '{e.name}' is not found, please install it using either pip or conda.")
    getpass.getpass("SYSTEM: Press Enter to quit in a few seconds...")
    sys.exit()


# %% Function overview
"""
The graph below is an overview of the call structure of the functions.
│
├───get_category_name()             # get the name of a category (sector)
├───get_num_of_pages()              # get the number of pages of a category
├───get_page_list()                 # get the list of urls of a category
│   
├───extract_dataframe()             # extract dataframe from a list of urls
│   │
│   ├───extract_page_normal()       # extract data from a given page (method 1)
│   └───extract_page_category()     # extract data from a given page (method 2)
│
├───trim_dataframe()                # clean a given dataframe
│
├───recursive_download()            # download database
│   │
│   └───get_filename()              # get the file name of a given page
│
├───config_create()                 # detect config and create one if not exist
├───config_read_check()             # read from section [Checks] in config
├───config_read_path()              # read from section [Paths] in config
├───config_save()                   # save to config
│
├───get_datetime()                  # get current datetime
"""


# %% Fake headers to bypass CloudFlare
base_url = "https://www.coingecko.com/"

agent_list = [
    {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 9_8_3) Gecko/20100101 Firefox/57.8'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.4; Win64; x64; en-US) Gecko/20130401 Firefox/50.0'},
    {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 10.4;) AppleWebKit/602.7 (KHTML, like Gecko) Chrome/50.0.3427.158 Safari/535'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 9_9_0) AppleWebKit/534.47 (KHTML, like Gecko) Chrome/52.0.1333.275 Safari/537'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.2; WOW64) AppleWebKit/536.31 (KHTML, like Gecko) Chrome/50.0.1826.173 Safari/534'},
    {'User-Agent': 'Mozilla/5.0 (Linux; U; Linux x86_64; en-US) AppleWebKit/603.40 (KHTML, like Gecko) Chrome/48.0.1697.142 Safari/537'},
    {'User-Agent': 'Mozilla/5.0 (Windows; Windows NT 10.0; Win64; x64; en-US) AppleWebKit/603.29 (KHTML, like Gecko) Chrome/52.0.2305.265 Safari/601'},
    {'User-Agent': 'Mozilla/5.0 (Windows; Windows NT 10.4;; en-US) AppleWebKit/603.14 (KHTML, like Gecko) Chrome/49.0.2454.349 Safari/600'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.3; WOW64) AppleWebKit/600.15 (KHTML, like Gecko) Chrome/54.0.3775.310 Safari/600.0 Edge/11.48575'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.5;) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/51.0.1326.199 Safari/537.8 Edge/12.30568'}]

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-CA,en-US;q=0.7,en;q=0.3',
    'Alt-Userd': 'www.coingceko.com',
    'Connection': 'keep-alive',
    'Cookie': '_session_id=5bdb2abf405a2d9e6824309986d26ccb; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Feb+06+2024+08%3A40%3A38+GMT-0500+(Eastern+Standard+Time)&version=202312.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=b43e2efa-81af-45cd-8f91-4ea1d60ea6a0&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0004%3A0%2CC0003%3A1&AwaitingReconsent=false; __cf_bm=8vFmBQvD0t925PV.lonDVn6L61j8X5N0evU_3kgoewc-1707226826-1-AVrry33UfNU8MD+TKHQP+N/zgo0MtXYo+aGs+L1kaJ8AQi4xD5oE7VrYJCpMe92bEBfI2yclbKhun5mMLMBmGwU=',
    'DNT': '1',
    'Host': 'www.coingecko.com',
    'Referer': 'https://www.coingecko.com/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'}


# %% Functions for getting key information in each category


def get_category_name(category_url: str) -> str:
    """
    The function takes a category url and returns the last segement of the url.

    Precondition:   category_url is the url of a specific crypto category
    Return:         a string that is the base name of web url

    # Example
    input:  "www.coingecko.com/en/categories/smart-contract-platform"
    output: "smart-contract-platform"
    """
    parsed_url = urlparse(category_url)
    basename = os.path.basename(parsed_url.path)
    filename, extension = os.path.splitext(basename)
    return filename


def get_num_of_pages(driver, category_url: str) -> int:
    """
    The function takes the given headers and sends a request to the category url,
    and returns the number of pages in this category.

    Precondition:   category_url is the url of a specific crypto category
    Return:         an integer that is the number of pages in this category

    # Example
    input:  headers, "www.coingecko.com/en/categories/smart-contract-platform"
    output: 2
    """
    driver.get(category_url)
    html = driver.page_source
    soup = bs(html, "html.parser").find_all("li", class_="page-item")
    num = int([obj.get_text() for obj in soup][-2])
    return num


def get_page_list(num: int, category_url: str) -> list:
    """
    The fucntion takes the category url and the number of pages to return a list of urls in this category.

    Precondition:   num is an integer that represents the number of pages
                    category_url is the url of a specific crypto category
    Return:         a list of strings that contains the urls of all the pages in this category

    # Example
    input:  2, "www.coingecko.com/en/categories/smart-contract-platform"

    output: ["www.coingecko.com/en/categories/smart-contract-platform",
             "www.coingecko.com/en/categories/smart-contract-platform?page=2"]
    """
    pages = [category_url]
    for i in range(2, num + 1):
        pages.append(f"{category_url}?page={str(i)}")
    return pages


# %% Functions for data mining


def extract_page_normal(soup) -> pd.DataFrame:
    """
    The function takes a BeautifulSoup soup object and returns a pandas dataframe.

    Precondition:   soup is a BeautifulSoup object parsed from a specific page html
    Return:         a pandas dataframe that contains the market data of the given page

    # Example
    input:  a BeautifulSoup object parsed from "www.coingecko.com/en/categories/smart-contract-platform"
    output: a pandas dataframe with 100 rows of market data
    """
    rows = soup.find_all("tr", class_="hover:tw-bg-gray-50 tw-bg-white dark:tw-bg-moon-900 hover:dark:tw-bg-moon-800 tw-text-sm")

    df = []
    for row in rows:
        symbol = row.find("div", class_="tw-text-xs tw-leading-4 tw-text-gray-500 dark:tw-text-moon-200 tw-font-medium tw-block 2lg:tw-inline")    
        name = row.find("div", class_="tw-text-gray-700 dark:tw-text-moon-100 tw-font-semibold tw-text-sm tw-leading-5")
        row_list = [symbol.get_text(), name.get_text()]

        cells = row.find_all("td", class_="tw-text-gray-900 dark:tw-text-moon-50 tw-px-1 tw-py-2.5 2lg:tw-p-2.5 tw-bg-inherit tw-text-end")
        for cell in cells:
            row_list.append(cell.get_text())

        df.append(row_list)

    df = pd.DataFrame(df)
    df.columns = ["Symbol", "Name", "Price", "Change1h", "Change24h", "Change7d", "Volume24h", "MarketCap"]

    return df


def extract_page_category(soup) -> pd.DataFrame:
    """
    The function takes a BeautifulSoup soup object and returns a pandas dataframe.

    Precondition:   soup is a BeautifulSoup object parsed from a specific page html
    Return:         a pandas dataframe that contains the market data of the given page

    # Example
    input:  a BeautifulSoup object parsed from "www.coingecko.com/en/categories/smart-contract-platform"
    output: a pandas dataframe with 100 rows of market data
    """
    names = soup.find_all("span", class_="lg:tw-flex font-bold tw-items-center tw-justify-between")
    symbols = soup.find_all("span", class_="d-lg-inline font-normal text-3xs tw-ml-0 md:tw-ml-2 md:tw-self-center tw-text-gray-500 dark:tw-text-white dark:tw-text-opacity-60")
    pricelst = soup.find_all("td", class_="td-price price text-right")

    prices = []
    for price in pricelst:
        prices.append(price.find("span", class_="no-wrap"))

    change1h = soup.find_all("td", class_="td-change1h change1h stat-percent text-right col-market")
    change24h = soup.find_all("td", class_="td-change24h change24h stat-percent text-right col-market")
    change7d = soup.find_all("td", class_="td-change7d change7d stat-percent text-right col-market")
    volume24h = soup.find_all("td", class_="td-liquidity_score lit text-right col-market")
    marketcap = soup.find_all("td", class_="td-market_cap cap col-market cap-price text-right")

    df = []
    for object_lst in [symbols, names, pricelst, change1h, change24h, change7d, volume24h, marketcap]:
        df.append([obj.get_text() for obj in object_lst])

    df = pd.DataFrame(df).transpose()
    df.columns = ["Symbol", "Name", "Price", "Change1h", "Change24h", "Change7d", "Volume24h", "MarketCap"]

    return df


def extract_dataframe(driver, url_lst: list[str], threshold: int, normal: bool)  -> (pd.DataFrame, int):
    """
    The function takes given headers and sends a request to the list of urls,
    and returns a concatenated pandas dataframe.

    Precondition:   url_list is a list of strings that contains the urls of all the pages in a category
    Return:         a pandas dataframe that contains all the market data of this category
                    a integer that represent the threshold

    # Example
    input:  headers,  ["www.coingecko.com/en/categories/smart-contract-platform",
                       "www.coingecko.com/en/categories/smart-contract-platform?page=2"], 0

    output: a pandas dataframe with 150 rows of market data 
            (100 rows on the first page, 50 rows on the second), 2
    """
    df_clean = pd.DataFrame(
        columns=["Symbol", "Name", "Price", "Change1h", "Change24h", "Change7d", "Volume24h", "MarketCap"])

    for url in url_lst:
        driver.get(url)
        html = driver.page_source
        soup = bs(html, "html.parser")

        if normal: df_page = extract_page_normal(soup)
        else: df_page = extract_page_category(soup)
        df_clean = pd.concat([df_clean, df_page], axis=0, ignore_index=True)

        info_extracting()
        time.sleep(0.5) 

        threshold += 1
        if threshold % 20 == 0:
            info_wait()
            time.sleep(20)

    return df_clean, threshold


def trim_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    The function takes a pandas dataframe and removes currency symbols and empty spaces.

    Precondition:   df is a pandas dataframe that contains market data
    Return:         a pandas dataframe where the cells contains no $ symbol, and no leading or trailing blanks

    # Example
    input:  a pandas dataframe with one row:    ["  BTC  ", "$30000   ", "$11200000  ", "$833000000"]
    output: a pandas dataframe with one row:    ["BTC", "30000", "11200000", "833000000"]
    """
    for column in df.columns:
        df[column] = df[column].str.strip()

    # Remove USD currency symbol
    df["Price"] = df["Price"].str.replace('Buy', '')
    df["Price"] = df["Price"].str.strip()
    df["Price"] = df["Price"].str.replace('$', '')
    df["Volume24h"] = df["Volume24h"].str.replace('$', '')
    df["MarketCap"] = df["MarketCap"].str.replace('$', '')

    return df


# %% Functions for database and recursive process


def get_filename(response: requests.Response, url: str) -> str:
    """
    This function takes an response object and returns the file name contained in it.

    Precondition:   response is a response object obtained by requests.get(url)
    Return:         a string that represents the file name

    #Example
    input:  a response object obatined by requests.get("https://www.coingecko.com/price_charts/export/N/usd.csv")
    output: "btc-usd-max.csv"
    """
    number_match = re.search(r"\/(\d+)\/", url)
    number = str(number_match.group(1)).zfill(5) + "-"

    if response.headers.get("Content-Disposition"):
        content_disposition = response.headers.get("Content-Disposition")
        filename_match = re.search(r'filename="(.+)"', content_disposition)
        filename = filename_match.group(1)
    else:
        current_time = datetime.datetime.now().strftime("%H-%M-%S")
        filename = f"no-name-{current_time}"
    return number + filename


def recursive_download(driver, url_list: list[str], output_path: str):
    """
    This function takes a list of valid urls and downloads the corresponding .csv files contained to a given path.

    Precondition:   url_list is a list of urls of the following format:
                    https://www.coingecko.com/price_charts/export/N/usd.csv
                    where N is a positive integer number
    """
    if not url_list:
        return

    url = url_list[0]
    response = requests.get(url, headers=agent_list[random.randint(0, 9)], stream=True)
    response.status_code

    if response.status_code == 200:
        url_list.pop(0)
        output_name = get_filename(response, url)
        df = pd.read_csv(io.StringIO(response.content.decode("utf-8")))
        df.to_csv(os.path.join(output_path, output_name), encoding="utf-8")
        info_database(200, url)
        time.sleep(0.5)
    elif response.status_code == 404:
        url_list.pop(0)
        info_database(404, url)
        time.sleep(0.5)
    elif response.status_code == 403:
        info_database(403, url)
        time.sleep(0.5)
    elif response.status_code == 429:
        info_database(429, url)
        time.sleep(20)

    return recursive_download(url_list, output_path)


# %% Function for output path and output time


def config_create() -> None:
    """
    This function detects if the config file exist.
    If not, it will create the config file with default save locations.
    """
    config_file = r"C:\Users\Public\config_gecko_scan.ini"
    if not os.path.exists(config_file):
        content = ("[Checks]\n"
                   "check_all_crypto=Accepted\n"
                   "check_categories=Accepted\n"
                   "check_database=Not Accepted\n"
                   "[Paths]\n"
                   r"output_path_all_crypto=C:\Users\Public\Documents" + "\n"
                   r"output_path_categories=C:\Users\Public\Documents" + "\n"
                   r"output_path_database=C:\Users\Public\Documents" + "\n")
        with open(config_file, "w") as f:
            f.write(content)
            f.close()


def config_read_check(selection: str) -> str:
    """
    Given a selection, this function will return the corresponding path.

    Return:         a string that represents either checked or not checked
    """
    config_file = r"C:\Users\Public\config_gecko_scan.ini"
    config = configparser.ConfigParser()
    config.read(config_file)
    config_check = config.get("Checks", selection)
    return config_check


def config_read_path(selection: str) -> (str, bool):
    """
    Given a selection, this function will return the corresponding path.

    Return:         a tuple of str and boolean
                    the string represents the path
                    the boolean represents the validity of the path
    """
    config_file = r"C:\Users\Public\config_gecko_scan.ini"
    config = configparser.ConfigParser()
    config.read(config_file)
    config_path = config.get("Paths", selection)

    if os.path.isdir(config_path):
        return config_path, True
    else:
        return config_path, False


def config_save(check1, check2, check3,
                path1, path2, path3) -> None:
    """
    Given three strings, this function will save the strings to the config file.
    """
    config_file = r"C:\Users\Public\config_gecko_scan.ini"
    content = ("[Checks]\n"
               f"check_all_crypto={check1}\n"
               f"check_categories={check2}\n"
               f"check_database={check3}\n"
               "[Paths]\n"
               f"output_path_all_crypto={path1}\n"
               f"output_path_categories={path2}\n"
               f"output_path_database={path3}\n")
    with open(config_file, "w") as f:
        f.write(content)
        f.close()


def get_datetime() -> str:
    """
    This function returns a string that represents the current datetime.

    Return:         a string of the format: %Y-%m-%d_%H-%M-%S
    """
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    return formatted_datetime


# %% Function for user notice


def notice_start(name: str) -> None:
    length = len(name) + 6*2
    print("")
    print(length*"#")
    print(f"##### {name} #####")
    print(length*"#")
    print("")


def notice_url_success(n) -> None:
    print("INFO: Successfully extracted URLs.")
    print(f"INFO: {n} URLs has been loaded.")
    print("")


def notice_batch_size(n) -> None:
    print("INFO: Successfully created batches.")
    print(f"INFO: {n} batches has been loaded.")
    print("")


def notice_save_success() -> None:
    print("SYSTEM: Successfully loaded output config.")
    print("SYSTEM: Data has been saved to the desired location.")
    print("")


def info_extracting() -> None:
    print("INFO: Extracting information...")


def info_wait() -> None:
    print("INFO: Wait 20 seconds to avoid being blocked.")


def info_category(category:str) -> None:
    print(f"INFO: Successfully extracted data for {category}")


def info_database(code, url) -> None:
    if code == 200:
        print(f"INFO: Downloaded {url}")
    elif code == 404:
        print(f"INFO: Discarded {url}")
    elif code == 403 or code == 429:
        print(f"INFO: Skipped {url}")


def info_data_ready() -> None:
    print("INFO: All data ready.")
    print("")


def error_url_timeout() -> None:
    print("")
    print("SYSTEM: URL extraction timeout, please try again.")
    getpass.getpass("SYSTEM: Press enter to quit...")
    sys.exit()


def error_data_timeout() -> None:
    print("")
    print("SYSTEM: Data extraction timeout, please try again.")
    getpass.getpass("SYSTEM: Press enter to quit...")
    sys.exit()


def error_save_failed() -> None:
    print("")
    print("SYSTEM: Failed to save extracted data, please check your config.")
    getpass.getpass("SYSTEM: Press enter to quit...")
    sys.exit()


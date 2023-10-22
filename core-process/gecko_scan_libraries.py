# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import re, io, os, sys, time, datetime, configparser, getpass
from urllib.parse import urlparse

try:
    import tkinter
    import requests
    import pandas as pd
    from bs4 import BeautifulSoup as bs
    from colorama import init, Fore
    init()
    print(Fore.GREEN + "Core modules imported.")

except ImportError as e:
    print(f"The module '{e.name}' is not found, please install it using either pip or conda.")
    getpass.getpass("Press Enter to quit in a few seconds...")
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
│   └───extract_page()              # extract data from a given page
│
├───trim_dataframe()                # clean a given dataframe
│
├───recursive_download()            # download database
│   │
│   └───get_filename()              # get the file name of a given page
│
├───config_create()                 # detect config and create one if not exist
├───config_read()                   # read from config
├───config_save()                   # save to config
│
├───get_datetime()                  # get current datetime
│
├───notice_wait_20()                # user notice
├───notice_save_desired()           # user notice
├───notice_save_default()           # user notice
├───error_url_timeout()             # user notice
├───error_data_timeout()            # user notice
└───error_save_failed()             # user notice
"""

# %% Fake headers to bypass CloudFlare
base_url = "https://www.coingecko.com/"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

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


def get_num_of_pages(headers: dict, category_url: str) -> int:
    """
    The function takes the given headers and sends a request to the category url,
    and returns the number of pages in this category.

    Precondition:   category_url is the url of a specific crypto category
    Return:         an integer that is the number of pages in this category

    # Example
    input:  headers, "www.coingecko.com/en/categories/smart-contract-platform"
    output: 2
    """
    response = requests.get(category_url, headers=headers)
    html = response.content
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


def extract_page(soup) -> pd.DataFrame:
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


def extract_dataframe(headers: dict, url_lst: list) -> "pd.DataFrame":
    """
    The function takes given headers and sends a request to the list of urls,
    and returns a concatenated pandas dataframe.

    Precondition:   url_list is a list of strings that contains the urls of all the pages in a category
    Return:         a pandas dataframe that contains all the market data of this category

    # Example
    input:  headers,  ["www.coingecko.com/en/categories/smart-contract-platform",
                       "www.coingecko.com/en/categories/smart-contract-platform?page=2"]

    output: a pandas dataframe with 150 rows of market data (100 rows on the first page, 50 rows on the second)
    """
    df_clean = pd.DataFrame(
        columns=["Symbol", "Name", "Price", "Change1h", "Change24h", "Change7d", "Volume24h", "MarketCap"])

    for url in url_lst:
        response = requests.get(url, headers=headers)
        html = response.content
        soup = bs(html, "html.parser").find("div", class_="coingecko-table")

        df_page = extract_page(soup)
        df_clean = pd.concat([df_clean, df_page], axis=0, ignore_index=True)

        print(Fore.WHITE, "- Extracting information...")
        time.sleep(0.5)

    return df_clean


def trim_dataframe(df: "pd.DataFrame") -> "pd.DataFrame":
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
    df["Price"] = df["Price"].str[1:]
    df["Volume24h"] = df["Volume24h"].str[1:]
    df["MarketCap"] = df["MarketCap"].str[1:]

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


def recursive_download(url_list: list, output_path: str):
    """
    This function takes a list of valid urls and downloads the corresponding .csv files contained to a given path.

    Precondition:   url_list is a list of urls of the following format:
                    https://www.coingecko.com/price_charts/export/N/usd.csv
                    where N is a positive integer number
    """
    if not url_list:
        return

    url = url_list[0]
    response = requests.get(url, headers=headers, stream=True)
    response.status_code

    if response.status_code == 200:
        url_list.pop(0)
        output_name = get_filename(response, url)
        df = pd.read_csv(io.StringIO(response.content.decode("utf-8")))
        df.to_csv(os.path.join(output_path, output_name), encoding="utf-8")
        print(Fore.WHITE, f"- Downloaded {url}")
        time.sleep(0.5)
    elif response.status_code == 404:
        url_list.pop(0)
        print(Fore.WHITE, f"- Discarded {url}")
        time.sleep(0.5)
    elif response.status_code == 403:
        print(Fore.YELLOW, f"- Skipped {url}")
        time.sleep(0.5)
    elif response.status_code == 429:
        print(Fore.YELLOW, f"- Skipped {url}")
        time.sleep(20)

    return recursive_download(url_list, output_path)


# %% Function for output path and output time


def config_create() -> None:
    """
    This function detects if the config file exist.
    If not, it will create the config file with default save locations.
    """
    config_file = r"C:\Users\Public\config.ini"
    if not os.path.exists(config_file):
        content = ("[Paths]\n"
                   r"output_path_all_crypto=C:\Users\Public\Documents" + "\n"
                   r"output_path_categories=C:\Users\Public\Documents" + "\n"
                   r"output_path_database=C:\Users\Public\Documents" + "\n")
        with open(config_file, "w") as f:
            f.write(content)
            f.close()


def config_read(selection: str) -> (str, bool):
    """
    Given a selection, this function will return the corresponding path.

    Return:         a tuple of str and boolean
                    the string represents the path
                    the boolean represents the validity of the path
    """
    config_file = r"C:\Users\Public\config.ini"
    config = configparser.ConfigParser()
    config.read(config_file)
    config_path = config.get("Paths", selection)
    
    if os.path.isdir(config_path):
        return config_path, True
    else:
        return config_path, False


def config_save(path1, path2, path3) -> None:
    """
    Given three strings, this function will save the strings to the config file.
    """
    config_file = r"C:\Users\Public\config.ini"
    content = ("[Paths]\n"
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
    print(Fore.WHITE + length*"#")
    print(Fore.WHITE + f"##### {name} #####")
    print(Fore.WHITE + length*"#")
    print("")


def notice_wait_20() -> None:
    print("")
    print(Fore.YELLOW + "Wait 20 seconds to avoid being blocked.")
    print("")


def notice_save_success() -> None:
    print(Fore.WHITE + "Successfully loaded output config.")
    print(Fore.WHITE + "Data has been saved to the desired location.")
    print("")


def error_url_timeout() -> None:
    print("")
    print(Fore.RED + "URL extraction timeout, please try again.")
    getpass.getpass("Press enter to quit...")
    sys.exit()


def error_data_timeout() -> None:
    print("")
    print(Fore.RED + "Data extraction timeout, please try again.")
    getpass.getpass("Press enter to quit...")
    sys.exit()


def error_save_failed() -> None:
    print("")
    print(Fore.RED + "Failed to save extracted data, please check your config.")
    getpass.getpass("Press enter to quit...")
    sys.exit()

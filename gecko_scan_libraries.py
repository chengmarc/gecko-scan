# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import re, io, os, sys, time, datetime, configparser, getpass
from urllib.parse import urlparse

script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

try:
    import requests
    import pandas as pd
    from bs4 import BeautifulSoup as bs
    
    #from selenium import webdriver
    #from selenium.webdriver.firefox.options import Options as FirefoxOptions
    #from selenium.webdriver.chrome.options import Options as ChromeOptions
    from colorama import init, Fore
    init()
    print(Fore.GREEN + "Core modules imported.")

except ImportError as e:
    print(f"The module '{e.name}' is not found, please install it using either pip or conda.")
    getpass.getpass("Press Enter to quit in a few seconds...")
    sys.exit()
    
# %% Fake headers to bypass CloudFlare
headers = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}

# %% Functions for intializing webdrivers (Note: selenium and webdrivers are deprecated, requests is used instead.)
"""
def initialize_firefox():
    #Current webdriver version:
    #mozilla/geckodriver 0.33.0    
    options = FirefoxOptions()
    options.add_argument("-headless")
    driver_path = script_path + "\webdrivers\geckodriver.exe"
    driver = webdriver.Firefox(executable_path=driver_path, service_log_path='NUL', options=options)
    return driver

def initialize_chrome():
    #Current webdriver version:
    #ChromeDriver 116.0.5845.96 (r1160321)
    options = ChromeOptions()
    options.add_argument("--headless")
    driver_path = script_path + "\webdrivers\chromedriver.exe"
    driver = webdriver.Chrome(executable_path=driver_path, service_log_path='NUL', options=options)
    return driver
"""
# %% Functions for getting key information in each category

def get_name(category_url:str) -> str:
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

def get_num_of_pages(headers, category_url:str) -> int:
    """
    The function takes given headers and send a request to a category url,
    and return the number of pages in this category.
    
    Precondition:   category_url is the url of a specific crypto category
    Return:         an integer that is the number of pages in this category

    # Example
    input:  headers, "www.coingecko.com/en/categories/smart-contract-platform"
    output: 2
    """    
    response = requests.get(category_url, headers=headers)
    html = response.content
    soup = bs(html, "html.parser").find_all('li', class_='page-item')
    num = int([obj.get_text() for obj in soup][-2])
    return num

def get_page_list(num, category_url:str) -> list[str]:
    """
    The fucntion takes a category url and the number of pages to return a list of urls in this category.
    
    Precondition:   num is an integer that represent the number of pages
                    category_url is the url of a specific crypto category
    Return:         a list of strings that contains the urls of all the pages in this category

    # Example
    input:  2, "www.coingecko.com/en/categories/smart-contract-platform"
    output: ["www.coingecko.com/en/categories/smart-contract-platform",
             "www.coingecko.com/en/categories/smart-contract-platform?page=2"]
    """
    pages = [category_url]
    for i in range(2, num+1):
        pages.append(category_url + "?page=" + str(i))
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
    names = soup.find_all('span', class_='lg:tw-flex font-bold tw-items-center tw-justify-between')
    symbols = soup.find_all('span', class_='d-lg-inline font-normal text-3xs tw-ml-0 md:tw-ml-2 md:tw-self-center tw-text-gray-500 dark:tw-text-white dark:tw-text-opacity-60')
    pricelst = soup.find_all('td', class_='td-price price text-right')

    prices = []
    for price in pricelst:
        prices.append(price.find('span', class_='no-wrap'))

    change1h = soup.find_all('td', class_='td-change1h change1h stat-percent text-right col-market')
    change24h = soup.find_all('td', class_='td-change24h change24h stat-percent text-right col-market')
    change7d = soup.find_all('td', class_='td-change7d change7d stat-percent text-right col-market')
    volume24h = soup.find_all('td', class_='td-liquidity_score lit text-right col-market')
    marketcap = soup.find_all('td', class_='td-market_cap cap col-market cap-price text-right')

    df = []
    for object_lst in [symbols, names, pricelst, change1h, change24h, change7d, volume24h, marketcap]:
        df.append([obj.get_text() for obj in object_lst])

    df = pd.DataFrame(df).transpose()
    df.columns=['Symbol', 'Name', 'Price', 'Change1h', 'Change24h', 'Change7d', 'Volume24h', 'MarketCap']
    return df

def extract_dataframe(headers, url_lst:list[str]) -> pd.DataFrame:
    """
    The function takes given headers and send a request to a list of urls,
    and returns a concatenated pandas dataframe.
    
    Precondition:   url_list is a list of strings that contains the urls of all the pages in a category                                    
    Return:         a pandas dataframe that contains all the market data of this category

    # Example
    input:  headers,  ["www.coingecko.com/en/categories/smart-contract-platform",
                       "www.coingecko.com/en/categories/smart-contract-platform?page=2"]
    output: a pandas dataframe with 150 rows of market data (100 rows on the first page, 50 rows on the second)
    """
    df_clean = pd.DataFrame(columns = ['Symbol', 'Name', 'Price', 'Change1h', 
                                       'Change24h', 'Change7d', 'Volume24h', 'MarketCap'])
    for url in url_lst:
        response = requests.get(url, headers=headers)
        html = response.content
        soup = bs(html, "html.parser").find('div', class_='coingecko-table')

        df_page = extract_page(soup)
        df_clean = pd.concat([df_clean, df_page], axis=0, ignore_index=True)

        print(Fore.WHITE, "Extracting information...")
        time.sleep(0.5)

    return df_clean

def trim_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    The function takes a pandas dataframe and removes the currency symbols and empty spaces.
    
    Precondition:   df is a pandas dataframe that contains market data
    Return:         a pandas dataframe where the cells contains no $ symbol, and no leading or trailing blanks

    # Example
    input:  a pandas dataframe with one row:    ["  BTC  ", "$30000   ", "$11200000  ", "$833000000"]
    output: a pandas dataframe with one row:    ["BTC", "30000", "11200000", "833000000"]
    """
    for column in df.columns:
        df[column] = df[column].str.strip()

    # Remove USD currency symbol
    df['Price'] = df['Price'].str[1:]
    df['Volume24h'] = df['Volume24h'].str[1:]
    df['MarketCap'] = df['MarketCap'].str[1:]
    
    return df

# %% Functions for database and recursive process

def get_filename(response, url:str) -> str:
    """
    This function takes an reponse object and returns the file name contained in it.
    
    Precondition:   response is an response object obtained by requests.get(url)
    Return:         a string representing the file name
    
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

def download_csv(response, filepath:str, filename:str):
    """
    This function takes an reponse object and downloads the .csv file contained in it.
    
    Precondition:   response is an response object obtained by requests.get(url)
                    the url must be the same as the following format:
                    https://www.coingecko.com/price_charts/export/N/usd.csv
                    where N is an positive integer number
    """
    s = response.content
    df = pd.read_csv(io.StringIO(s.decode('utf-8')))
    df.to_csv(filepath + "\\" + filename, encoding='utf-8')

def recursive_download(url_list:list, output_path:str):
    """
    This function takes a list of valid urls and download the .csv files contained in the urls.
    
    Precondition:   url_list is a list of urls in the following format:
                    https://www.coingecko.com/price_charts/export/N/usd.csv
                    where N is an positive integer number
    """
    if not url_list:                    # Base case: if list_429 is empty, return the updated lists
        return
    
    url = url_list[0] 
    response = requests.get(url, stream=True)
    response.status_code
    
    if response.status_code == 200:
        url_list.pop(0)
        output_name = get_filename(response, url)
        download_csv(response, output_path, output_name)
        print(Fore.GREEN, "Downloaded", url)
        time.sleep(0.5)
    elif response.status_code == 404:
        url_list.pop(0)
        print(Fore.GREEN, "Discarded", url)
        time.sleep(0.5)
    elif response.status_code == 429:
        print(Fore.YELLOW, "Skipped", url)
        time.sleep(20)
        
    return recursive_download(url_list, output_path)

# %% Function for output path
def get_output_path(selection:str) -> str:
    """
    This function check "gecko_scan config.ini" and return a path if there is one.
    If the path is empty or is not valid, then it will return the default path.
    
    Return:         a string representing the output path
    """
    config = configparser.ConfigParser()
    config.read('gecko_scan config.ini')
    config_path = config.get('Paths', selection)
    if config_path != "" and os.path.isdir(config_path):
        return config_path
    elif selection == 'output_path_all_crypto':
        return script_path + "\\all-crypto-daily"
    elif selection == 'output_path_categories':
        return script_path + "\\categories-daily"
    elif selection == 'output_path_database':
        return script_path + "\\database"
        
# %% Function for user notice

def notice_data_ready():
    print(Fore.GREEN + "       _ _       _       _                             _       ")
    print(Fore.GREEN + "  __ _| | |   __| | __ _| |_ __ _   _ __ ___  __ _  __| |_   _ ")
    print(Fore.GREEN + " / _` | | |  / _` |/ _` | __/ _` | | '__/ _ \/ _` |/ _` | | | |")
    print(Fore.GREEN + "| (_| | | | | (_| | (_| | || (_| | | | |  __/ (_| | (_| | |_| |")
    print(Fore.GREEN + " \__,_|_|_|  \__,_|\__,_|\__\__,_| |_|  \___|\__,_|\__,_|\__, |")
    print(Fore.GREEN + "                                                         |___/ ")
    
def notice_wait_20():
    print("")
    print(Fore.YELLOW + "Wait 20 seconds to avoid being blocked.")
    print("")
    
def notice_input():
    print("")
    print(Fore.WHITE + "Data has been saved to desired location.")
    getpass.getpass("Press Enter to quit in a few seconds...")
    sys.exit()
    
def notice_exit():
    print("")
    print(Fore.WHITE + "Data has been saved to desired location.")
    print(Fore.WHITE + "Quit automatically in 20 seconds...")
    time.sleep(20)
    sys.exit()

"""
def error_browser():    
    print("")
    print(Fore.WHITE + "If you already have Chrome or Firefox installed, but still see this message,",
                       "please check \"troubleshooting\" section on https://github.com/chengmarc/gecko-scan.")  
    print("")
    getpass.getpass("Press Enter to quit in a few seconds...")
    sys.exit()
"""

def error_url_timeout():
    print("")
    print(Fore.RED + "URL extraction timeout, please try again.")
    getpass.getpass("Press Enter to quit in a few seconds...")
    sys.exit()

def error_data_timeout():    
    print("")
    print(Fore.RED + "Data extraction timeout, please try again.")
    getpass.getpass("Press Enter to quit in a few seconds...")
    sys.exit()
    
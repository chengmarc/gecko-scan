# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import os, time
from urllib.parse import urlparse

script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

try:
    import pandas as pd
    from bs4 import BeautifulSoup as bs
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from colorama import init, Fore
    init()
    print(Fore.GREEN + "Core modules imported.")

except ImportError as e:
    print(f"The module '{e.name}' is not found, please install it using either pip or conda.")
    input('Press any key to quit.')
    exit()
    
# %% Functions for intializing webdrivers

def initialize_firefox():
    #mozilla/geckodriver 0.33.0
    options = FirefoxOptions()
    options.add_argument("-headless")
    driver_path = script_path + "\geckodriver.exe"
    driver = webdriver.Firefox(executable_path=driver_path, options=options)
    return driver

def initialize_chrome():
    #ChromeDriver 114.0.5735.90
    options = ChromeOptions()
    options.add_argument("--headless")
    driver_path = script_path + "\chromedriver.exe"
    driver = webdriver.Chrome(executable_path=driver_path, options=options)
    return driver

# %% Functions for getting key information in each category

def get_name(category_url:str) -> str:
    """
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

def get_num_of_pages(driver, category_url:str) -> int:
    """
    Precondition:   driver is a selenium web driver
                    category_url is the url of a specific crypto category      
    Return:         an integer that is the number of pages in this category

    # Example
    input:  driver, "www.coingecko.com/en/categories/smart-contract-platform"
    output: 2
    """
    driver.get(category_url)
    html = driver.page_source
    soup = bs(html, "html.parser").find_all('li', class_='page-item')
    num = int([obj.get_text() for obj in soup][-2])
    return num

def get_page_list(num, category_url:str) -> list[str]:
    """
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

def extract_dataframe(driver, url_lst:list[str]) -> pd.DataFrame:
    """
    Precondition:   driver is a selenium web driver
                    url_list is a list of strings that contains the urls of all the pages in a category                  
    Return:         a pandas dataframe that contains all the market data of this category

    # Example
    input:  a selenium web driver,  ["www.coingecko.com/en/categories/smart-contract-platform",
                                     "www.coingecko.com/en/categories/smart-contract-platform?page=2"]
    output: a pandas dataframe with 150 rows of market data (100 rows on the first page, 50 rows on the second)
    """
    df_clean = pd.DataFrame(columns = ['Symbol', 'Name', 'Price', 'Change1h', 
                                       'Change24h', 'Change7d', 'Volume24h', 'MarketCap'])
    for url in url_lst:
        driver.get(url)
        html = driver.page_source
        soup = bs(html, "html.parser").find('div', class_='coingecko-table')

        df_page = extract_page(soup)
        df_clean = pd.concat([df_clean, df_page], axis=0, ignore_index=True)

        print(Fore.WHITE, "Extracting information...")
        time.sleep(1)

    return df_clean

def trim_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
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

# %% Function for user notice

def notice_data_ready():
    print("")
    print(Fore.GREEN + "       _ _       _       _                             _       ")
    print(Fore.GREEN + "  __ _| | |   __| | __ _| |_ __ _   _ __ ___  __ _  __| |_   _ ")
    print(Fore.GREEN + " / _` | | |  / _` |/ _` | __/ _` | | '__/ _ \/ _` |/ _` | | | |")
    print(Fore.GREEN + "| (_| | | | | (_| | (_| | || (_| | | | |  __/ (_| | (_| | |_| |")
    print(Fore.GREEN + " \__,_|_|_|  \__,_|\__,_|\__\__,_| |_|  \___|\__,_|\__,_|\__, |")
    print(Fore.GREEN + "                                                         |___/ ")
    print("")
    
def notice_wait_20():
    print("")
    print(Fore.YELLOW + "Wait 20 seconds to avoid being blocked.")
    print("")
    
def error_chrome():    
    print("")
    print(Fore.WHITE + "If you already have Chrome installed, but still see this message,",
                       "please check \"troubleshooting\" section on https://github.com/chengmarc/gecko-scan.")  
    print("")
    input(Fore.WHITE + 'Press any key to quit.')
    exit()

def error_url_timeout():
    print("")
    print(Fore.RED + "URL extraction timeout, please try again.")
    input(Fore.WHITE + 'Press any key to quit.')
    exit()  

def error_cloudflare():    
    print("")
    print(Fore.RED + "Cloudflare has blocked the traffic, please try again.")
    input(Fore.WHITE + 'Press any key to quit.')
    exit()
    
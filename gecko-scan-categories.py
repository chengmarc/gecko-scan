# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
try:
    # Import standard libraries
    import os, time, datetime, configparser
    from urllib.parse import urlparse
    
    # Import core libraries
    import pandas as pd
    from bs4 import BeautifulSoup as bs
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.firefox.service import Service
    from colorama import init, Fore
    init()
    print(Fore.GREEN + "All libraries imported.")

except:
    print("Dependencies missing, please use pip/conda to install all dependencies.")
    print("Standard libraries:      os, time, datetime, configparser")
    print("Core libraries:          pandas, bs4, selenium, colorama")
    input('Press any key to quit.')
    exit()
    
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

# %% Initialize web driver
options = Options()
options.add_argument("-headless")
service = Service(script_path + "\geckodriver.exe")

try:
    driver = webdriver.Firefox(service=service, options=options)
    print(Fore.GREEN + "Web driver initialized.")

except:
    print(Fore.RED + "Firefox Browser missing, please install Firefox Browser.")
    input('Press any key to quit.')
    exit()

# %% Getting urls in the page "Categories"
base_url = 'https://www.coingecko.com'
driver.get('https://www.coingecko.com/en/categories')
html = driver.page_source
soup = bs(html, 'html.parser').find('tbody').find_all('a')

categories_url = []
for link in soup:
    href = str(link.get('href'))
    if "categories" in href and "ecosystem" not in href:
        categories_url.append(base_url + href)
categories_url = list(dict.fromkeys(categories_url))
del soup, html, href, base_url

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

        print(Fore.WHITE + "Extracting information...")
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

print(Fore.WHITE + "Preparation for extraction is ready.")

# %% Main Execution
data_dictionary, reset_threshold = {}, 0

try:
    for url in categories_url:
        category = get_name(url)
        num = get_num_of_pages(driver, url)
        pages = get_page_list(num, url)
        data = extract_dataframe(driver, pages)
        data = trim_dataframe(data)
        data_dictionary[category] = data
        print(Fore.YELLOW + "Successfully extracted data for " + category)

        reset_threshold += num
        if reset_threshold > 30:
            print(Fore.YELLOW + "Wait 20 seconds to avoid being blocked.")
            reset_threshold = 0
            time.sleep(20)

    print(Fore.GREEN + "       _ _       _       _                             _       ")
    print(Fore.GREEN + "  __ _| | |   __| | __ _| |_ __ _   _ __ ___  __ _  __| |_   _ ")
    print(Fore.GREEN + " / _` | | |  / _` |/ _` | __/ _` | | '__/ _ \/ _` |/ _` | | | |")
    print(Fore.GREEN + "| (_| | | | | (_| | (_| | || (_| | | | |  __/ (_| | (_| | |_| |")
    print(Fore.GREEN + " \__,_|_|_|  \__,_|\__,_|\__\__,_| |_|  \___|\__,_|\__,_|\__, |")
    print(Fore.GREEN + "                                                         |___/ ")
    driver.quit()

except:
    print(Fore.RED + "Cloudflare has blocked the traffic, please try again.")
    driver.quit()

    input(Fore.WHITE + 'Press any key to quit.')
    exit()

# %% Export data to desired location
config = configparser.ConfigParser()
config.read('gecko-scan config.ini')
output_path = config.get('Paths', 'output_path')

current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

for category, dataframe in data_dictionary.items():
    output_name = category + '-' + formatted_datetime + ".csv"
    dataframe.to_csv(output_path + "\\" + output_name)

print("")
print(Fore.WHITE + "Data has been saved to desired location.")
print(Fore.WHITE + "Quitting automatically after 5 seconds.")

time.sleep(5)

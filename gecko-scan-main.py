# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
try:
    # Import core libraries
    import pandas as pd
    from bs4 import BeautifulSoup as bs
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options

    # Import libraries for utilities
    import os, time, datetime, configparser
    from colorama import init, Fore
    init()
    print(Fore.GREEN + "All libraries imported.")

except:
    print("Dependencies missing, please use pip to install all dependencies:")
    print("pandas, bs4, selenium, os, time, datetime, configparser, colorama")
    input('Press any key to quit.')
    exit()

# %% Initialize web driver
options = Options()
options.add_argument("-headless")

try:
    driver = webdriver.Firefox(options=options)
    print(Fore.GREEN + "Web driver initialized.")

except:
    print(Fore.RED + "Firefox Browser missing, please install Firefox Browser.")
    input('Press any key to quit.')
    exit()

# %% Getting the number of pages and the urls of all pages
base_url = "https://www.coingecko.com/"
driver.get(base_url)
html = driver.page_source
soup = bs(html, "html.parser").find_all('li', class_='page-item')

total_pages = int([obj.get_text() for obj in soup][-2])
pages = [base_url]
for i in range(2, total_pages+1):
    pages.append(base_url + "?page=" + str(i))
del soup, html, base_url

# %% Function for data mining

def extract_page(soup) -> pd.DataFrame:
    """
    Precondition:   soup is a BeautifulSoup object parsed from a specific page html   
    Return:         a pandas dataframe that contains the market data of the given page

    # Example
    input:  a BeautifulSoup object parsed from "www.coingecko.com/?page=5"
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

print(Fore.WHITE + "Preparation for extraction is ready.")

# %% Main Execution
reset_threshold = 0
df_clean = pd.DataFrame(columns = ['Symbol', 'Name', 'Price', 'Change1h', 
                                   'Change24h', 'Change7d', 'Volume24h', 'MarketCap'])

for url in pages:
    driver.get(url)
    html = driver.page_source
    soup = bs(html, "html.parser")
    soup = soup.find('div', class_='coingecko-table')

    df_page = extract_page(soup)
    df_clean = pd.concat([df_clean, df_page], axis=0, ignore_index=True)

    reset_threshold += 1
    if reset_threshold > 30:
        print(Fore.YELLOW + "Wait 20 seconds to avoid being blocked.")
        reset_threshold = 0
        time.sleep(20)

    print(Fore.WHITE + "Extracting information...")
    time.sleep(1)

driver.quit()
del url, html, pages, df_page

print(Fore.GREEN + "Successfully extracted all market data.")

# %% Data cleaning
df_trim = df_clean.copy()
for column in df_trim.columns:
    df_trim[column] = df_trim[column].str.strip()
del column

# Remove USD currency symbol
df_trim['Price'] = df_trim['Price'].str[1:]
df_trim['Volume24h'] = df_trim['Volume24h'].str[1:]
df_trim['MarketCap'] = df_trim['MarketCap'].str[1:]

print(Fore.WHITE + "Data cleaning completed.")

# %% Export data to desired location
script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

config = configparser.ConfigParser()
config.read('gecko-scan config.ini')
output_path = config.get('Paths', 'output_path')

current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
output_name = "all-crypto-" + formatted_datetime + ".csv"

df_trim.to_csv(output_path + "\\" + output_name)

print("")
print(Fore.GREEN + "Data has been saved to desired location.")
print(Fore.WHITE + "Quitting automatically after 5 seconds.")

time.sleep(5)

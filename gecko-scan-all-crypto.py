# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
try:
    # Import standard libraries
    import os, time, datetime, configparser, warnings
    
    # Import core libraries
    import pandas as pd
    from bs4 import BeautifulSoup as bs
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from colorama import init, Fore
    init()
    print(Fore.GREEN + "All libraries imported.")

except ImportError as e:
    print(f"The module '{e.name}' is not found, please install it using either pip or conda.")
    input('Press any key to quit.')
    exit()
    
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

# %% Initialize web driver
warnings.filterwarnings("ignore", category=DeprecationWarning) 

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
    
try:
    driver = initialize_firefox()
    print(Fore.GREEN + "Mozilla driver initialized.")
except:
    print(Fore.YELLOW + "Firefox not detected, attempt to proceed with Chrome...")
    
    try:
        driver = initialize_chrome()
        print(Fore.GREEN + "Chrome driver initialized.")
    except:
        print(Fore.YELLOW + "Chrome not detected, aborting execution...")
        print("")
        print(Fore.YELLOW + "If you already have Chrome installed, but still see this message,",
                            "please check \"troubleshooting\" section on https://github.com/chengmarc/gecko-scan.")  
        print("")
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

print(Fore.WHITE + "Successfully extracted URLs.")

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
print("")

# %% Function for user notice
def print_ready():
    print("")
    print(Fore.GREEN + "       _ _       _       _                             _       ")
    print(Fore.GREEN + "  __ _| | |   __| | __ _| |_ __ _   _ __ ___  __ _  __| |_   _ ")
    print(Fore.GREEN + " / _` | | |  / _` |/ _` | __/ _` | | '__/ _ \/ _` |/ _` | | | |")
    print(Fore.GREEN + "| (_| | | | | (_| | (_| | || (_| | | | |  __/ (_| | (_| | |_| |")
    print(Fore.GREEN + " \__,_|_|_|  \__,_|\__,_|\__\__,_| |_|  \___|\__,_|\__,_|\__, |")
    print(Fore.GREEN + "                                                         |___/ ")
    
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
    if reset_threshold > 25:
        print("")
        print(Fore.YELLOW + "Wait 20 seconds to avoid being blocked.")
        print("")
        reset_threshold = 0
        time.sleep(20)

    print(Fore.WHITE, "Extracting information...")
    time.sleep(1)

print(Fore.GREEN, "Successfully extracted data for all crypto")
print_ready()
driver.quit()
del url, html, pages, df_page

# %% Data cleaning
df_trim = df_clean.copy()
for column in df_trim.columns:
    df_trim[column] = df_trim[column].str.strip()
del column

# Remove USD currency symbol
df_trim['Price'] = df_trim['Price'].str[1:]
df_trim['Volume24h'] = df_trim['Volume24h'].str[1:]
df_trim['MarketCap'] = df_trim['MarketCap'].str[1:]

# %% Set output path
config = configparser.ConfigParser()
config.read('gecko-scan config.ini')
if config.get('Paths', 'output_path_all_crypto') != "":
    output_path = config.get('Paths', 'output_path_all_crypto')
else:
    output_path = script_path + "\\all-crypto-daily"

# %% Export data to desired location
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
output_name = "all-crypto-" + formatted_datetime + ".csv"

df_trim.to_csv(output_path + "\\" + output_name)

# %% Notice User
print(Fore.WHITE + "Data has been saved to desired location.")
print(Fore.WHITE + "Quitting automatically after a minute.")

time.sleep(60)

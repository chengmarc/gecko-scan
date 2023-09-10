# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import os, time, datetime, configparser, warnings

script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

import gecko_scan_libraries as gsl
from colorama import init, Fore
init()

# %% Initialize web driver
warnings.filterwarnings("ignore", category=DeprecationWarning) 

try:
    driver = gsl.initialize_firefox()
    print(Fore.GREEN + "Mozilla driver initialized.")
except:
    print(Fore.YELLOW + "Firefox not detected, attempt to proceed with Chrome...")
    
    try:
        driver = gsl.initialize_chrome()
        print(Fore.GREEN + "Chrome driver initialized.")
    except:
        print(Fore.RED + "Chrome not detected, aborting execution...")
        gsl.error_chrome()

# %% Getting the number of pages and the urls of all pages
try: 
    base_url = "https://www.coingecko.com/"
    driver.get(base_url)
    html = driver.page_source
    soup = gsl.bs(html, "html.parser").find_all('li', class_='page-item')

    total_pages = int([obj.get_text() for obj in soup][-2])
    pages = [base_url]
    for i in range(2, total_pages+1):
        pages.append(base_url + "?page=" + str(i))
    print(Fore.WHITE + "Successfully extracted URLs.")
    
except:
    driver.quit()
    gsl.error_url_timeout()
    
# %% Main Execution
print("")

try:
    reset_threshold, df_clean = 0, gsl.pd.DataFrame(columns = ['Symbol', 'Name', 'Price', 'Change1h', 
                                                               'Change24h', 'Change7d', 'Volume24h', 'MarketCap'])
    for url in pages:
        driver.get(url)
        html = driver.page_source
        soup = gsl.bs(html, "html.parser")
        soup = soup.find('div', class_='coingecko-table')
        df_page = gsl.extract_page(soup)
        df_clean = gsl.pd.concat([df_clean, df_page], axis=0, ignore_index=True)

        reset_threshold += 1
        if reset_threshold > 25:
            gsl.notice_wait_20()
            reset_threshold = 0
            time.sleep(20)

        print(Fore.WHITE, "Extracting information...")
        time.sleep(1)
    
    df_clean = gsl.trim_dataframe(df_clean)

    driver.quit()
    gsl.notice_data_ready()

except:
    driver.quit()
    gsl.error_cloudflare()
    
# %% Set output path
config = configparser.ConfigParser()
config.read('gecko_scan config.ini')
if config.get('Paths', 'output_path_all_crypto') != "":
    output_path = config.get('Paths', 'output_path_all_crypto')
else:
    output_path = script_path + "\\all-crypto-daily"

# %% Export data to desired location
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
output_name = "all-crypto-" + formatted_datetime + ".csv"
df_clean.to_csv(output_path + "\\" + output_name)

# %% Notice User
print(Fore.WHITE + "Data has been saved to desired location.")
input(Fore.WHITE + 'Press any key to quit.')
exit()

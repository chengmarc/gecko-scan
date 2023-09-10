# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chen79gmarc

"""
import os, time, datetime
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

import gecko_scan_libraries as gsl
from colorama import init, Fore
init()

# %% Initialize web driver (Note: selenium and webdrivers are deprecated, requests is used instead.)
"""
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

try:
    raise Exception
    driver = gsl.initialize_firefox()
    print(Fore.GREEN + "Mozilla driver initialized.")
except:
    print(Fore.YELLOW + "Firefox not detected, attempt to proceed with Chrome...")
    
    try:
        driver = gsl.initialize_chrome()
        print(Fore.GREEN + "Chrome driver initialized.")
    except:
        print(Fore.RED + "Chrome not detected, aborting execution...")
        gsl.error_browser()
"""
# %% Getting the number of pages and the urls of all pages
try: 
    base_url = "https://www.coingecko.com/"
    response = gsl.requests.get(base_url, headers=gsl.headers)
    html = response.content
    soup = gsl.bs(html, "html.parser").find_all('li', class_='page-item')

    total_pages = int([obj.get_text() for obj in soup][-2])
    pages = [base_url]
    for i in range(2, total_pages+1):
        pages.append(base_url + "?page=" + str(i))
    print(Fore.WHITE + "Successfully extracted URLs.")
    
except:
    #driver.quit()
    gsl.error_url_timeout()
    
# %% Main Execution
try:
    print("")
    reset_threshold, df_clean = 0, gsl.pd.DataFrame(columns = ['Symbol', 'Name', 'Price', 'Change1h', 
                                                               'Change24h', 'Change7d', 'Volume24h', 'MarketCap'])
    for url in pages:        
        response = gsl.requests.get(url, headers=gsl.headers)
        html = response.content
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
        time.sleep(0.5)
    
    df_clean = gsl.trim_dataframe(df_clean)
    
    #driver.quit()
    gsl.notice_data_ready()

except:
    #driver.quit()
    gsl.error_data_timeout()

# %% Export data to desired location
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

output_path = gsl.get_output_path('output_path_all_crypto')
output_name = "all-crypto-" + formatted_datetime + ".csv"
df_clean.to_csv(output_path + "\\" + output_name)

gsl.notice_exit()

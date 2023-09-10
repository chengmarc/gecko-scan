# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

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
# %% Getting urls in the page "Categories"
try:
    base_url = 'https://www.coingecko.com'
    response = gsl.requests.get("https://www.coingecko.com/en/categories", headers=gsl.headers)
    html = response.content
    soup = gsl.bs(html, 'html.parser').find('tbody').find_all('a')

    categories_url = []
    for link in soup:
        href = str(link.get('href'))
        if "categories" in href and "ecosystem" not in href:
            categories_url.append(base_url + href)
            categories_url = list(dict.fromkeys(categories_url))
    print(Fore.WHITE + "Successfully extracted URLs.")
    
except:
    #driver.quit()
    gsl.error_url_timeout()
    
# %% Main Execution
try:
    print("")
    data_dictionary, reset_threshold = {}, 0
    for url in categories_url:
        category = gsl.get_name(url)
        num = gsl.get_num_of_pages(gsl.headers, url)
        pages = gsl.get_page_list(num, url)
        data = gsl.extract_dataframe(gsl.headers, pages)
        data = gsl.trim_dataframe(data)
        data_dictionary[category] = data
        print(Fore.GREEN, "Successfully extracted data for " + category)

        reset_threshold += num
        if reset_threshold > 25:
            gsl.notice_wait_20()
            reset_threshold = 0
            time.sleep(20)

    #driver.quit()
    gsl.notice_data_ready()
    
except:
    #driver.quit()
    gsl.error_data_timeout()

# %% Export data to desired location
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

output_path = gsl.get_output_path('output_path_categories')
for category, dataframe in data_dictionary.items():
    output_name = category + '-' + formatted_datetime + ".csv"
    dataframe.to_csv(output_path + "\\" + output_name)
    
gsl.notice_exit()

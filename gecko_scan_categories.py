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
    
# %% Getting urls in the page "Categories"
try:
    base_url = 'https://www.coingecko.com'
    driver.get('https://www.coingecko.com/en/categories')
    html = driver.page_source
    soup = gsl.bs(html, 'html.parser').find('tbody').find_all('a')

    categories_url = []
    for link in soup:
        href = str(link.get('href'))
        if "categories" in href and "ecosystem" not in href:
            categories_url.append(base_url + href)
            categories_url = list(dict.fromkeys(categories_url))
    print(Fore.WHITE + "Successfully extracted URLs.")
    
except:
    driver.quit()
    gsl.error_url_timeout()
    
# %% Main Execution
print("")

try:
    data_dictionary, reset_threshold = {}, 0
    for url in categories_url:
        category = gsl.get_name(url)
        num = gsl.get_num_of_pages(driver, url)
        pages = gsl.get_page_list(num, url)
        data = gsl.extract_dataframe(driver, pages)
        data = gsl.trim_dataframe(data)
        data_dictionary[category] = data
        print(Fore.GREEN, "Successfully extracted data for " + category)

        reset_threshold += num
        if reset_threshold > 25:
            gsl.notice_wait_20()
            reset_threshold = 0
            time.sleep(20)

    driver.quit()
    gsl.notice_data_ready()
    
except:
    driver.quit()
    gsl.error_cloudflare()
    
# %% Set output path
config = configparser.ConfigParser()
config.read('gecko_scan config.ini')
if config.get('Paths', 'output_path_categories') != "":
    output_path = config.get('Paths', 'output_path_categories')
else:
    output_path = script_path + "\\categories-daily"

# %% Export data to desired location
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
for category, dataframe in data_dictionary.items():
    output_name = category + '-' + formatted_datetime + ".csv"
    dataframe.to_csv(output_path + "\\" + output_name)

# %% Notice User
print(Fore.WHITE + "Data has been saved to desired location.")
input(Fore.WHITE + 'Press any key to quit.')
exit()


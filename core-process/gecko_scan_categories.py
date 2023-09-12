# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import os
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

import gecko_scan_libraries as gsl
from colorama import init, Fore
init()

# %% Extract urls
try:
    response = gsl.requests.get("https://www.coingecko.com/en/categories", headers=gsl.headers)
    html = response.content
    soup = gsl.bs(html, "html.parser").find("tbody").find_all("a")

    categories_url = []
    for link in soup:
        href = str(link.get("href"))
        if "categories" in href and "ecosystem" not in href:
            categories_url.append(gsl.base_url + href)
            categories_url = list(dict.fromkeys(categories_url))
    print(Fore.WHITE + "Successfully extracted URLs.")

except:
    gsl.error_url_timeout()

# %% Extract data
try:
    print("")
    data_dictionary, reset_threshold = {}, 0

    for url in categories_url:
        category = gsl.get_category_name(url)
        num = gsl.get_num_of_pages(gsl.headers, url)
        pages = gsl.get_page_list(num, url)
        data = gsl.extract_dataframe(gsl.headers, pages)
        data = gsl.trim_dataframe(data)
        data_dictionary[category] = data
        print(Fore.WHITE, f"- Successfully extracted data for {category}")

        reset_threshold += num
        if reset_threshold > 25:
            gsl.notice_wait_20()
            reset_threshold = 0
            gsl.time.sleep(20)

    print("")
    print(Fore.GREEN + "All data ready.")

except:
    gsl.error_data_timeout()

# %% Export data
try:
    output_path, valid = gsl.get_and_check_config("output_path_categories", os.path.dirname(script_path))
    for category, dataframe in data_dictionary.items():
        output_name = f"{category}-{gsl.get_datetime()}.csv"
        dataframe.to_csv(gsl.os.path.join(output_path, output_name))
    if valid:
        gsl.notice_save_desired()
    else:
        gsl.notice_save_default()

except:
    gsl.error_save_failed()

gsl.sys.exit()

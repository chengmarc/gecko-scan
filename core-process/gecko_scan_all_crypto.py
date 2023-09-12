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
    response = gsl.requests.get("https://www.coingecko.com/", headers=gsl.headers)
    html = response.content
    soup = gsl.bs(html, "html.parser").find_all("li", class_="page-item")

    total_pages = int([obj.get_text() for obj in soup][-2])
    pages = [gsl.base_url]
    for i in range(2, total_pages + 1):
        pages.append(f"{gsl.base_url}?page={str(i)}")
    print(Fore.WHITE + "Successfully extracted URLs.")

except:
    gsl.error_url_timeout()

# %% Extract data
try:
    print("")
    reset_threshold, df_clean = 0, gsl.pd.DataFrame(
        columns=["Symbol", "Name", "Price", "Change1h", "Change24h", "Change7d", "Volume24h", "MarketCap"])

    for url in pages[:1]:
        response = gsl.requests.get(url, headers=gsl.headers)
        html = response.content
        soup = gsl.bs(html, "html.parser")
        soup = soup.find("div", class_="coingecko-table")
        df_page = gsl.extract_page(soup)
        df_clean = gsl.pd.concat([df_clean, df_page], axis=0, ignore_index=True)
        print(Fore.WHITE, "- Extracting information...")
        gsl.time.sleep(0.5)

        reset_threshold += 1
        if reset_threshold > 25:
            gsl.notice_wait_20()
            reset_threshold = 0
            gsl.time.sleep(20)

    df_clean = gsl.trim_dataframe(df_clean)

    print("")
    print(Fore.GREEN + "All data ready.")

except:
    gsl.error_data_timeout()

# %% Export data
try:
    output_path, valid = gsl.get_and_check_config("output_path_all_crypto", os.path.dirname(script_path))
    output_name = f"all-crypto-{gsl.get_datetime()}.csv"
    df_clean.to_csv(gsl.os.path.join(output_path, output_name))
    if valid:
        gsl.notice_save_desired()
    else:
        gsl.notice_save_default()

except:
    gsl.error_save_failed()

gsl.sys.exit()

# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import gecko_scan_libraries as gsl


def main(path):

    gsl.notice_start("Extract Historical Database")  

    """
    This try-except block will:
        1. Create a list of urls that directs to the database
        2. Seperate the full list into batches to prevent stack overflow
    """
    try:
        url_list = [f"https://www.coingecko.com/price_charts/export/{str(i+1)}/usd.csv" for i in range(32000)]
        print(gsl.Fore.WHITE + f"{len(url_list)} URLs has been loaded.")

        batch_size = 1000
        batch_list = []
        for i in range(0, len(url_list), batch_size):
            batch_list.append(url_list[i:i + batch_size])
        print(gsl.Fore.WHITE + f"{len(batch_list)} batches has been created.")
    except:
        gsl.error_url_timeout()

    """
    This try-except block will:
        1. Iterate through each batch in the given list
        1. Recursively download the database for each batch
    """
    try:
        print("")
        output_path = path
        for url_list in batch_list:
            gsl.recursive_download(url_list, output_path)
        print("")
        print(gsl.Fore.GREEN + "All data ready.")
        gsl.notice_save_success()

    except:
        gsl.error_save_failed()

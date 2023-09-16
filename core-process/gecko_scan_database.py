# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import os
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

import gecko_scan_libraries as gsl

# %% Load or create list of urls
try:
    url_file = open(gsl.os.path.join(os.path.dirname(script_path), "recursive-process", "url_validation_verified.txt"), "r")
    url_list = url_file.read()
    url_list = url_list.split("\n")
    url_file.close()
    print(gsl.Fore.WHITE + f"Pre-validated URLs detected, {len(url_list)} URLs has been loaded.")
except:
    url_list = [f"https://www.coingecko.com/price_charts/export/{str(i+1)}/usd.csv" for i in range(32000)]
    print(gsl.Fore.WHITE + f"Pre-validated URLs not detected, {len(url_list)} URLs has been loaded.")

# %% Execution by batch to prevent stackoverflow
batch_size = 1000
batch_list = []
for i in range(0, len(url_list), batch_size):
    batch_list.append(url_list[i:i + batch_size])

# %% Main execution and data export
try:
    print("")
    output_path, valid = gsl.get_and_check_config("output_path_database", os.path.dirname(script_path))
    for url_list in batch_list:
        gsl.recursive_download(url_list, output_path)      
    print("")
    print(gsl.Fore.GREEN + "All data ready.")
    
    if valid:
        gsl.notice_save_desired()
    else:
        gsl.notice_save_default()

except:
    gsl.error_save_failed()

gsl.sys.exit()

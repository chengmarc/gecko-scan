# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import os, configparser
    
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

import gecko_scan_libraries as gsl
from colorama import init, Fore
init()

# %% Load or create list of urls
try: 
    url_file = open(script_path + "//gecko_scan_validated_urls.txt", "r")
    url_list = url_file.read()
    url_list = url_list.split('\n')
    url_file.close()
    print(Fore.WHITE + f"Pre-validated URLs detected, {len(url_list)} URLs has been loaded.")
except:
    url_list = [f"https://www.coingecko.com/price_charts/export/{str(i+1)}/usd.csv" for i in range(32000)]
    print(Fore.WHITE + f"Pre-validated URLs not detected, {len(url_list)} URLs has been loaded.") 
    
# %% Set output path
config = configparser.ConfigParser()
config.read('gecko_scan config.ini')
if config.get('Paths', 'output_path_database') != "":
    output_path = config.get('Paths', 'output_path_database')
else:
    output_path = script_path + "\\database"

# %% Execution by batch to prevent stackoverflow
batch_size = 1000
batch_list = []
for i in range(0, len(url_list), batch_size):
    batch_list.append(url_list[i:i + batch_size])
    
for url_list in batch_list:
    gsl.recursive_download(url_list, output_path)
gsl.notice_data_ready()

# %% Notice User
print(Fore.WHITE + "Data has been saved to desired location.")
input(Fore.WHITE + 'Press any key to quit.')
exit()

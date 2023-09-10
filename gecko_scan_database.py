# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import re, io, os, time, datetime, requests, configparser
    
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

import gecko_scan_libraries as gsl
from colorama import init, Fore
init()

# %%
try: 
    url_file = open(script_path + "//gecko_scan_validated_urls.txt", "r")
    url_list = url_file.read()
    url_list = url_list.split('\n')
    url_file.close()
    print(Fore.WHITE + f"Pre-validated URLs detected, {len(url_list)} URLs has been loaded.")
except:
    url_list = [f"https://www.coingecko.com/price_charts/export/{str(i+1)}/usd.csv" for i in range(32000)]
    print(Fore.WHITE + f"Pre-validated URLs not detected, {len(url_list)} URLs has been loaded.") 

# %% Functions for download and recursive process

def get_filename(response) -> str:
    if response.headers.get("Content-Disposition"):
        content_disposition = response.headers.get("Content-Disposition")
        filename_match = re.search(r'filename="(.+)"', content_disposition)
        filename = filename_match.group(1)
    else:
        current_time = datetime.datetime.now().strftime("%H-%M-%S")
        filename = f"no-name-{current_time}"
    return filename

def download_csv(response, filepath:str, filename:str):
    s = response.content
    df = gsl.pd.read_csv(io.StringIO(s.decode('utf-8')))
    df.to_csv(filepath + "//" + filename, encoding='utf-8')

def recursive_download(url_list:list, output_path:str):
    url = url_list[0]                   # Get the first URL from list_429 and send a request    
    response = requests.get(url, stream=True)
    response.status_code
    
    if response.status_code == 200:
        url_list.pop(0)
        output_name = get_filename(response)
        download_csv(response, output_path, output_name)
        print(Fore.GREEN, "Downloaded", url)
    elif response.status_code == 404:            # If status code is 404, simply remove from list_429
        url_list.pop(0)
        print(Fore.GREEN, "Discarded", url)
    elif response.status_code == 429:            # If status code is 429, do nothing
        print(Fore.YELLOW, "Skipped", url)
        
    return recursive_download(url_list, output_path)

# %% Main Execution
config = configparser.ConfigParser()
config.read('gecko_scan config.ini')
if config.get('Paths', 'output_path_database') != "":
    output_path = config.get('Paths', 'output_path_database')
else:
    output_path = script_path + "\\database"
    
print("")
recursive_download(url_list, output_path)
gsl.notice_data_ready()

# %% Notice User
print(Fore.WHITE + "Data has been saved to desired location.")
print(Fore.WHITE + "Quitting automatically after a minute.")
time.sleep(60)

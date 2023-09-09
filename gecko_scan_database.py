# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
try:
    # Import standard libraries
    import re, io, os, time, requests, configparser
    
    # Import core libraries
    import pandas as pd
    from colorama import init, Fore
    init()
    print(Fore.GREEN + "All libraries imported.")

except ImportError as e:
    print(f"The module '{e.name}' is not found, please install it using either pip or conda.")
    input('Press any key to quit.')
    exit()
    
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

# %% Functions for .csv download
  
def get_filename(url:str) -> str:
    response = requests.get(url, stream=True)    
    if response.status_code == 200 and response.headers.get("Content-Disposition"):
        content_disposition = response.headers.get("Content-Disposition")
        filename_match = re.search(r'filename="(.+)"', content_disposition)
    else:
        filename_match = None
        
    if filename_match:
        filename = filename_match.group(1)
        print(Fore.WHITE, "Deteceted", filename)
        return filename
    else:
        print(Fore.YELLOW, "No file detected for", url)
        return None

def download_csv(url:str, filepath:str, filename:str):
    s = requests.get(url).content
    df = pd.read_csv(io.StringIO(s.decode('utf-8')))
    df.to_csv(filepath + "//" + filename, encoding='utf-8')
    print(Fore.GREEN, "Downloaded", filename)    

print(Fore.WHITE + "Preparation for download is ready.")
print("")

# %% Function for user notice
def print_ready():
    print("")
    print(Fore.GREEN + "       _ _       _       _                             _       ")
    print(Fore.GREEN + "  __ _| | |   __| | __ _| |_ __ _   _ __ ___  __ _  __| |_   _ ")
    print(Fore.GREEN + " / _` | | |  / _` |/ _` | __/ _` | | '__/ _ \/ _` |/ _` | | | |")
    print(Fore.GREEN + "| (_| | | | | (_| | (_| | || (_| | | | |  __/ (_| | (_| | |_| |")
    print(Fore.GREEN + " \__,_|_|_|  \__,_|\__,_|\__\__,_| |_|  \___|\__,_|\__,_|\__, |")
    print(Fore.GREEN + "                                                         |___/ ")
    
# %% Set output path
config = configparser.ConfigParser()
config.read('gecko-scan config.ini')
if config.get('Paths', 'output_path_database') != "":
    output_path = config.get('Paths', 'output_path_database')
else:
    output_path = script_path + "\\database"

# %% Main Execution
for i in range(10):
    url = "https://www.coingecko.com/price_charts/export/" + str(i+1) + "/usd.csv"
    output_name = get_filename(url)
    if output_name is not None:
        download_csv(url, output_path, output_name)   
        
print_ready()

# %% Notice User
print(Fore.WHITE + "Data has been saved to desired location.")
print(Fore.WHITE + "Quitting automatically after a minute.")

time.sleep(60)

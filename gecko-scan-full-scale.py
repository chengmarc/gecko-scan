# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
try:
    # Import standard libraries
    import pandas as pd
    
    # Import core libraries
    import re, io, os, time, requests, configparser
    from colorama import init, Fore
    init()
    print(Fore.GREEN + "All libraries imported.")

except:
    print("Dependencies missing, please use pip/conda to install all dependencies.")
    print("Standard libraries:      re, io, os, time, requests, configparser")
    print("Core libraries:          pandas")
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

# %% Main Execution
config = configparser.ConfigParser()
config.read('gecko-scan config.ini')
output_path = config.get('Paths', 'output_path')

base_url = 'https://www.coingecko.com'

for i in range(10):
    sub_url = "/price_charts/export/" + str(i) + "/usd.csv"
    output_name = get_filename(base_url + sub_url)
    if output_name is not None:
        download_csv(base_url + sub_url, output_path, output_name)   

print("")
print(Fore.WHITE + "Data has been saved to desired location.")
print(Fore.WHITE + "Quitting automatically after 5 seconds.")

time.sleep(5)

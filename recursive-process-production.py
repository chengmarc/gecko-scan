# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import os, requests

script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

# %% Recursive function to verify all urls until list_429 is empty

def process_urls(list_200, list_429):
    if not list_429:                    # Base case: if list_429 is empty, return the updated lists
        return list_200, list_429
    
    url = list_429[0]                   # Get the first URL from list_429 and send a request
    status_code = requests.head(url).status_code
    
    if status_code == 200:              # If status code is 200, add to list_200 and remove from list_429
        list_200.append(url)
        list_429.pop(0)
        print("Appended", url)
    elif status_code == 404:            # If status code is 404, simply remove from list_429
        list_429.pop(0)
        print("Discarded", url)
    elif status_code == 429:            # If status code is 429, do nothing and proceed to the next URL
        print("Skipped", url)
    
    return process_urls(list_200, list_429)

# %% Main Execution
list_200 = []
list_429 = []     
for i in range(32000):       
    url = "https://www.coingecko.com/price_charts/export/" + str(i+1) + "/usd.csv"
    list_429.append(url)

final_200, final_429 = process_urls(list_200, list_429)

# %% Output to .txt file
filename = script_path + "\\recursive-process-output.txt"
file = open(filename,'w')
for url in final_200:
	file.write(url + "\n")
file.close()

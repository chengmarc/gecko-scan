# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import os, time, requests

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
        time.sleep(0.5)
    elif status_code == 404:            # If status code is 404, simply remove from list_429
        list_429.pop(0)
        print("Discarded", url)
        time.sleep(0.5)
    elif status_code == 429:            # If status code is 429, do nothing
        print("Skipped", url)
        time.sleep(20)
    
    return process_urls(list_200, list_429)

# %% Execution by batch to prevent stackoverflow
def list_429_per_batch(i:int, j:int) -> list:
    list_429 = []
    for i in range(i, j):       
        url = "https://www.coingecko.com/price_charts/export/" + str(i+1) + "/usd.csv"
        list_429.append(url)
    return list_429

""" 
##### Warning #####

Currently there are about 32000 urls needs to be validated.
Recursive alogarithm will send about 50 requests per minute.
Validate all 32000 urls will take around 10 hours. 

I have already run this alogarithm and saved a list of validated urls in "url_validation_verified.txt".
This list should be more than enough.
Do not run this alogarithm unless you have fully understand every line of code.
"""

batch_size = 1000

final_list_200 = []
for batch_index in range(0, 32):
    start = batch_index * batch_size
    end = (batch_index + 1) * batch_size
    list_200 = []
    list_429 = list_429_per_batch(start, end)
    list_200, list_429 = process_urls(list_200, list_429)
    final_list_200.extend(list_200)

# %% Output to .txt file
filename = script_path + "\\url_validation_output.txt"
file = open(filename,'w')
for url in final_list_200:
	file.write(url + "\n")
file.close()

# %% Notice User
print(f"{len(final_list_200)} URLs are validated")
print("Quitting automatically after a minute.")
time.sleep(60)
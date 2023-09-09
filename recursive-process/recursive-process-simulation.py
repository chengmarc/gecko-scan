# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import random

# %% Simulation of server behavior

# Given a url, the server will check if this url is valid.
# If it is valid, then the server will return 200.
# Otherwise, the server will return 404.
# However, if too much requests are sent, the server will block the request and return 429.

# This dictionary is a simulation of what should be returned.
dictionary = {0: 200, 1: 200, 2:200, 3:404, 4:404,
              5: 200, 6: 200, 7:404, 8:200, 9:404}

# This function is a simulation of what will be returned.
def request_status(i: int) -> int:
    reject = random.randint(0, 1)
    if reject == 1:
        return 429
    if reject == 0:
        return dictionary[i]
        
# %% Recursive function to verify all urls until list_429 is empty

def process_urls(list_200, list_429):
    if not list_429:                    # Base case: if list_429 is empty, return the updated lists
        return list_200, list_429
    
    url = list_429[0]                   # Get the first URL from list_429 and send a request
    status_code = request_status(url)
    
    if status_code == 200:              # If status code is 200, add to list_200 and remove from list_429
        list_200.append(url)
        list_429.pop(0)
        print("Appended", url)
    elif status_code == 404:            # If status code is 404, simply remove from list_429
        list_429.pop(0)
        print("Discarded", url)
    elif status_code == 429:            # If status code is 429, do nothing
        print("Skipped", url)
    
    return process_urls(list_200, list_429)
    
# %% Main Execution
list_200 = []
list_429 = []     
for i in range(10):
    list_429.append(i)

final_200, final_429 = process_urls(list_200, list_429)

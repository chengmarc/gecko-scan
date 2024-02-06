# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import os
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

with open("links.html", "w") as file:
    file.write("<html>\n")
    file.write("<body>\n")

    for i in range(20, 40):
        link = f"https://www.coingecko.com/price_charts/export/{i}/usd.csv"
        file.write(f"<a href='{link}'>{link}</a><br>\n")

    file.write("</body>\n")
    file.write("</html>\n")


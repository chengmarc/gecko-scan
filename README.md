# Introduction
**gecko-scan** is a web crawler that extract data from the famous cryptocurrency website CoinGecko (a site that hosts up-to-date data on cryptocurrencies). **gecko-scan** will help you download all the data into **.csv** format and store it locally, so that you can perform quantitative analysis using your favourite data science tools.

# First time use
1. Install **Python 3.10.11** on your computer. \
(note: should also work with other versions of Python, but not tested)

2. Download this repository as a **.zip** file and extract it.
3. Double click **execute_all.bat** and data will be extracted automatically. \
(note: virtual environment will be created under "core-process" so it won't mess up with your existing environment)

# For further use
Normally, you only need to double click **execute_all.bat**. This will takes around *10 minutes* and extract a daily snapshot of the cryptomarket. It is recommended to do this daily or weekly. This batch file executes **gecko_scan_all_crypto.py** and **gecko_scan_categories.py** in <ins>"core-process"</ins>.

For historical data, you will need to double click **database.bat**. This will takes around *10 hours* and extract the historical data of around 25000 coins and tokens. This batch file executes **gecko_scan_database.py** in <ins>"core-process"</ins>.

# Save location
By default, data are saved under <ins>"all-crypto-daily"</ins>, <ins>"categories-daily"</ins>, and <ins>"database"</ins>. \
If you want to change the output location, please edit in **config.ini**

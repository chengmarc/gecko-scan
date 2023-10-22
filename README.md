# Introduction
**gecko-scan** is a web crawler that extract data from the famous cryptocurrency website CoinGecko (a site that hosts up-to-date data on cryptocurrencies). **gecko-scan** will help you download all the data into **.csv** format and store it locally, so that you can perform quantitative analysis using your favourite data science tools.

# First time use
Go to **Releases** on the right of this page, and download the **.exe** file. That's it.

If you have Python installed, you can also: 
1. Download this repository as a **.zip** file and extract it.
2. Double click **gecko-scan.bat** and launch the application. \
(note: virtual environment will be created under "core-process" so it won't mess up with your existing environment)

# For further use
Normally, you only need to check the first two checkbox. This will takes around *10 minutes* and extract a daily snapshot of the cryptomarket. It is recommended to do this daily or weekly.

For historical data, you need to check **Database of Historical Prices**. This will takes around *10 hours* and extract the historical data of around 25000 coins and tokens. 

# Save location
By default, data are saved under "<ins>C:\Users\Public\Documents</ins>" \
If you want to change the output location, please edit in **config.ini** under "<ins>C:\Users\Public</ins>".


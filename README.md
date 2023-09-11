

# Introduction
**gecko-scan** is a web crawler that extract data from the famous cryptocurrency website CoinGecko (a site that hosts up-to-date data on cryptocurrencies). **gecko-scan** will help you download all the data into **.csv** format and store it locally, so that you can perform quantitative analysis using your favourite data science tools.

# First time use
First, make sure to install **Python 3.10.11** on your computer.

Second, simply download this repository as a **.zip** file and extract it. 

Finally, you would also need to install all the dependencies using either **pip** or **conda**. 
```
pip install requests pandas bs4 colorama
conda install requests pandas bs4 colorama
```

Now you are all set, simply double click **execute.bat** and data will be extracted automatically.

# For further use
**execute.bat** is a batch file that execute **gecko_scan_all_crypto.py** and **gecko_scan_categories.py**. Normally, you only need to double click this file.

- **gecko_scan_all_crypto.py** is an **.html** crawler, it extracts all cryptocurrencies data without splitting them into categories. This script is recommended to be executed daily or weekly.
- **gecko_scan_categories.py** is an **.html** crawler, it extracts cryptocurrencies data per category. This script is recommended to be executed daily or weekly.
- **gecko_scan_database.py** is a **.csv** download script, it directly downloads from CoinGecko's database and saves it locally. Running it will extract about 26000 **.csv** file, which will take around 10 hours. This script is recommended for one-time execution only.
# Troubleshooting
While **selenium** is more suitable fore dynamic website interactions, **requests** is less resource dependent and more suitable for our purpose. Hence, **requests** has been implemented to replace **selenium**. There should be no more browser issues. 

<del>Currently, **gecko-scan** has with two webdrivers: Mozilla's **geckodriver.exe** (x64 version 0.33.0) and Chrome's **chromedriver.exe** (x32 version 114.0.5735.90).<del>

<del>- **geckodriver.exe** works with Firefox Browser.<del>
<del>- **chromedriver.exe** works with Chrome Browser.<del>

<del>Here's the catch, **geckodriver.exe** usually supports the latest Firefox Browser, **chromedriver.exe** is usually a few versions behind the latest Chrome Browser. If you are encoutering this issue, it's likely that your Chrome Browser's version is too new. <del>

<del>Here's two ways you can solve it: <del>
<del>- Install the latest Firefox Browser, or<del>
<del>- Install an old version of Chrome Browser.<del>

<del>It is always recommended to install Firefox Browser, since the latest version will always be supported.~<del>

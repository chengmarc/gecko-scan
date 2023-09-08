
# Introduction
**gecko-scan** is a web crawler that extract data from the famous cryptocurrency website CoinGecko (a site that hosts up-to-date data on cryptocurrencies). **gecko-scan** will help you download all the data into **.csv** format and store it locally, so that you can perform quantitative analysis using your favourite data science tools.

# First time use
First, make sure to install **Git** and **Python** on your computer, see the links are given below:
- Git: https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe
- Python: https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe 

Second, clone this repository using **Git Bash** using the line below, or simply download it as a **.zip** file and extract it.
```
git clone git@github.com:chengmarc/gecko-scan.git
```

Finally, you would also need to install all the dependencies using either **pip** or **conda**. 
```
pip install pandas bs4 requests selenium colorama
conda install pandas bs4 requests selenium colorama
```

Now you are all set, simply double click **gecko-scan execute-all.bat** and the program will run automatically.

# For further use
For consistent data, **gecko-scan-all-crypto.py** and **gecko-scan-categories.py** are recommended to be executed daily or weekly. In contrast, **gecko-scan-database.py** is for one-time execution, execute it accordingly to your need.

- **gecko-scan-all-crypto.py** is an **.html** crawler, it extracts all cryptocurrencies data without splitting them into categories.
- **gecko-scan-categories.py** is an **.html** crawler, it extracts cryptocurrencies data per category.
- **gecko-scan-database.py** is a **.csv** download tool, it directly download from CoinGecko's database and save it locally.

# Troubleshooting
```
Chrome not detected, aborting execution...
If you already have Chrome installed, but still see this message, please check "troubleshooting" section on https://github.com/chengmarc/gecko-scan.
```
Currently, **gecko-scan** has with two webdrivers: Mozilla's **geckodriver.exe** (x64 version 0.33.0) and Chrome's **chromedriver.exe** (x32 version 114.0.5735.90).

- **geckodriver.exe** works with Firefox Browser.
- **chromedriver.exe** works with Chrome Browser.

Here's the catch, **geckodriver.exe** usually supports the latest Firefox Browser, **chromedriver.exe** is usually a few versions behind the latest Chrome Browser. If you are encoutering this issue, it's likely that your Chrome Browser's version is too new. 

Here's two ways you can solve it: 
- Install the latest Firefox Browser, or
- Install an old version of Chrome Browser.

It is always recommended to install Firefox Browser, since the latest version will always be supported.

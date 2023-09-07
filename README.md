# Introduction
**gecko-scan** is a web crawler that extract data from the famous cryptocurrency website **CoinGecko** (a site that hosts up-to-date data on cryptocurrencies). **gecko-scan** will help you download all the data into **.csv** format and store it locally, so that you can perform quantitative analysis using your favourite data science tools.

# First time use
First, make sure to install **Git** and **Python** on your computer, see the links are given below:
- Git: https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe
- Python: https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe 

Second, you want to clone this repository using **Git Bash** using the line below, or simply download it as a **.zip** file and extract it.
```
git@github.com:chengmarc/gecko-scan.git
```

Finally, you would also need to install all the dependencies using either **pip** or **conda**. 
```
pip install pandas bs4 selenium colorama
conda install pandas bs4 selenium colorama
```

Now you are all set, simply double click **gecko-scan execute-all.bat** and the program will run automatically.


## Description
A webscraping application to split bills between my roommates and I.

Using Selenium to grab bills from Avista Utilies and Spectrum Internet.
Calculates how to split up the bills. Sends Venmo requests to whomever
specified. Sends emails to let specified people know the bill breakdown.

This is a purely personal project because I find splitting up the bills dreadful.
As such, this code is very hacky and low quality... it's meant to be a time savor
and I don't anticipate anyone having the exact same needs as me.

## Installation
Go to https://chromedriver.chromium.org/downloads and download a chromedriver.exe file that matches your version of chrome (Alternativly you could use firefox). Put chromedriver.exe in this directory. 

Rename the private_info_example.py file to private_info.py. Fill out private_info.py and it should work assuming you have valid account credentials and the like - good luck! But then again it wasn't really made to be used by others. 

Finally, run this:
```
pip install selenium
pip install yagmail
pip install venmo_api
python Scraper.py
```
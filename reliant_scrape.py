from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys
import selenium.webdriver as webdriver
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import selenium
import html5lib
import json
import os

def logon(headless, download_path, url, creds):
    """logon to reliant site.
    
    keyword arguments:
    headless (bool) - whether webscrape should be headless or not
    download_path (str) - filepath to save downloads
    url (str) - url to log on to
    creds (str) - filepath of user/password credentials
    
    returns:
    browser (selenium.WebDriver) - selenium webdriver object
    """
    
    opts = Options()
    opts.add_argument('--no-sandbox')
    opts.add_argument('--ignore-certificate-errors')
    opts.add_argument('--start-maximized')
    opts.add_argument('--disable-dev-shm-usage')
    #opts.binary_location = '/usr/bin/google-chrome-stable'
    
    with open(creds, 'r') as f:
        creds = json.load(f)

    if headless:
        opts.add_argument('--headless')
        assert opts.headless
        
        def enable_download_headless(browser, download_dir):
            browser.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
            params = {'cmd':'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
            browser.execute("send_command", params)
     
        prefs = {
            'download.default_directory': download_path,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': False,
            'safebrowsing.disable_download_protection': True}

    else:
        prefs = {
            'download.prompt_for_download': False,
            'safebrowsing.enabled': False,
            'safebrowsing.disable_download_protection': True}

    opts.add_experimental_option("prefs", prefs)

    browser = Chrome(executable_path = '/usr/local/bin/chromedriver', options = opts)
    
    if download_path and headless:
        enable_download_headless(browser, download_path)
        
    browser.get('https://www.reliant.com/public/altLogon.htm')
    
    user = browser.find_element_by_xpath("//input[@id='altLoginUsername']")
    checkbox = browser.find_element_by_xpath("//input[@id='altRememberMe']")
    password = browser.find_element_by_xpath("//input[@id='altLoginPassword']")
    
    user.send_keys(creds['user'])
    password.send_keys(creds['password'])
    
    logon = browser.find_element_by_css_selector("button[class*=myaccount-btn]")
    logon.click()
    wait = ui.WebDriverWait(browser,15)
    
    return(browser)

def acct_info(browser):
    """scrape basic user info.

    keyword arguments:
    browser (selenium.WebDriver) - selenium webdriver object

    returns:
    total (float) - account balance
    name (str) - user full name
    acct (str) - user account number
    address (str) - user service address
    """

    due = browser.find_element_by_xpath("//div[@class='resp-col-12-sm resp-col-8 left contentComponent']")
    welcome = browser.find_element_by_xpath("//div[@class='resp-col-5 resp-col-5-sm left colorWhite']")

    dollars, cents = due.text.split('\n')[1].split('$')[1].split('.')
    total = int(dollars) + int(cents)/100

    name_acct = welcome.text.split('\n')[0]
    address = welcome.text.split('\n')[1]

    name, acct = name_acct.split('(')
    name = ' '.join(name.split(' ')[:2])
    acct = acct.split(')')[0]
    return(total, name, acct, address)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as ui
import selenium.webdriver as webdriver
from selenium.webdriver import Chrome
from datetime import datetime, timedelta
#import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import selenium
import html5lib
import yaml
import json
import time
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
    # opts.binary_location = '/usr/bin/google-chrome-stable'
    
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

    # browser = Chrome(executable_path = '/usr/local/bin/chromedriver', options = opts)

    browser = Chrome(executable_path = 'chromedriver', options = opts)
    
    if download_path and headless:
        enable_download_headless(browser, download_path)
        
    browser.get(url)
    
    user = browser.find_element_by_xpath("//input[@id='altLoginUsername']")
    # checkbox = browser.find_element_by_xpath("//input[@id='altRememberMe']")
    password = browser.find_element_by_xpath("//input[@id='altLoginPassword']")
    
    user.send_keys(creds['user'])
    password.send_keys(creds['password'])
    
    logon = browser.find_element_by_css_selector("button[class*=myaccount-btn]")
    logon.click()
    #wait = ui.WebDriverWait(browser,15)
    
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

def table_to_df(browser):
    """parses acct page for usage data
    
    keyword arguments:
    browser (selenium.WebDriver) - browser object on account page
    
    returns:
    data (dataframe) - dataframe of usage table
    """
    
    soup = BeautifulSoup(browser.page_source, features = 'html5lib')
    table = soup.find_all('tbody', {'id':'transTbody'})
    headers = soup.find_all('thead', {'class':'classictblhdr'})

    header_row = headers[0].find_all('tr')
    table_rows = table[0].find_all('tr')

    l = []
    for tr in table_rows:
        td = tr.find_all('td')
        row = [tr.text for tr in td]
        l.append(row)
    
    h = []
    for tr in header_row:
        th = tr.find_all('th')
        header = [tr.text for tr in th]
        h.append(header)
    
    data = pd.DataFrame(l, columns = h[0])
    return(data)

def process_data(data, date):
    """converts raw data to clean data
    
    keyword arguments:
    data (pandas dataframe) - dataframe read directly from table
    
    returns:
    data (pandas dataframe) - dataframe with final columns & types
    """
    
    data['Usage (kWh)'] = pd.to_numeric(data['Usage (kWh)'])
    data['Cost ($)'] = pd.to_numeric(data['Cost ($)'])
    data['Hi'] = [int(a.split(' / ')[0]) for a in list(data['Temp (hi / low)'])]
    data['Low'] = [int(a.split(' / ')[1]) for a in list(data['Temp (hi / low)'])]
    data.drop(['Temp (hi / low)'], axis = 1, inplace = True)

    new_hour = []
    for hour in list(data.Hour):
        new = []
        for char in hour:
            try:
                new.append(str(int(char)))
        
            except:
                pass
    
        new = ''.join(new)

        if ('pm' in hour) and (int(new) < 12):
            new = int(new) + 12
            new = str(new)
    
        if ('am' in hour) and (int(new) == 12):
            new = int(new) - 12
            new = str(new)

        new = date + ' ' + new
        new_hour.append(new)
    
    data['Date'] = [datetime.strptime(h, "%B %d, %Y %H") for h in new_hour]
    data.drop(['Hour'], axis = 1, inplace = True)
    data.set_index(['Date'], inplace = True)
    return(data)

def get_daily_use(browser):
    """
    iterate thru tables and get daily usage.
    
    keyword arguments:
    browser (selenium.WebDriver) - browser object on account page
    
    returns:
    data (pandas dataframe) - cleaned dataframe of hourly use
    dt (datetime) - datetime of usage day
    vars (selenium.WebElement) - web element of chart header
    """
    
    views = browser.find_element_by_xpath("//div[@id='selectusgviewdiv']")
    views.find_element_by_id('daybtnid').click() #click to daily data
    time.sleep(2)

    vars = browser.find_element_by_xpath("//div[@id='costandusagedivareaid']")
    date = vars.find_element_by_id('messgaetxt').text #get date
    dt = datetime.strptime(date, '%B %d, %Y')

    browser.find_element_by_xpath("//li[@id='tabletid']").click() #click to table view
    time.sleep(3)
    
    data = table_to_df(browser)
    data = process_data(data, date)
    
    total_use = round(np.sum(data['Usage (kWh)']), 2)
    total_cost = np.sum(data['Cost ($)'])
    print('{} had usage of {} kWh and cost ${}.'.format(date, total_use, total_cost))
    
    return(data, dt, vars)

if __name__ == "__main__":


    with open('config.yaml', 'r') as f:
        config = yaml.load(f, Loader = yaml.FullLoader)

    #logon to site
    output = logon(config['headless'], config['download'], config['site'], config['creds'])
    print('logged on successfully.')
    time.sleep(10)

    #scrape basic info
    amt, name, acct, address = acct_info(output)

    print('current bill is ${}.'.format(amt))
    print('service for {}, account {} at {}.'.format(name, acct, address))

    #select account option from menu
    want_to = output.find_element_by_xpath("//select[@id='wantTo']")
    options = [x for x in want_to.find_elements_by_tag_name('option')]
    options_text = [x.text for x in want_to.find_elements_by_tag_name('option')]

    Select(want_to).select_by_visible_text('View usage history')
    time.sleep(5)

    #make dataframe of daily use
    master = pd.DataFrame()

    data, date, var = get_daily_use(output)
    start_date = date

    try:
        var.find_element_by_id('nextid').click() #click to next day
        time.sleep(2)

    except:
        print('out of days.')

    while start_date < datetime.today():
    
        time.sleep(5)
        data, date, var = get_daily_use(output)
        start_date += timedelta(days = 1)
    
        if data.shape[0] > 0:
            master = pd.concat([master, data], axis = 0)
    
        try:
            var.find_element_by_id('nextid').click() #click to next day
            time.sleep(2)

        except:
            print('out of days.')

    #write to .csv
    base = os.getcwd()
    date_string = datetime.strftime(datetime.today(), format = '%m%d%Y')
    fname = 'daily_usage_' + date_string + '.csv'
    filepath = os.path.join(base, 'data', fname)
    master.to_csv(filepath)
    print('wrote daily usage to .csv')

    #plot
    #master.plot(y = 'Usage (kWh)')
    #plt.show()
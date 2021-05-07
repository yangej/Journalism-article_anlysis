#coding=utf-8

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import csv
import time

## set browser
options = Options()
options.add_argument("--disable-notifications")
chrome = webdriver.Chrome('../chromedriver', chrome_options=options)
chrome.implicitly_wait(5)

## open browser
chrome.get('http://www.rmbnewsbank.com/applec/appletp')

def writeTuplesToFile(year, tuples):
    dirPath = os.path.abspath(os.getcwd()) + '/records'
    file = year + 'tuples.csv'
    path = os.path.join(dirPath, file)

    fileExist = False
    if (os.path.exists(path)):
        fileExist = True

    with open(path, 'a', encoding = 'utf-8', newline = '') as outfile:
        writer = csv.writer(outfile)

        if (fileExist == False):
            fieldNames = ['publish_date', 'title', 'content', 'press']
            writer.writerow(fieldNames)

        for tuple in tuples:
            writer.writerow(tuple)

def scrape(keyword, durations):
    for duration in durations:
        ## select html elements
        time.sleep(5)
        inputEls = chrome.find_elements_by_class_name('form-control')
        keywordInputEl = inputEls[0]
        fromInputEl = inputEls[1]
        toInputEl = inputEls[2]
        searchBtn = chrome.find_element_by_class_name('search')

        keywordInputEl.send_keys(keyword)
        fromInputEl.send_keys(duration[0])
        toInputEl.send_keys(duration[1])
        searchBtn.click()

        time.sleep(1)
        resultPage = chrome.current_url

        # get links
        soup = BeautifulSoup(chrome.page_source, 'html.parser')
        resultEls = chrome.find_elements_by_class_name('sum_th')
        tuples = []

        for i in range(len(resultEls)):
            print('current article index: ', i)
            time.sleep(1)
            chrome.find_elements_by_class_name('sum_th')[i].click()
            time.sleep(2)
            soup = BeautifulSoup(chrome.page_source, 'html.parser')

            try:
                PRESS = '蘋果日報'

                tdEls = soup.findAll('td')
                title = tdEls[0].text.strip()
                publish_date = tdEls[1].text.strip()
                content = tdEls[3].text.strip().replace('\n', '').replace(u'\u3000', u'')

                tuple = (publish_date, title, content, PRESS)
                print(tuple)
                tuples.append(tuple)

            except Exception as ex:
                print('skip!')
                print(ex)
                chrome.get(resultPage)
                continue

            time.sleep(2)
            chrome.get(resultPage)
        writeTuplesToFile(duration[2], tuples)

    try:
        nextPageBtn = chrome.find_element_by_class_name('glyphicon-triangle-right')
        nextPageBtn.click()
    except:
        print("no more pages!")

KEYWORD = u'奧斯卡 NOT ("英國奧斯卡" OR "日本奧斯卡")'
durations = [('20170227', '20170305', '2017'), ('20180305', '20180311', '2018'), ('20190225', '20190307', '2019'), ('20200210', '20200216', '2020'), ('20210426', '20210502', '2021')]
scrape(KEYWORD, durations)
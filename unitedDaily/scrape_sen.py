#coding=utf-8

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import csv
import time
import random
import requests

## set browser
options = Options()
options.add_argument("--disable-notifications")
chrome = webdriver.Chrome('../chromedriver', chrome_options=options)
chrome.implicitly_wait(10)

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

def getDetailTuples(year, listUrl):
    tuples = []
    scrollOffset = 50
    resultEls = chrome.find_elements_by_class_name('control-pic')
    print('current year is: ', year)

    for i in range(len(resultEls) - 1):
        print('current article index: ', i)
        time.sleep(random.random()*10)
        chrome.execute_script(f"window.scroll(0, {scrollOffset})")
        time.sleep(1)
        chrome.execute_script(f"document.querySelectorAll('.control-pic > a')[{i}].click()")

        # authentication check
        try:
            chrome.execute_script(f"document.querySelectorAll('.button-a-color')[0].click()")

        except Exception as ex:
            pass

        time.sleep(2)
        soup = BeautifulSoup(chrome.page_source, 'html.parser')

        # get tuple
        try:
            time.sleep(2)
            PRESS = '聯合報'
            title = soup.find('h1').text.strip()
            publish_date = soup.find(class_='story-source').text[1:11].strip()
            content = soup.find('article').text.strip().replace('\n', '').replace('\t', '').replace(u'\u3000', u'')

            tuple = (publish_date, title, content, PRESS)
            print(tuple)
            tuples.append(tuple)

        except Exception as ex:
            print('skip!')
            print(ex)
            continue

        chrome.get(url)
        scrollOffset += 100

    writeTuplesToFile(year, tuples)

yearLinks = [
    { 'year': "2012", 'from': "20120226", 'to': "20120304" },
    { 'year': "2013", 'from': "20130224", 'to': '20130302' },
    { 'year': "2014", 'from': "20140302", 'to': "20140308" },
    { 'year': "2015", 'from': "20150222", 'to': "20150228" },
    { 'year': "2016", 'from': "20160228", 'to': "20160305" },
    { 'year': "2017", 'from': "20170227", 'to': "20170305" },
    { 'year': "2018", 'from': "20180305", 'to': '20180312' },
    { 'year': "2019", 'from': "20190225", 'to': "20190307" },
    { 'year': "2020", 'from': "20200210", 'to': "20200216" },
    { 'year': "2021", 'from': "20210426", 'to': "20210502" }
]

for link in yearLinks:
    # page num is hard coded!
    url = f'https://udndata.com/ndapp/Searchdec?udndbid=udnfree&page=3&SearchString=%B6%F8%B4%B5%A5%64%2B%A4%E9%B4%C1%3E%3D{link["from"]}%2B%A4%E9%B4%C1%3C%3D{link["to"]}%2B%B3%F8%A7%4F%3D%C1%70%A6%58%B3%F8&sharepage=20&select=1&kind=2'
    chrome.get(url)
    getDetailTuples(link['year'], url)
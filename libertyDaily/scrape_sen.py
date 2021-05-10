#coding=utf-8

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import csv
import time
import requests

## set browser
options = Options()
options.add_argument("--disable-notifications")
chrome = webdriver.Chrome('../chromedriver', chrome_options=options)

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

def getDetailTuples(year):
    tuples = []
    resultEls = chrome.find_elements_by_class_name('tit')
    for i in range(len(resultEls) - 1):
        print('current article index: ', i)
        time.sleep(1)
        resultEls = chrome.find_elements_by_class_name('tit')
        time.sleep(2)
        titleEl = resultEls[i]
        titleEl.click()
        time.sleep(2)
        soup = BeautifulSoup(chrome.page_source, 'html.parser')

        try:
            PRESS = '自由時報'
            title = soup.find('h1').text.strip()
            publish_date = soup.find(class_='time').text[0:11].strip()
            content = soup.find(class_='text').text.strip().replace('\n', '').replace(u'\u3000', u'')

            tuple = (publish_date, title, content, PRESS)
            tuples.append(tuple)

        except Exception as ex:
            print('skip!')
            continue

        chrome.back()
    writeTuplesToFile(year, tuples)

    try:
        nextBtn = chrome.find_element_by_class_name('p_next')
        nextBtn.click()
        time.sleep(1)
        getDetailTuples(year)
    except Exception as ex:
        print(ex)
        print('no more pages!')

yearLinks = [
    { 'year': "2017", 'url': "https://search.ltn.com.tw/list?keyword=%E5%A5%A7%E6%96%AF%E5%8D%A1&start_time=20170227&end_time=20170305&sort=date&type=all&type=entertainment&page=1" },
    { 'year': "2018", 'url': "https://search.ltn.com.tw/list?keyword=%E5%A5%A7%E6%96%AF%E5%8D%A1&start_time=20180305&end_time=20180312&sort=date&type=all&type=entertainment&page=1" },
    { 'year': "2019", 'url': "https://search.ltn.com.tw/list?keyword=%E5%A5%A7%E6%96%AF%E5%8D%A1&start_time=20190225&end_time=20190307&sort=date&type=all&type=entertainment&page=1" },
    { 'year': "2020", 'url': "https://search.ltn.com.tw/list?keyword=%E5%A5%A7%E6%96%AF%E5%8D%A1&start_time=20200210&end_time=20200216&sort=date&type=all&type=entertainment&page=1" },
    { 'year': "2021", 'url': "https://search.ltn.com.tw/list?keyword=%E5%A5%A7%E6%96%AF%E5%8D%A1&start_time=20210426&end_time=20210502&sort=date&type=all&type=entertainment&page=1" }
    { 'year': "2012", 'url': "https://search.ltn.com.tw/list?keyword=%E5%A5%A7%E6%96%AF%E5%8D%A1&start_time=20120226&end_time=20120304&sort=date&type=all&type=entertainment&page=1" },
    { 'year': "2013", 'url': "https://search.ltn.com.tw/list?keyword=%E5%A5%A7%E6%96%AF%E5%8D%A1&start_time=20130224&end_time=20130302&sort=date&type=all&type=entertainment&page=1" },
    { 'year': "2014", 'url': "https://search.ltn.com.tw/list?keyword=%E5%A5%A7%E6%96%AF%E5%8D%A1&start_time=20140302&end_time=20140308&sort=date&type=all&type=entertainment&page=1" },
    { 'year': "2015", 'url': "https://search.ltn.com.tw/list?keyword=%E5%A5%A7%E6%96%AF%E5%8D%A1&start_time=20150222&end_time=20150228&sort=date&type=all&type=entertainment&page=1" },
    { 'year': "2016", 'url': "https://search.ltn.com.tw/list?keyword=%E5%A5%A7%E6%96%AF%E5%8D%A1&start_time=20160228&end_time=20160305&sort=date&type=all&type=entertainment&page=1" }
]

for link in yearLinks:
    chrome.get(link['url'])
    getDetailTuples(link['year'])
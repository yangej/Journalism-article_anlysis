#coding=utf-8

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import os
import re
import csv
import time
import random
import requests
import urllib3

## set browser
options = Options()
options.add_argument("--disable-notifications")
chrome = webdriver.Chrome('../chromedriver', chrome_options=options)
chrome.implicitly_wait(5)
actions = ActionChains(chrome)

regex = r'Playvolume.*{ display:none; } }'

def writeTuplesToFile(name, tuples):
    dirPath = os.path.abspath(os.getcwd()) + '/other_records'
    file = name + 'result.csv'
    path = os.path.join(dirPath, file)

    fileExist = False
    if (os.path.exists(path)):
        fileExist = True

    with open(path, 'a', encoding = 'utf-8', newline = '') as outfile:
        writer = csv.writer(outfile)

        if (fileExist == False):
            fieldNames = ['人選', '日期', '分類', '標題', '內容']
            writer.writerow(fieldNames)

        for tuple in tuples:
            writer.writerow(tuple)

def scrollToTarget(index):
    scrollTime = 1
    itemNumber = 20
    for i in range(int(index / itemNumber)):
        chrome.execute_script(f"window.scroll(0, document.body.scrollHeight)")
        time.sleep(5)

def rollback(tuples, index, link):
    chrome.get(link)
    scrollToTarget(index)
    getArticleTuple(tuples, index, link)

def getArticleTuple(tuples, index, link):
    print('current article index: ', index)
    time.sleep(random.random()*10)

    window = chrome.window_handles[0]
    chrome.switch_to.window(window_name=window)


    itemNumber = 20
    if (index % itemNumber == 0):
        chrome.execute_script(f"window.scroll(0, document.body.scrollHeight)")

    try:
        chrome.execute_script(f"window.open(document.querySelectorAll('.story-card')[{index}].getAttribute('href'), '_blank')")
    except Exception as ex:
        print(ex)
        rollback(tuples, index, link)

    window = chrome.window_handles[1]
    chrome.switch_to.window(window_name=window)
    time.sleep(2)

    soup = BeautifulSoup(chrome.page_source, 'html.parser')
    try:
        title = soup.find('h1').text.strip()
        content = soup.findAll('section')[3].text.strip().replace('\n', '').replace('\t', '').replace(u'\u3000', u'')
        content = re.sub(regex, '', content)
        print(content)
        parsedUrl = chrome.current_url.replace('https://tw.appledaily.com/', '').split('/')
        type = parsedUrl[0]
        publish_date = parsedUrl[1]

        if publish_date[0:4] == '2016':
            writeTuplesToFile(name, tuples)
            return True

        else:
            print(chrome.current_url)
            tuples.append((name, publish_date, type, title, content))
            print(name, '|', publish_date, ':', title)
            chrome.close()

    except Exception as ex:
        print('skip!')
        print(ex)
        chrome.close()

    if (index % 10 == 0):
        writeTuplesToFile(name, tuples)
        tuples = []

    index += 1

    getArticleTuple(tuples, index, link)


def getDetailTuples(name, link):
    tuples = []
    scrollOffset = 300
    articleIndex = 20
    print('---- current person is: ', name)

    tuple = getArticleTuple(tuples, articleIndex, link)

linksInfos = [
    ('徐巧芯', 'https://tw.appledaily.com/search/%E5%BE%90%E5%B7%A7%E8%8A%AF/'),
    ('賴品妤', 'https://tw.appledaily.com/search/%E8%B3%B4%E5%93%81%E5%A6%A4/'),
    ('高嘉瑜', 'https://tw.appledaily.com/search/%20%E9%AB%98%E5%98%89%E7%91%9C/'),
    ('黃捷', 'https://tw.appledaily.com/search/%E9%BB%83%E6%8D%B7/')
]

# this is apple daily
for info in linksInfos:
    name = info[0]
    link = info[1]

    chrome.get(link)
    getDetailTuples(name, link)
    chrome.quit()
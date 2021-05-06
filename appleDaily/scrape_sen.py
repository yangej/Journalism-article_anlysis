#coding=utf-8

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests

## set browser
options = Options()
options.add_argument("--disable-notifications")

chrome = webdriver.Chrome('../chromedriver', chrome_options=options)

## open browser
chrome.get('http://www.rmbnewsbank.com/applec/appletp?@@0.8725746023111722#JUMPOINT')

## select html elements
inputEls = chrome.find_elements_by_class_name('form-control')
keywordInputEl = inputEls[0]
fromInputEl = inputEls[1]
toInputEl = inputEls[2]
searchBtn = chrome.find_element_by_class_name('search')

## manipulate search behavior
# set input values
KEYWORD = u'奧斯卡 NOT ("英國奧斯卡" OR "日本奧斯卡")'
# durations = [('20170227', '20170305'), ('20180305', '20180311'), ('20190225', '20190307'), ('20200210', '20200216'), ('20210426', '20210502')]
duration = ('20170227', '20170305')

keywordInputEl.send_keys(KEYWORD)
fromInputEl.send_keys(duration[0])
toInputEl.send_keys(duration[1])
searchBtn.click()

time.sleep(3)

# get links
soup = BeautifulSoup(chrome.page_source, 'html.parser')
tuples = []
resultEls = chrome.find_elements_by_class_name('godetail')

for i in range(len(resultEls) - 1):
    print('current article index: ', i)
    time.sleep(5)
    resultEls = chrome.find_elements_by_class_name('godetail')
    time.sleep(2)
    titleEl = resultEls[i]
    print(resultEls[i])
    #FIXME: NoneType Object
    titleEl.click()
    time.sleep(2)
    break
    soup = BeautifulSoup(chrome.page_source, 'html.parser')

#     try:
#         PRESS = '蘋果日報'
#         title = soup.find(class_='edi_title').text.strip()
#
#         tdEls = soup.findAll('td')
#         publish_date = tdEls[1].strip()
#         content = tdEls[3].text.strip().replace('\n', '').replace(u'\u3000', u'')
#
#         tuple = (publish_date, title, content, PRESS)
#         print(tuple)
#         break
# #         tuples.append(tuple)
#
#     except Exception as ex:
#         print('skip!')
#         print(ex)
#         continue

    chrome.back()

# try:
#     nextPageBtn = chrome.find_element_by_class_name('glyphicon-triangle-right')
#     nextPageBtn.click()
# except:
#     print("no more pages!")

## get detail tuples for db
# def getDetailTuples(links):
#     baseUrl = 'http://www.rmbnewsbank.com/'
#     tuples = []
#
#     for link in links:
#         response = requests.get(baseUrl + link)
#         response.encoding = 'utf-8'
#         soup = BeautifulSoup(response.text, 'html.parser')
#
#         tdEls = soup.findAll("td")
#         title = tdEls[0].text.strip().replace(u'\u3000', u'')
#         publish_date = tdEls[1].text
#         content = tdEls[2].text
#         PRESS = '蘋果日報'
#         tuple = (title, publish_date, content, PRESS)
#
#         tuples.append(tuple)
#
#     return tuples

## construct news article class
# class NewsArticle:
#     def __init__(self, keyword, duration):
#         self.keyword = keyword
#         self.duration = duration
#
#     def scrape(self):
#         result = list()
#
#
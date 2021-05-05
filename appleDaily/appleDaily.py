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
chrome.get("https://www.facebook.com/")

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
detailATag = soup.findAll('a', { 'class': 'godetail' })
detailLinks = [a.get('href') for a in detailATag]

#FIXME test whether can find next page btn
try:
    nextPageBtn = chrome.find_element_by_class_name('pagination')
    print("pagination found!")
except:
    print("no next page!")

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
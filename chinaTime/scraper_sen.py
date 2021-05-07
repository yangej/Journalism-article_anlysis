#coding=utf-8

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import os
import csv
import time
import requests

## set browser
options = Options()
options.add_argument("--disable-notifications")
chrome = webdriver.Chrome('../chromedriver', chrome_options=options)
chrome.implicitly_wait(5)

# common constants
REGEX_FOR_TABLE = r'<table[.\s\S]+<\/table>'
REGEX_FOR_STYLE = r'<style[.\s\S]+<\/style>'
REGEX_FOR_ARTICLE = r'</?\barticle\b.*?>'
regexs = [REGEX_FOR_TABLE, REGEX_FOR_STYLE, REGEX_FOR_ARTICLE]
KEYWORD = '奧斯卡'

def writeTuplesToFile(year, tuples):
    print('write into csv!!')
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

def getDetailTuples(year, start, end):
    tuples = []
    resultEls = chrome.find_elements_by_class_name('NewsContetn')
    for i in range(len(resultEls)):
        print('current article index: ', i)
        time.sleep(1)
        resultEls = chrome.find_elements_by_class_name('NewsContetn')
        titleEl = resultEls[i]
        articleUrl = titleEl.get_attribute('href')
        chrome.get(articleUrl)
        time.sleep(2)

        soup = BeautifulSoup(chrome.page_source, 'html.parser')

        try:
            PRESS = '中國時報'
            title = soup.find('h1').text.strip()
            publish_date = soup.find(id='ctl00_ContentPlaceHolder1_UCNewsContent1_lbldateAuth').text[0:10].strip()
            content = str(soup.findAll('article')[1])

            # remove unnecessary part in content
            for reg in regexs:
                regex = re.compile(reg)
                content = re.sub(regex, '', content)
            content = content.replace('\n', '').replace('\t', '').replace(u'\u3000', u'').replace('<br/>', '')

            tuple = (publish_date, title, content, PRESS)
            tuples.append(tuple)

        except Exception as ex:
            print(ex)
            print('skip!')
            continue

        chrome.back()
    writeTuplesToFile(year, tuples)

    nextBtn = chrome.find_element_by_id('ctl00_ContentPlaceHolder1_UCPage1_lbtnPageNext')
    if(len(nextBtn.get_attribute('class')) >= 2):
        print('no more pages!')
    else:
        nextBtn.click()
        time.sleep(1)
        getDetailTuples(year, start, end)


yearLinks = [
    { 'year': "2021", 'start': { 'month': "4", 'date': "26" }, 'end': { 'month': "5", 'date': "2" } }
    { 'year': "2020", 'start': { 'month': "2", 'date': "11" }, 'end': { 'month': "2", 'date': "16" } }
    { 'year': "2019", 'start': { 'month': "2", 'date': "26" }, 'end': { 'month': "3", 'date': "7" } }
    { 'year': "2018", 'start': { 'month': "3", 'date': "5" }, 'end': { 'month': "3", 'date': "11" } }
    { 'year': "2017", 'start': { 'month': "2", 'date': "27" }, 'end': { 'month': "3", 'date': "5" } }
]

url = 'http://kmw.chinatimes.com/News/NewsSearch.aspx?searchkind=s'
chrome.get(url)
chrome.find_element_by_id('lbInfotimesLogin').click()

for link in yearLinks:
    print('current link is: ', link)

    year = link['year']
    start = link['start']
    end = link['end']

    # set duration and search
    keywordInputEl = chrome.find_element_by_id('txtKeyword')
    inputEls = chrome.find_elements_by_class_name('temp-calendar')
    startInputEl = inputEls[0]
    endInputEl = inputEls[1]
    searchBtn = chrome.find_element_by_name('ctl00$ContentPlaceHolder1$btnSearch')

    time.sleep(1)
    keywordInputEl.click()
    keywordInputEl.clear()
    keywordInputEl.send_keys(KEYWORD)

    chrome.find_element_by_xpath("//label[contains(text(), '工商')]").click()
    chrome.find_element_by_xpath("//label[contains(text(), '旺報')]").click()

    try:
        endInputEl.click()
        time.sleep(1)
        chrome.find_element_by_id('selCalendar_y').click()
        time.sleep(1)
        chrome.find_element_by_xpath(f"//option[@value='{year}']").click()
        time.sleep(1)
        chrome.find_element_by_id('selCalendar_m').click()
        time.sleep(1)
        chrome.find_element_by_xpath(f"//option[@value='{end['month']}']").click()
        time.sleep(1)
        endDateEl = chrome.find_element_by_xpath("//td[contains(text(), '" + end['date'] + "')]")
        time.sleep(1)
        chrome.execute_script("arguments[0].click();", endDateEl)
    except Exception as ex:
        print(ex)

    try:
        startInputEl.click()
        time.sleep(1)
        chrome.find_element_by_id('selCalendar_y').click()
        time.sleep(1)
        chrome.find_element_by_xpath(f"//option[@value='{year}']").click()
        time.sleep(1)
        chrome.find_element_by_id('selCalendar_m').click()
        time.sleep(1)
        chrome.find_element_by_xpath(f"//option[@value='{start['month']}']").click()
        time.sleep(1)
        startDateEl = chrome.find_element_by_xpath("//td[contains(text(), '" + start['date'] + "')]")
        time.sleep(1)
        chrome.execute_script("arguments[0].click();", startDateEl)
    except Exception as ex:
        print(ex)

    searchBtn.click()

    getDetailTuples(year, start, end)
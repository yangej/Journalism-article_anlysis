#coding=utf-8

from bs4 import BeautifulSoup
import time
import requests
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def getTotalPage(soup, articlePerPage):
    print(soup.find(class_="mark"))
    totalArticleNum = int(soup.find(class_="mark").text.split(" ")[1])
    totalPage = 0

    if totalArticleNum % articlePerPage != 0:
        totalPage = totalArticleNum / articlePerPage + 1
    else:
        totalPage = totalArticleNum / articlePerPage

    return int(totalPage)

def getPageHtml(keyword, dateFrom, dateTo, currentPage):
    url = 'https://search.ltn.com.tw/list?keyword=%(keyword)s&start_time=%(start)s&end_time=%(end)s&sort=date&type=all&page=%(page)s' % { "keyword": keyword, "start": dateFrom, "end": dateTo, "page": currentPage }
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

def writeLinksToFile(links):
    dirPath = os.path.abspath(os.getcwd()) + '/records'
    file = 'links.csv'
    path = os.path.join(dirPath, file)

    with open(path, 'w', encoding = 'utf-8', newline = '') as outfile:
        fieldNames = ['links']
        writer = csv.writer(outfile)
        writer.writerow(fieldNames)

        for link in links:
            writer.writerow(link)

def getLinks(keyword, durations):
    print("getting links from search page")
    links = []
    durationCount = 1
    for duration in durations:
        print('duration process: ', durationCount, '', len(durations))
        time.sleep(3)

        dateFrom = duration[0]
        dateTo = duration[1]
        currentPage = 1

        soup = getPageHtml(keyword, dateFrom, dateTo, currentPage)
        articlePerPage = 20
        totalPage = getTotalPage(soup, articlePerPage)

        while(currentPage <= totalPage):
            if (currentPage != 1):
                soup = getPageHtml(keyword, dateFrom, dateTo, currentPage)

            aTags = soup.findAll(class_='tit')
            for aTag in aTags:
                links.append(aTag.get('href'))

            currentPage += 1

        durationCount += 1

    writeLinksToFile(links)
    return links

def writeTuplesToFile(tuples):
    dirPath = os.path.abspath(os.getcwd()) + '/records'
    file = 'tuples.csv'
    path = os.path.join(dirPath, file)

    with open(path, 'w', encoding = 'utf-8', newline = '') as outfile:
        fieldNames = ['publish_date', 'title', 'content', 'press']
        writer = csv.writer(outfile)
        writer.writerow(fieldNames)

        for tuple in tuples:
            writer.writerow(tuple)

def getDetailTuples(links):
    print("getting details from each link")
    linkCount = 1
    tuples = []
    for link in links:
        print('link process: ', linkCount, '/', len(links))
        print('current link is: ', link)
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            PRESS = '自由時報'
            title = soup.find('h1').text.strip()
            publish_date = soup.find(class_='time').text[0:11].strip()
            content = soup.find(class_='text').text.strip().replace('\n', '').replace(u'\u3000', u'')

            tuple = (publish_date, title, content, PRESS)
            tuples.append(tuple)

            linkCount += 1
        except Exception as ex:
            print('exception happened in getDetailTuples, link is: ', link)
            continue

    writeTuplesToFile(tuples)
    return tuples

def saveToDB(tuples):
    print("saving into database!")
    db_settings = {
        "host": os.getenv('HOST'),
        "port": os.getenv('PORT'),
        "user": os.getenv('USER'),
        "password": os.getenv('DB_PASSWORD'),
        "db": os.getenv('DB'),
        "charset": os.getenv('CHARSET')
    }

    try:
        conn = pymysql.connect(**db_settings)

        with conn.cursor() as cursor:
            sql = """
                INSERT INTO news_articles(
                        publish_date,
                        title,
                        content,
                        press
                    )
                VALUES(%s, %s, %s, %s)
            """

        for tuple in tuples:
            cursor.execute(sql, tuple)

        conn.commit()

    except Exception as ex:
        print("Exception:", ex)

def scrape():
    durations = [('20170227', '20170305'), ('20180305', '20180311'), ('20190225', '20190307'), ('20200210', '20200216'), ('20210426', '20210502')]
    links = getLinks('奧斯卡', durations)
    tuples = getDetailTuples(links)
    saveToDB(tuples)
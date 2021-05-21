#coding=utf-8

from sklearn.feature_extraction.text import CountVectorizer
from gensim import corpora, models, similarities
import gensim
import jieba
import jieba.analyse
import re
import os
import csv
import pandas as pd
from itertools import chain

## get stop words
common_words = ['奧斯卡', '電影', '片中', '最佳', '今年', '頒獎']
with open('stop_word.txt') as f:
    stop_words = [line.strip() for line in f.readlines()]
f.close()

with open('stop_word_manual.txt') as f:
     [stop_words.append(line.strip()) for line in f.readlines()]
 f.close()

removed_words = common_words + stop_words

## get dataset
initial_data_tuples = []
data_tuples = []
with open('clean_data.csv') as f:
    title_and_content = ''
    for line in f.readlines():
        str_arr = line.split(',')
        title = str_arr[3]
        content = str_arr[4]
        publisher = str_arr[5]
        title_and_content = title + content
        data_tuples.append((str_arr[0], title_and_content, publisher))
        initial_data_tuples.append((str_arr[0], title, content))
f.close()

## group dataset by year and split into eng & chi two parts
years = []
group_by_year = {}
eng_regex = r'([A-Z]+[a-z]*)'
for tuple in data_tuples:
    year = tuple[0]
    title_and_content = tuple[1]
    words = ''.join([word for word in jieba.lcut(title_and_content.replace(" ", "")) if word not in removed_words])
    # ^ remove stop words

    if group_by_year.get(year) == None:
        years.append(year)
        group_by_year[year] = [words]
    else:
        group_by_year[year].append(words)

group_by_year_titles = {}
for tuple in initial_data_tuples:
    year = tuple[0]
    title = tuple[1]

    if group_by_year_titles.get(year) == None:
        group_by_year_titles[year] = [title]
    else:
        group_by_year_titles[year].append(title)

year_lda = []
year_clusters = []
num_topics = [5, 6, 7, 8, 9, 10]
for year in years:
    current_year_docs = group_by_year[year]
    dictionary = corpora.Dictionary([jieba.lcut(doc) for doc in current_year_docs])
    corpus = [dictionary.doc2bow(jieba.lcut(doc)) for doc in current_year_docs]

    for num in num_topics:
        lda = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=num)
        dirPath = os.path.abspath(os.getcwd()) + f'/results/{year}_results/{year}_{num}_cluster_results'
        try:
            os.makedirs(dirPath)
        except Exception as ex:
            print('directory exists')

        topFile = f'{year}_{num}_cluster.csv'
        topPath = os.path.join(dirPath, topFile)
        topFileExist = False
        if (os.path.exists(topPath)):
            topFileExist = True
        with open(topPath, 'w', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            if (topFileExist == False):
                fieldNames = ['topic', 'keywords']
                writer.writerow(fieldNames)

            for topic in lda.print_topics(num_topics=num, num_words=10):
                writer.writerow(topic)

        docFile = f'{year}_{num}_cluster_document.csv'
        docPath = os.path.join(dirPath, docFile)
        docFileExist = False
        if (os.path.exists(docPath)):
            docFileExist = True
        with open(docPath, 'w', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            if (docFileExist == False):
                fieldNames = ['topic', 'probability',  'title']
                writer.writerow(fieldNames)

            for i in range(len(group_by_year_titles[year])):
                topic_pro = lda.get_document_topics(corpus[i])
                tuple = (topic_pro, group_by_year_titles[year][i])
                writer.writerow(tuple)

    f.close()

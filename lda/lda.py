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
dataset_name = 'test_articles.csv'
initial_data_tuples = []
data_tuples = []
with open(dataset_name) as f:
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

    eng_words = re.findall(eng_regex, title_and_content)
    chi_words = [word for word in jieba.lcut(re.sub(eng_regex, '', title_and_content.replace(" ", ""))) if word not in removed_words]
    # ^ remove stop words

    if group_by_year.get(year) == None:
        years.append(year)
        group_by_year[year] = [{ 'eng_words': eng_words, 'chi_words': chi_words }]
    else:
        group_by_year[year].append({ 'eng_words': eng_words, 'chi_words': chi_words })

## get yearly titles
group_by_year_titles = {}
for tuple in initial_data_tuples:
    year = tuple[0]
    title = tuple[1]

    if group_by_year_titles.get(year) == None:
        group_by_year_titles[year] = [title]
    else:
        group_by_year_titles[year].append(title)

class OutputFile:
    def __init__(self, doc_tuples, topic_year, topics, topic_num):
        self.doc_tuples = doc_tuples
        self.topic_year = topic_year
        self.topics = topics
        self.topic_num = topic_num

        dir_path = ''
        if (dataset_name == 'test_articles.csv'):
            dir_path = os.path.abspath(os.getcwd()) + f'/test_results/{self.topic_year}_results/{self.topic_year}_{self.topic_num}_cluster_results'
        else:
            dir_path = os.path.abspath(os.getcwd()) + f'/results/{self.topic_year}_results/{self.topic_year}_{self.topic_num}_cluster_results'
        self.__dir_path = dir_path

    def creat_topic_file(self):
        top_file = f'{self.topic_year}_{self.topic_num}_cluster.csv'
        top_path = os.path.join(self.__dir_path, top_file)
        top_file_exist = False

        if (os.path.exists(top_path)):
            top_file_exist = True

        with open(top_path, 'w', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            if (top_file_exist == False):
                field_names = ['topic', 'keywords']
                writer.writerow(field_names)

            for topic in self.topics:
                writer.writerow(topic)
        outfile.close()

    def create_topic_doc_file(self):
        doc_file = f'{self.topic_year}_{self.topic_num}_cluster_document.csv'
        doc_path = os.path.join(self.__dir_path, doc_file)
        doc_file_exist = False

        if (os.path.exists(doc_path)):
            doc_file_exist = True

        with open(doc_path, 'w', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            if (doc_file_exist == False):
                field_names = ['topic', 'probability',  'title']
                writer.writerow(field_names)

            for tuple in self.doc_tuples:
                writer.writerow(tuple)
        outfile.close()

    def create_topic_and_doc_files(self):
        try:
            os.makedirs(self.__dir_path)
        except Exception as ex:
            print('directory exists')

        self.creat_topic_file()
        self.create_topic_doc_file()

year_lda = []
year_clusters = []
num_topics = [5, 6, 7, 8, 9, 10]
for year in years:
    current_year_docs = group_by_year[year]

    ## gather all words
    word_list = []
    for obj in current_year_docs:
        title_and_content = obj['eng_words'] + obj['chi_words']
        word_list.append(title_and_content)

    ## create training dictionary and bag of words
    dictionary = corpora.Dictionary(word_list)
    corpus = [dictionary.doc2bow(word) for word in word_list]

    ## create different number of topics
    for num in num_topics:
        lda = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=num)
        topics = lda.print_topics(num_topics=num, num_words=10)
        titles = group_by_year_titles[year]

        doc_tuples = []
        for i in range(len(titles)):
            topic_pro = lda.get_document_topics(corpus[i])
            tuple = (topic_pro, group_by_year_titles[year][i])
            doc_tuples.append(tuple)

        output = OutputFile(doc_tuples, year, topics, num)
        output.create_topic_and_doc_files()

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
dataset_name = 'clean_data.csv'
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
    def __init__(self, doc_tuples, top_tuples, topic_year, topics, topic_num):
        self.doc_tuples = doc_tuples
        self.top_tuples = top_tuples
        self.topic_year = topic_year
        self.topics = topics
        self.topic_num = topic_num

        dir_path = ''
        if (dataset_name == 'test_articles.csv'):
            dir_path = os.path.abspath(os.getcwd()) + f'/test_results/{self.topic_year}_results/{self.topic_year}_{self.topic_num}_cluster_results'
        else:
            dir_path = os.path.abspath(os.getcwd()) + f'/results/{self.topic_year}_results/{self.topic_year}_{self.topic_num}_cluster_results'
        self.__dir_path = dir_path

    def create_doc_topic_file(self):
        doc_file = f'{self.topic_year}_{self.topic_num}_by_document.csv'
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

    def create_topic_doc_file(self):
        doc_file = f'{self.topic_year}_{self.topic_num}_by_cluster.csv'
        doc_path = os.path.join(self.__dir_path, doc_file)
        doc_file_exist = False

        if (os.path.exists(doc_path)):
            doc_file_exist = True

        with open(doc_path, 'w', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            if (doc_file_exist == False):
                field_names = ['topic', 'keywords', 'title']
                writer.writerow(field_names)

            for tuple in self.top_tuples:
                writer.writerow(tuple)
        outfile.close()

    def create_files(self):
        try:
            os.makedirs(self.__dir_path)
        except Exception as ex:
            print('directory exists')

        self.create_topic_doc_file()
        self.create_doc_topic_file()

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
    for topic_num in num_topics:
        lda = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=topic_num)
        topics = lda.print_topics(num_topics=topic_num, num_words=10)
        titles = group_by_year_titles[year]

        lda_topic_assignment = [max(p,key=lambda item: item[1]) for p in lda[corpus]]

        ## create documents with assigned topic
        doc_tuples = []
        for i in range(len(titles)):
            tuple = (lda_topic_assignment[i][0], lda_topic_assignment[i][1], group_by_year_titles[year][i])
            doc_tuples.append(tuple)

        ## create topics with belonging documents
        top_dictionary = {}
        for i in range(len(doc_tuples)):
            current_doc = doc_tuples[i]
            doc_topic = current_doc[0]
            doc_title = current_doc[2]

            if top_dictionary.get(doc_topic) == None:
                top_dictionary[doc_topic] = [doc_title]
            else:
                top_dictionary[doc_topic].append(doc_title)

        top_tuples = []
        for topic in range(topic_num):
            if top_dictionary.get(topic) == None:
                top_tuples.append((topic, topics[topic][1], []))
            else:
                top_tuples.append((topic, topics[topic][1], top_dictionary[topic]))

        output = OutputFile(doc_tuples, top_tuples, year, topics, topic_num)
        output.create_files()

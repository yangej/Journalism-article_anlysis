#coding=utf-8

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import os
import csv
from ckiptagger import WS
ws = WS("./data")

## get stop words
common_words = ['奧斯卡', '電影', '片中', '最佳', '今年', '頒獎', ' ']
with open('stop_word.txt') as f:
    stop_words = [line.strip() for line in f.readlines()]
f.close()

with open('stop_word_manual.txt') as f:
    [stop_words.append(line.strip()) for line in f.readlines()]
f.close()

removed_words = common_words + stop_words

## get dataset
dataset_name = 'clean_data.csv'
year_list = []
titles = []
texts_collection = []
with open(dataset_name) as f:
    title_and_content = ''
    for line in f.readlines():
        str_arr = line.split(',')

        year = str_arr[0]
        title = str_arr[3]
        content = str_arr[4]
        title_and_content = title + content

        titles.append(title)
        texts_collection.append(title_and_content)
        year_list.append(year)
f.close()

## split words by ckip
ws_results = ws(texts_collection)
clean_texts_collection  = []
for word_seg in ws_results:
    clean_texts_collection.append(' '.join([word for word in word_seg if word not in removed_words]))

## group dataset by year and split into eng & chi two parts
years = []
group_by_year = {}
eng_regex = r'([A-Z]+[a-z]*)'
for i in range(len(clean_texts_collection)):
    year = year_list[i]
    title = titles[i]
    texts = clean_texts_collection[i]

    if group_by_year.get(year) == None:
        years.append(year)
        group_by_year[year] = [(title, texts)]
    else:
        group_by_year[year].append((title, texts))

class OutputFile:
    def __init__(self, doc_tuples, top_tuples, topic_year, topics, topic_num):
        self.doc_tuples = doc_tuples
        self.top_tuples = top_tuples
        self.topic_year = topic_year
        self.topics = topics
        self.topic_num = topic_num

        dir_path = ''
        if (dataset_name == 'test_articles.csv'):
            dir_path = os.path.abspath(os.getcwd()) + f'/sklearn_test_results/{self.topic_year}_results/{self.topic_year}_{self.topic_num}_cluster_results'
        else:
            dir_path = os.path.abspath(os.getcwd()) + f'/sklearn_results/{self.topic_year}_results/{self.topic_year}_{self.topic_num}_cluster_results'
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
                field_names = ['topic',  'title']
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
                field_names = ['topic', 'features', 'title']
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
num_feature = 10
for year in years:
    current_year_docs = group_by_year[year]

    ## gather all words
    all_docs = []
    for doc_tuple in current_year_docs:
        all_docs.append(doc_tuple[1])

    ## create training dictionary and bag of words
    cv = CountVectorizer()
    cv_data = cv.fit_transform(all_docs)
    cv_feature_names = cv.get_feature_names()


    ## create different number of topics
    for topic_num in num_topics:
        lda = LatentDirichletAllocation(n_components=topic_num,
                                        learning_method='online',
                                        max_iter=1000,
                                        learning_offset=50,
                                        random_state=0).fit(cv_data)
        lda_components = lda.components_
        doc_topic = lda.transform(cv_data)
        ## doc_topic is the probabilities that the doc is assigned to each topics

        ## gather topics with features
        topics = []
        for i, topic in enumerate(lda_components):
            topic_features = [cv_feature_names[i] for i in topic.argsort()[:-num_feature - 1:-1]]
            topics.append(topic_features)

        ## create documents with assigned topic
        doc_tuples = []
        for i in range(doc_topic.shape[0]):
            most_fit_topic = doc_topic[i].argmax()
            title = current_year_docs[i][0]

            tuple = (most_fit_topic, title)
            doc_tuples.append(tuple)

        ## create topics with belonging documents
        top_dictionary = {}
        for i in range(len(doc_tuples)):
            current_doc = doc_tuples[i]
            doc_topic = current_doc[0]
            doc_title = current_doc[1]

            if top_dictionary.get(doc_topic) == None:
                top_dictionary[doc_topic] = [doc_title]
            else:
                top_dictionary[doc_topic].append(doc_title)

        top_tuples = []
        for topic_i in range(topic_num):
            features = '+'.join(topics[topic_i])

            if top_dictionary.get(topic_i) == None:
                top_tuples.append((topic_i, features, []))
            else:
                title = top_dictionary[topic_i]
                top_tuples.append((topic_i, features, title))

        output = OutputFile(doc_tuples, top_tuples, year, topics, topic_num)
        output.create_files()
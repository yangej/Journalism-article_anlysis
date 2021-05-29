#coding=utf-8

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import GridSearchCV
import re
import os
import csv
from ckiptagger import WS
ws = WS("./data")

## get stop words
removed_words = []
with open('stop_word.txt') as f:
    removed_words = [line.strip() for line in f.readlines()]
f.close()

with open('stop_word_manual.txt') as f:
    [removed_words.append(line.strip()) for line in f.readlines()]
f.close()

## get dataset
dataset_name = 'clean_data.csv'
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
f.close()

## split words by ckip
ws_results = ws(texts_collection)
clean_texts_collection  = []
index = 0
for word_seg in ws_results:
    clean_texts_collection.append((titles[index], ' '.join([word for word in word_seg if word not in removed_words])))
    index += 1

class OutputFile:
    def __init__(self, doc_tuples, top_tuples, topics, topic_num):
        self.doc_tuples = doc_tuples
        self.top_tuples = top_tuples
        self.topics = topics
        self.topic_num = topic_num

        dir_path = ''
        if (dataset_name == 'test_articles.csv'):
            dir_path = os.path.abspath(os.getcwd()) + f'/sklearn_test_results/all_results/all_{self.topic_num}_cluster_results'
        else:
            dir_path = os.path.abspath(os.getcwd()) + f'/sklearn_results/all_results/all_{self.topic_num}_cluster_results'
        self.__dir_path = dir_path

    def create_doc_topic_file(self):
        doc_file = f'all_{self.topic_num}_by_document.csv'
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
        doc_file = f'all_{self.topic_num}_by_cluster.csv'
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
num_topics = [5, 6, 7]
num_feature = 20

## gather all words
all_docs = []
for doc_tuple in clean_texts_collection:
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
                                    learning_offset=300,
                                    random_state=0,
                                    learning_decay=0.9).fit(cv_data)
    lda_components = lda.components_
    doc_topic = lda.transform(cv_data)
    ## doc_topic is the scores that the doc is assigned to each topics

    ## gather topics with features
    topics = []
    for i, topic in enumerate(lda_components):
        topic_features = [cv_feature_names[i] for i in topic.argsort()[:-num_feature - 1:-1]]
        topics.append(topic_features)

    ## create documents with assigned topic
    doc_tuples = []
    for i in range(doc_topic.shape[0]):
        most_fit_topic = doc_topic[i].argmax()
        title = clean_texts_collection[i][0]

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

    output = OutputFile(doc_tuples, top_tuples, topics, topic_num)
    output.create_files()
#coding=utf-8

import re
import os
import csv
from ckiptagger import WS
from sklearn.feature_extraction.text import CountVectorizer
ws = WS("./data")

## get stop words
removed_words = []
with open('stop_word.txt') as f:
    removed_words = [line.strip() for line in f.readlines()]
f.close()

with open('stop_word_manual.txt') as f:
    [removed_words.append(line.strip()) for line in f.readlines()]
f.close()


def get_texts_and_original_data(file_path, texts_collection, dataset):
    with open(file_path, newline='') as csvfile:
        rows = csv.reader(csvfile)

        for row in rows:
            year = row[0]
            month = row[1]
            date = row[2]
            title = row[3]
            content = row[4]
            publisher = row[5].strip()
            row_data = [year, month, date, title, content, publisher, '']

            title_and_content = title + content
            texts_collection.append(title_and_content)
            dataset.append(row_data)
    csvfile.close()

def get_keyword_count_for_documents(docs_results, ws_results):
    for wd_index in range(len(ws_results)):
            doc_keywords = {}
            doc = ws_results[wd_index]
            for word in doc:
                if word in keyword:
                    if doc_keywords.get(word) == None:
                        doc_keywords[word] = 1
                    else:
                         doc_keywords[word] += 1
            docs_results.append(doc_keywords)

def creat_dataset_with_count(topic_num, dataset):
    filename = f'{topic_num}_keyword_from_cluster.csv'
    output_path = os.path.join(os.path.abspath(os.getcwd()), filename)
    with open(output_path, 'w', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        field_names = ['年', '月', '日', '標題', '內容', '報社', '關鍵字']
        writer.writerow(field_names)

        for data_index in range(len(dataset)):
            dataset[data_index][6] = docs_results[data_index]
            writer.writerow(dataset[data_index])
    outfile.close()

def get_keyword_count(keyword_count, ws_results):
    for wd_index in range(len(ws_results)):
        doc = ws_results[wd_index]
        for word in doc:
            if word in keyword:
                if keyword_count.get(word) == None:
                    keyword_count[word] = 1
                else:
                     keyword_count[word] += 1

def creat_keyword_count(topic_num, tuples):
    filename = f'all_keyword_count.csv'
    output_path = os.path.join(os.path.abspath(os.getcwd()), filename)
    with open(output_path, 'w', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        field_names = ['keyword', 'count']
        writer.writerow(field_names)

        for tuple in tuples:
            writer.writerow(tuple)
    outfile.close()

dataset = []
texts_collection = []
file_paths = ['./clean_data.csv']
# file_paths = ['./all_5_0_dataset.csv', './all_5_1_dataset.csv', './all_5_2_dataset.csv', './all_5_3_dataset.csv', './all_5_4_dataset.csv']
for file_index in range(len(file_paths)):
    file_path = file_paths[file_index]
    topic_num = file_path[8]

    ## get needed materials
    get_texts_and_original_data(file_path, texts_collection, dataset)

    ## split words by ckip
    ws_results = ws(texts_collection)
    clean_texts_collection  = []
    for word_seg in ws_results:
        clean_texts_collection.append(' '.join([word for word in word_seg if word not in removed_words]))

    ## get keyword count results
    cv = CountVectorizer()
    cv_fit=cv.fit_transform(clean_texts_collection)
    word_list = cv.get_feature_names()
    word_counts = cv_fit.toarray().sum(axis=0)
    keyword_counts = dict(zip(word_list,word_counts))
    keyword_count_tuples = list(keyword_counts.items())

    ## create result files
#     creat_dataset_with_count(topic_num, dataset)
    creat_keyword_count(topic_num, keyword_count_tuples)


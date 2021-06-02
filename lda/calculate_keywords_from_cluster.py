#coding=utf-8

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
    filename = f'{topic_num}_keyword_count.csv'
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
file_paths = ['./all_5_0_dataset.csv', './all_5_1_dataset.csv', './all_5_2_dataset.csv', './all_5_3_dataset.csv', './all_5_4_dataset.csv']
keywords = [
    ['導演','李安','影片','美國','入圍','主角','台灣','pi','藝術家','少年','法國','典禮','演員','夫人','票房','好萊塢','拿下','伊朗','大獎','美元'],
    ['禮服','女星','搭配','紅毯','耳環','珠寶','lv','鑽石','時尚','復古','影后','項鍊','造型','現身','訂製','黑色','服裝','訂製服','金色','蕭邦'],
    ['默片','烏吉','柯達','米歇爾阿札納維休斯','拍賣','精神獎','驚魂記','卡麥蓉狄亞','黛咪','希區考克','李奧納多','有聲','底片','比利懷德','主人','梅里葉','戰馬','凱特溫絲蕾','巴黎','the'],
    ['典禮','梅莉史翠普','柴契爾','主角','影帝','影后','鐵娘子','演員','藝術家','女星','尚杜賈丹','英國','入圍','默片','演出','姊妹','角色','明星','派對','杜賈丹'],
    ['失智症','醫師','中風','克里斯多夫','政治','走出','退化性','總統','照顧','病人','大學','英國','黑人','整形','病情','戰爭','透過','血管性','徐文俊','肉毒桿菌素']
]
for file_index in range(len(file_paths)):
    file_path = file_paths[file_index]
    topic_num = file_path[8]
    keyword = keywords[file_index]

    ## get needed materials
    get_texts_and_original_data(file_path, texts_collection, dataset)

    ## split words by ckip
    ws_results = ws(texts_collection)

    ## get keyword count results
    keyword_count = {}
    get_keyword_count(keyword_count, ws_results)
    keyword_count_tuples = list(keyword_count.items())

    ## get keyword count for each document
    docs_results = []
    get_keyword_count_for_documents(docs_results, ws_results)

    ## create result files
    creat_dataset_with_count(topic_num, dataset)
    creat_keyword_count(topic_num, keyword_count_tuples)


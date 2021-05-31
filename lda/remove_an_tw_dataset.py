#coding=utf-8

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import os
import csv
from ckiptagger import WS
ws = WS("./data")

class OutputFile:
    def __init__(self, find_list):
        self.find_list = find_list

        dir_path = ''
        if (dataset_name == 'test_articles.csv'):
            dir_path = os.path.abspath(os.getcwd()) + f'/sklearn_test_results'
        else:
            dir_path = os.path.abspath(os.getcwd()) + f'/sklearn_results'
        self.__dir_path = dir_path

    def create_count_file(self):
        file = f'no_an_tw_dataset.csv'
        file_path = os.path.join(self.__dir_path, file)
        file_exists = False

        if (os.path.exists(file_path)):
            file_exists = True

        with open(file_path, 'w', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)

            if file_exists == False:
                field_names = ['年', '月', '日', '標題', '內容', '報社']
                writer.writerow(field_names)

            for line in self.find_list:
                writer.writerow(line)
        outfile.close()

    def create_files(self):
        try:
            os.makedirs(self.__dir_path)
        except Exception as ex:
            print('directory exists')

        self.create_count_file()

## get stop words
with open('stop_word.txt') as f:
    stop_words = [line.strip() for line in f.readlines()]
f.close()

with open('stop_word_manual.txt') as f:
    [stop_words.append(line.strip()) for line in f.readlines()]
f.close()

## get dataset
dataset_name = 'clean_data.csv'
year_list = []
titles = []
texts_collection = []
original_data = []
with open(dataset_name) as f:
    title_and_content = ''
    reader = csv.reader(f)
    next(reader, None)
    for line in reader:
        year = line[0]
        title = line[3]
        content = line[4]
        title_and_content = title + content

        year_list.append(year)
        titles.append(title)
        texts_collection.append(title_and_content)
        original_data.append(line)
f.close()

## doc word vectors
ws_results = ws(texts_collection)
keywords = ['台灣', '李安']
print(len(ws_results))
find_list = []
for index in range(len(ws_results)):
    word_seg  = ws_results[index]
    hasKeyword = False
    for word in word_seg:
        if word in keywords:
            hasKeyword = True
            break
    if hasKeyword == False:
        find_list.append(original_data[index])

output = OutputFile(find_list)
output.create_files()
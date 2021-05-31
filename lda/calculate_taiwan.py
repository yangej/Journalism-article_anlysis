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
    def __init__(self, count_tuples):
        self.count_tuples = count_tuples

        dir_path = ''
        if (dataset_name == 'test_articles.csv'):
            dir_path = os.path.abspath(os.getcwd()) + f'/sklearn_test_results'
        else:
            dir_path = os.path.abspath(os.getcwd()) + f'/sklearn_results'
        self.__dir_path = dir_path

    def create_count_file(self):
        file = f'award_keyword_count.csv'
        file_path = os.path.join(self.__dir_path, file)

        with open(file_path, 'w', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            field_names = ['topic',  'title']
            writer.writerow(field_names)

            for tuple in self.count_tuples:
                writer.writerow(tuple)
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
dataset_name = 'test_articles.csv'
years = []
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
        years.append(year)
f.close()

## doc word vectors
ws_results = ws(texts_collection)
keyword = '李安'

## group dataset by year and split into eng & chi two parts
group_by_year = {}
eng_regex = r'([A-Z]+[a-z]*)'
for i in range(len(ws_results)):
    year = years[i]
    texts = ws_results[i]

    if group_by_year.get(year) == None:
        years.append(year)
        group_by_year[year] = [texts]
    else:
        group_by_year[year].append(texts)

## calculate keyword count grouping by year
find_dictionary_by_year = {}
for year in years:
    current_year_docs = group_by_year[year]
    for index in range(len(current_year_docs)):
        doc = current_year_docs[index]
        for word in doc:
            if word == keyword:
                if find_dictionary_by_year.get(word) == None:
                    item = { word: [index] }
                    find_dictionary_by_year[year] = item
                else:
                    find_dictionary_by_year[year][word].append(index)
                break

print(find_dictionary_by_year)

# ## calculate keyword count not grouping by year
#
# find_dictionary = {}
# for index in range(len(ws_results)):
#     word_seg  = ws_results[index]
#     for word in word_seg:
#         if word in find_keyword:
#             if find_dictionary.get(word) == None:
#                 find_dictionary[word] = [index]
#             else:
#                 find_dictionary[word].append(index)
#             break
#
# count_tuples = []
# for keyword in find_keyword:
#     docs = find_dictionary[keyword]
#     tuple = (keyword, len(docs))
#
#     count_tuples.append(tuple)
#
# output = OutputFile(count_tuples)
# output.create_files()
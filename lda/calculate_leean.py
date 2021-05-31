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
    def __init__(self, keyword, count_tuples, year_count_tuples):
        self.keyword = keyword
        self.count_tuples = count_tuples
        self.year_count_tuples = year_count_tuples

        dir_path = ''
        if (dataset_name == 'test_articles.csv'):
            dir_path = os.path.abspath(os.getcwd()) + f'/sklearn_test_results'
        else:
            dir_path = os.path.abspath(os.getcwd()) + f'/sklearn_results'
        self.__dir_path = dir_path

    def create_count_file(self):
        file = f'award_keyword_count.csv'
        file_path = os.path.join(self.__dir_path, file)
        file_exists = False

        if (os.path.exists(file_path)):
            file_exists = True

        with open(file_path, 'a', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)

            if file_exists == False:
                field_names = ['topic',  'title']
                writer.writerow(field_names)

            for tuple in self.count_tuples:
                writer.writerow(tuple)
        outfile.close()

    def create_year_count_file(self):
            file = f'award_{keyword}_count_by_year.csv'
            file_path = os.path.join(self.__dir_path, file)
            file_exists = False

            if (os.path.exists(file_path)):
                file_exists = True

            with open(file_path, 'w', encoding='utf-8') as outfile:
                writer = csv.writer(outfile)
                if file_exists == False:
                    field_names = ['topic',  'title']
                    writer.writerow(field_names)

                for tuple in self.year_count_tuples:
                    writer.writerow(tuple)
            outfile.close()

    def create_files(self):
        try:
            os.makedirs(self.__dir_path)
        except Exception as ex:
            print('directory exists')

        self.create_count_file()
        self.create_year_count_file()

## get stop words
with open('stop_word.txt') as f:
    stop_words = [line.strip() for line in f.readlines()]
f.close()

with open('stop_word_manual.txt') as f:
    [stop_words.append(line.strip()) for line in f.readlines()]
f.close()

## get dataset
dataset_name = 'award_dataset.csv'
year_list = []
titles = []
texts_collection = []
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
f.close()

## doc word vectors
ws_results = ws(texts_collection)
keyword = '李安'

## group dataset by year and split into eng & chi two parts
group_by_year = {}
years = []

for i in range(len(ws_results)):
    year = year_list[i]
    texts = ws_results[i]

    if group_by_year.get(year) == None:
        years.append(year)
        group_by_year[year] = [texts]
    else:
        group_by_year[year].append(texts)


## calculate keyword count grouping by year
find_dictionary_by_year = {}
year_count_tuples = []
for year in years:
    current_year_docs = group_by_year[year]
    for index in range(len(current_year_docs)):
        doc = current_year_docs[index]
        for word in doc:
            if word == keyword:
                if find_dictionary_by_year.get(year) == None:
                    find_dictionary_by_year[year] = [index]
                else:
                    find_dictionary_by_year[year].append(index)
                break
        continue

    doc_count = 0
    if find_dictionary_by_year.get(year) != None:
        doc_count = len(find_dictionary_by_year[year])

    tuple = (year, doc_count)
    year_count_tuples.append(tuple)

print(year_count_tuples)
# calculate keyword count not grouping by year

find_list = {}
for index in range(len(ws_results)):
    word_seg  = ws_results[index]
    for word in word_seg:
        if word == keyword:
            if len(find_list) == 0:
                find_list = [index]
            else:
                find_list.append(index)
            break

count_tuples = []
tuple = (keyword, len(find_list))

count_tuples.append(tuple)
print(count_tuples)

output = OutputFile(keyword, count_tuples, year_count_tuples)
output.create_files()
#coding=utf-8

from wordcloud import WordCloud, ImageColorGenerator
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import GridSearchCV
import numpy as np
import re
import os
import csv
from ckiptagger import WS
ws = WS("./data")

# ## get stop words
# removed_words = []
# with open('stop_word.txt') as f:
#     removed_words = [line.strip() for line in f.readlines()]
# f.close()
#
# with open('stop_word_manual.txt') as f:
#     [removed_words.append(line.strip()) for line in f.readlines()]
# f.close()
#
# ## get dataset
# dataset_name = 'clean_data.csv'
# titles = []
# texts_collection = []
# original_dataset = []
# with open(dataset_name) as f:
#     title_and_content = ''
#     for line in f.readlines():
#         str_arr = line.split(',')
#
#         year = str_arr[0]
#         month = str_arr[1]
#         date = str_arr[2]
#         title = str_arr[3]
#         content = str_arr[4]
#         publisher = str_arr[5].strip()
#         original_data = (year, month, date, title, content, publisher)
#         title_and_content = title + content
#
#         original_dataset.append(original_data)
#         titles.append(title)
#         texts_collection.append(title_and_content)
# f.close()
# collection_length = len(original_dataset)
#
# ## split words by ckip
# ws_results = ws(texts_collection)
# clean_texts_collection  = []
# index = 0
# for word_seg in ws_results:
#     clean_texts_collection.append((titles[index], ' '.join([word for word in word_seg if word not in removed_words])))
#     index += 1

samples = ['awesome unicorns are awesome','batman forever and ever','I love batman forever']
bigram_vectorizer = CountVectorizer(ngram_range=(1, 2), vocabulary = {'awesome unicorns':0, 'batman forever':1})
co_occurrences = bigram_vectorizer.fit_transform(samples)
print 'Printing sparse matrix:', co_occurrences
print 'Printing dense matrix (cols are vocabulary keys 0-> "awesome unicorns", 1-> "batman forever")', co_occurrences.todense()
sum_occ = np.sum(co_occurrences.todense(),axis=0)
print 'Sum of word-word occurrences:', sum_occ
print 'Pretty printig of co_occurrences count:', zip(bigram_vectorizer.get_feature_names(),np.array(sum_occ)[0].tolist())
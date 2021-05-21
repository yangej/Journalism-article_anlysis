#coding=utf-8

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
removed_words = common_words + stop_words
f.close()

## get dataset
initial_data_tuples = []
data_tuples = []
with open('clean_data.csv') as f:
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
split_data_objs = []
eng_regex = r'([A-Z]+[a-z]*)'
for tuple in data_tuples:
    year = tuple[0]
    title_and_content = tuple[1]

    eng_words = re.findall(eng_regex, title_and_content)
    chi_words = [word for word in jieba.lcut(re.sub(eng_regex, '', title_and_content.replace(" ", ""))) if word not in removed_words]

    split_data_objs.append({ 'eng_words': eng_words, 'chi_words': chi_words })

def transform_id2word(map, id):
    for word, word_id in map.items():
        if id == word_id:
            return word

def gen_tfidf_all():
    word_list = []
    for obj in split_data_objs:
        title_and_content = obj['eng_words'] + obj['chi_words']
        word_list.append(title_and_content)

    dictionary = corpora.Dictionary(word_list)
    corpus = [dictionary.doc2bow(word) for word in word_list]

    token_2_id_map = dictionary.token2id
    tfidf_list = []

    for doc_bow in corpus:
        for word_freq in doc_bow:
            word_id = word_freq[0]
            word_frequency = word_freq[1]
            word = transform_id2word(token_2_id_map, word_id)

            tfidf_list.append((word, word_frequency))

    dir_path = os.path.abspath(os.getcwd()) + f'/results/tfidf'
    try:
        os.makedirs(dir_path)
    except Exception as ex:
        print('directory exists')

    output_file = f'all_tfidf_test.csv'
    output_path = os.path.join(dir_path, output_file)

    output_file_exist = False
    if (os.path.exists(output_path)):
        output_file_exist = True

    with open(output_path, 'w', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        if (output_file_exist == False):
            field_names = ['word', 'tfidf']
            writer.writerow(field_names)

        for tuple in tfidf_list:
            writer.writerow(tuple)
gen_tfidf_all()
#coding=utf-8

from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import re
import os
import csv
from ckiptagger import WS
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import networkx as nx
font = fm.FontProperties(fname='./NotoSansTC-Regular.otf')  # speicify font
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
datasets = ['test_articles.csv']
# datasets = ['all_5_0_dataset', 'all_5_1_dataset', 'all_5_2_dataset', 'all_5_3_dataset', 'all_5_4_dataset']
for dataset in datasets:
    cluster_num = dataset[6]
    texts_collection = []
    with open(dataset_name) as f:
        title_and_content = ''
        for line in f.readlines():
            str_arr = line.split(',')

            title = str_arr[3]
            content = str_arr[4]
            title_and_content = title + content

            texts_collection.append(title_and_content)
    f.close()

    ## split words by ckip
    ws_results = ws(texts_collection)
    clean_texts_collection  = []
    for word_seg in ws_results:
        clean_texts_collection.append(' '.join([word for word in word_seg if word not in removed_words]))

    ngram_size = 2

    vectorizer = CountVectorizer(ngram_range=(ngram_size,ngram_size))
    vectorizer.fit(clean_texts_collection) # build ngram dictionary
    ngram = vectorizer.transform(clean_texts_collection) # get ngram

    ngram_counts = ngram.toarray()
    ngram_features = vectorizer.get_feature_names()
    feature_tuples = []
    for feature in ngram_features:
        words = feature.split(' ')
        tuple = (words[0], words[1])
        feature_tuples.append(tuple)

    count_dict = {}
    for doc in ngram_counts:
        for index in range(len(feature_tuples)):
            if doc[index] == 1:
                if count_dict.get(feature_tuples[index]) == None:
                    count_dict[feature_tuples[index]] = 1
                else:
                    count_dict[feature_tuples[index]] += 1
    print(count_dict)

    # Create network plot

    G = nx.Graph()

    # Create connections between nodes
    for word_tuple, count in count_dict.items():
        G.add_edge(word_tuple[0], word_tuple[1], weight=(count * 10))

    pos = nx.circular_layout(G)
    edges = G.edges()
    weights = [G[u][v]['weight'] for u,v in edges]
    fig, ax = plt.subplots(figsize=(10, 8))
    pos = nx.spring_layout(G, k=2)

    # Plot networks
    nx.draw_networkx(G, pos,
                     font_size=16,
                     width=weights,
                     edge_color='grey',
                     node_color='purple',
                     with_labels = False,
                     ax=ax)

    # Create offset labels
    for key, value in pos.items():
        x, y = value[0]+.135, value[1]+.045
        ax.text(x, y,
            font_family=font,
            s=key,
            bbox=dict(facecolor='red', alpha=0.25),
            horizontalalignment='center', fontsize=13)

    plt.savefig(f'{cluster_num}_word_network.png')
    print('finish!')
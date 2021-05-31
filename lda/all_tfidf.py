
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
dataset_name = 'no_an_tw_dataset.csv'
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
    def __init__(self, tfidf_tuples):
        self.tfidf_tuples = tfidf_tuples

        dir_path = ''
        if (dataset_name == 'test_articles.csv'):
            dir_path = os.path.abspath(os.getcwd()) + f'/sklearn_test_results/tfidf'
        else:
            dir_path = os.path.abspath(os.getcwd()) + f'/sklearn_results/tfidf'
        self.__dir_path = dir_path

    def create_tfidf_file(self):
        tfidf_file = f'all_tfidf.csv'
        tfidf_path = os.path.join(self.__dir_path, tfidf_file)

        with open(tfidf_path, 'w', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            field_names = ['topic',  'title']
            writer.writerow(field_names)

            for tuple in self.tfidf_tuples:
                writer.writerow(tuple)
        outfile.close()

    def create_files(self):
        try:
            os.makedirs(self.__dir_path)
        except Exception as ex:
            print('directory exists')

        self.create_tfidf_file()


## gather all words
all_docs = []
for doc_tuple in clean_texts_collection:
    all_docs.append(doc_tuple[1])
print(all_docs)
## create training dictionary and bag of words
tfidf_transformer = TfidfVectorizer(smooth_idf=True, use_idf=True)
tfidf_vectors = tfidf_transformer.fit_transform(all_docs)
vector_dictionary = tfidf_transformer.vocabulary_

feature_index = tfidf_vectors[0,:].nonzero()[1]
tfidf_scores = zip(feature_index, [tfidf_vectors[0, x] for x in feature_index])

#     Assume result of tfidf_vectors would like => (A,B) C
#     A: Document index
#     B: Specific word-vector index
#     C: TFIDF score for word B in document A

term_dictionary = {}
for term, index in vector_dictionary.items():
    term_dictionary[index] = term

tfidf_tuples = [(term_dictionary[tfidf_tuple[0]], tfidf_tuple[1]) for tfidf_tuple in tfidf_scores]
print(tfidf_tuples)
output = OutputFile(tfidf_tuples)
output.create_files()


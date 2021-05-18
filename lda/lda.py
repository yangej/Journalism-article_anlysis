#coding=utf-8

# #匯入模組與資料並進行檢視
# import pandas as pd
# reviews_data = pd.read_csv('clean_data.csv')
# reviews_data.head()

import jieba
import jieba.analyse
import re

## get stop words
common_words = ['奧斯卡', '電影', '片中']
with open('stop_word.txt') as f:
    stop_words = [line.strip() for line in f.readlines()]
removed_words = common_words + stop_words
f.close()

print(removed_words)

## get dataset
data_tuples = []
with open('test_articles.csv') as f:
    title_and_content = ''
    for str in f.readlines():
        str_arr = str.split(',')
        title_and_content = str_arr[3] + str_arr[4]
        data_tuples.append((str_arr[0], title_and_content, str_arr[5]))
f.close()

## group dataset by year and split into eng & chi two parts
years = []
group_by_year = {}
eng_regex = r'([A-Z]+[a-z]*)'
for tuple in data_tuples:
    year = tuple[0]
    title_and_content = tuple[1]
    eng_words = re.findall(eng_regex, title_and_content)
    chi_words = ''.join([word for word in jieba.lcut(re.sub(eng_regex, '', title_and_content)) if word not in removed_words])

    if group_by_year.get(year) == None:
        years.append(year)
        group_by_year[year] = { 'eng_words': eng_words, 'chi_words': chi_words }
    else:
        group_by_year[year]['eng_words'] += eng_words
        group_by_year[year]['chi_words'] += chi_words
print(group_by_year)

# chi_words = ''.join([word for word in words if word not in stopWords])
# print('--------------------------------- 原文：')
# print(chi_words)
#
# keywords = jieba.analyse.extract_tags(chi_words)
# print('--------------------------------- 關鍵字：')
# print(keywords)
#
# seg_list = jieba.lcut(chi_words, cut_all=True)
# print('--------------------------------- 斷詞後：')
# print(seg_list)

# #使用scikit-learn進行向量轉換
# #忽略在文章中佔了90%的文字(即去除高頻率字彙)
# #文字至少出現在2篇文章中才進行向量轉換
# from sklearn.feature_extraction.text import CountVectorizer
# cv = CountVectorizer(max_df = 0.9, min_df =2, stop_words = 'english')
# df = df.dropna
# dtm = cv.fit_transform(df['related_data'])
#
# #使用LDA演算法
# from sklearn.decomposition import LatentDirichletAllocation
# LDA = LatentDirichletAllocation(n_components=5, random_state=42)
# LDA.fit(dtm)
# #n_components => 想分成幾群
# #random_state => 設定成42
#
# #觀看結果
# for i,topic in enumerate(LDA.components_):
#     print(f"TOP 10 WORDS PER TOPIC #{i}")
#     print([cv.get_feature_names()[index] for index in topic.argsort()[-10:]])
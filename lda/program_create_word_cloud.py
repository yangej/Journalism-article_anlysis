#coding=utf-8

import csv
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def read_in_data(dictionary, filename):
    with open(f'./calculation_results/keyword_count_by_clusters/{filename}') as file:
        lines = csv.reader(file)
        next(lines, None)

        for line in lines:
            keyword = line[0]
            count = int(line[1])
            dictionary[keyword] = count
    file.close()

filenames = ['0_keyword_count.csv', '1_keyword_count.csv', '2_keyword_count.csv', '3_keyword_count.csv', '4_keyword_count.csv']
font_path='./NotoSansTC-Regular.otf'

for filename in filenames:
    keyword_counts = {}
    read_in_data(keyword_counts, filename)

    wordcloud = WordCloud(font_path=font_path).generate_from_frequencies(keyword_counts)
    wordcloud.to_file(f'wordcloud_{filename[:-4]}.png')
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()
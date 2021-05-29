#coding=utf-8

import re
import os
import csv

## get stop words
award_titles = []
outfit_titles = []
file_path = './sklearn_results/all_results/all_5_cluster_results/all_5_by_document.csv'
with open(file_path, newline='') as csvfile:
    rows = csv.reader(csvfile)

    for row in rows:
        topic = row[0]
        title = row[1]
        if topic == '0':
            print('0: ', title)
            award_titles.append(title)
        elif topic == '3':
            print('3: ', title)
            outfit_titles.append(title)
csvfile.close()

file_path = 'clean_data.csv'
award_dataset = []
outfit_dataset = []
with open(file_path, newline='') as csvfile:
    rows = csv.reader(csvfile)

    for row in rows:
        title = row[3]
        if title in award_titles:
            award_dataset.append(row)
        elif title in outfit_titles:
            outfit_dataset.append(row)
csvfile.close()

file_infos = [
    { 'filename': 'award_dataset.csv', 'dataset': award_dataset },
    { 'filename': 'outfit_dataset.csv', 'dataset': outfit_dataset}
]

for file_info in file_infos:
    output_path = os.path.join(os.path.abspath(os.getcwd()), file_info['filename'])

    with open(output_path, 'w', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        field_names = ['年', '月', '日', '標題', '內容', '報社']
        writer.writerow(field_names)

        for data in file_info['dataset']:
            writer.writerow(data)
    outfile.close()
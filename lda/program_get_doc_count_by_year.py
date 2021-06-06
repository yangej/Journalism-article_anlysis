#coding=utf-8

import csv

file_path = './dataset_with_an.csv'
years = []
with open(file_path, newline='') as csvfile:
    rows = csv.reader(csvfile)

    for row in rows:
        year = row[0]
        years.append(year)
csvfile.close()

count_by_year = {}
for year in years:
    if count_by_year.get(year) == None:
        count_by_year[year] = 1
    else:
        count_by_year[year] += 1

print(count_by_year)
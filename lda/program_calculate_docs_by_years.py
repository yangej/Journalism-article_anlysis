#coding=utf-8

import re
import os
import csv

read_file = 'Streep_dataset.csv'
year_count = {}
with open(read_file) as file:
    lines = csv.reader(file)
    next(lines, None)
    for line in lines:
        year = line[0]
        if year_count.get(year) == None:
            year_count[year] = 1
        else:
            year_count[year] += 1
file.close()

print(year_count)
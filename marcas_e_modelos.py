#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob,csv
def extract(csv_path, delimiter=','):
    """Simply pulls rows into a DictReader"""
    with open(csv_path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        for row in reader:
            yield row

mark={}
for file in glob.glob("./marcas-e-modelos/marcas*.csv"):
    for record in extract(file, ";"):
        mark[record['\ufeffID']]={"NOME":record['NOME'],"MODELS":[]}

for file in glob.glob("./marcas-e-modelos/modelos*.csv"):
    for record in extract(file, ";"):
        print(record)
        mark[record['IDMARCA']]["MODELS"].append(record['NOME'])

print(mark)
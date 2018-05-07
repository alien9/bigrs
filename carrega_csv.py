#!/usr/bin/env python
# -*- coding: utf-8 -*-

from csvutils import *
vitimas={}
for y in range(2010,2018):
    for row in extract("maps/Vitimas%s.csv" % (str(y)), '\t'):
        if not row['id_acidente'] in vitimas:
            vitimas[row['id_acidente']]=[]
        vitimas[row['id_acidente']].append(row)
        print(y)

veiculos={}
for y in range(2010,2018):
    for row in extract("maps/Veiculos%s.csv"%(str(y)),'\t'):
        if not row['id_acidente'] in veiculos:
            veiculos[row['id_acidente']]=[]
        veiculos[row['id_acidente']].append(row)
        #print(row)
        print(y)
print(veiculos)
print(vitimas)

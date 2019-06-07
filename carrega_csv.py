#!/usr/bin/env python
# -*- coding: utf-8 -*-

from csvutils import *

directory='SAT'

def loadvitimas():
    vitimas = {}
    for row in extract("%s/vitimas.csv" % (directory), ','):
        if not row['id_acidente'] in vitimas:
            vitimas[row['id_acidente']]=[]
        if not row in vitimas[row['id_acidente']]:
            vitimas[row['id_acidente']].append(row)
    return vitimas
def loadveiculos():
    veiculos = {}
    for row in extract("%s/veiculos.csv" % (directory),','):
        if not row['id_acidente'] in veiculos:
            veiculos[row['id_acidente']]=[]
        if not row in veiculos[row['id_acidente']]:
            veiculos[row['id_acidente']].append(row)
    return veiculos
#print(veiculos)
#print(vitimas)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from csvutils import *
vitimas={}
for row in extract("SAT/vitimas.csv", ','):
    if not row['id_acidente'] in vitimas:
        vitimas[row['id_acidente']]=[]
    if not row in vitimas[row['id_acidente']]:
        vitimas[row['id_acidente']].append(row)

veiculos={}
for row in extract("SAT/veiculos.csv",','):
    if not row['id_acidente'] in veiculos:
        veiculos[row['id_acidente']]=[]
    if not row in veiculos[row['id_acidente']]:
        veiculos[row['id_acidente']].append(row)

#print(veiculos)
#print(vitimas)

#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json,psycopg2

cstring="dbname='driver' user='driver' host='localhost' port='5432' password='lol_256_rms'"

conn = psycopg2.connect(cstring)
cur=conn.cursor()

cur.execute('select uuid, data from ashlar_record')

for uuid,d in cur.fetchall():
    #   d=json.loads(row[1])
    for v in d[u'driverVíTima']:
        print(v['Idade'])
        try:
            age=int(v['Idade'])
            if age > 59:
                faixa = '60 ou mais'
            elif age > 29:
                faixa = '30 a 59'
            elif age > 24:
                faixa = '25 a 29'
            elif age > 19:
                faixa = '20 a 24'
            elif age > 17:
                faixa = '18 a 19'
            elif age > 14:
                faixa = '15 a 17'
            elif age > 10:
                faixa = '11 a 14'
            elif age > 5:
                faixa = '6 a 10'
            else:
                faixa = '5 ou menos'

        except:
            faixa='Sem Informação'
        print(faixa)
        v['Faixa'] = faixa
    print(d)
    cur.execute("update ashlar_record set data=%s where uuid=%s",(json.dumps(d), uuid))
    conn.commit()
"""
0-5
6-10
11-14
15-17
18-19
20-24
25-29
30-59
60+
SI (Sem Info)

"""
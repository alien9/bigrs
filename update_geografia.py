#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json,psycopg2

cstring="dbname='driver'"
conn = psycopg2.connect(cstring)
cur=conn.cursor()

cur.execute('select uuid, data, geom from ashlar_record')
n=0
for uuid,d,g in cur.fetchall():
    n+=1
    cur.execute("select ds_nome, 'dist' from distrito where st_contains(geom,%s)='t'", (g,))
    distrito = cur.fetchone()
    if distrito is not None:
        d['driverIncidenteDetails']['Distrito']=distrito[0]
    cur.execute("select sp_nome, 'sub' from subprefeitura where st_contains(geom,%s)='t'", (g,))
    sub = cur.fetchone()
    if sub is not  None:
        d['driverIncidenteDetails']['Subprefeitura']=sub[0]
    print(n)
    print(d)
    cur.execute("update ashlar_record set data=%s where uuid=%s",(json.dumps(d), uuid))
    conn.commit()

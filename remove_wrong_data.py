#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, requests, getpass, csv, json, uuid, glob
from dateutil import parser
from dateutil.tz import gettz
import pytz #,ogr

tz1 = gettz('America/Sao_Paulo')

username=input("Usuário:")
password=getpass.getpass("Senha:")

def extract(csv_path, delimiter=','):
    """Simply pulls rows into a DictReader"""
    with open(csv_path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        for row in reader:
            yield row
def _add_local_id(dictionary):
    dictionary['_localId'] = str(uuid.uuid4())

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

client=requests.session()
URL="https://driver.alien9.net"
r=client.get(URL+"/api-auth/login/?next=/api/")
csrf=r.cookies.get('csrftoken')
cookies=r.cookies
r=client.post(URL+"/api-auth/login/", data={"username":username,"password":password,"csrfmiddlewaretoken":csrf,"next":"/api/"},cookies=r.cookies,headers={"referer":URL+"/api-auth/login/?next=/api/"})
r=client.get(URL+"/api/recordtypes/?active=True&format=json",cookies=r.cookies,headers={"referer":URL+"/api/"})
j=r.json()
"""
schema_uuid=None
for rj in j['results']:
    if rj["label"]=="Intervention":
        schema_uuid=rj['current_schema']
if schema_uuid is None:
    print("Tipo 'Intervention' não existe.")
    exit()
"""

n=1
while n>0:
    r=client.get(URL+'/api/records/?archived=False&jsonb={%22interventionDetails%22:{%22Type%22:{%22_rule_type%22:%22containment%22,%22contains%22:[%22Fiscalização%20de%20Velocidade%22]}}}')
    j=r.json()
    print("%s encontrados"%(j['count']))
    n=int(j['count'])
    print(csrf)
    print(cookies)

    for re in j['results']:
        print(re["uuid"])
        print(URL+"/api/records/"+re["uuid"]+"/?archived=False")
        r=client.post(URL+"/api/records/"+re["uuid"]+"/?archived=False", data={"csrfmiddlewaretoken":csrf, "_method":"DELETE"},cookies=cookies,headers={"referer":URL+"/api-auth/login/?next=/api/"})
        print(r)
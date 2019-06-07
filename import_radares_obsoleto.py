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
print(j)
schema_uuid=None
for rj in j['results']:
    if rj["label"]=="Intervention":
        schema_uuid=rj['current_schema']
if schema_uuid is None:
    print("Tipo 'Intervention' não existe.")
    exit()

r=client.get(URL+"/api/recordschemas/%s/"%(j['results'][0]["current_schema"]),cookies=r.cookies,headers={"referer":URL+"/api/recordtypes/?active=True&format=json"})
j=r.json()

n=0
for record in extract("./maps/radares_tsv.csv", "\t"):
    print(record)
    if record['_LIGADO']=='SIM' or record['_DATA DE D'] != "":
        print(record['_DATA DE P'])
        if re.match("V",record['_ENQUADRA']):
            print("é velocidade")
            dia, mes, ano= record['_DATA DE P'].split('/')
            stringdate="%s-%s-%s 00:00:00"%(int(ano)+2000,mes,dia)
            occurred_date = pytz.timezone('America/Sao_Paulo').localize(parser.parse(stringdate))
            print(n)
            print(record['_VELOCIDAD'])
            try:
                latitude, longitude=re.sub("[\)\(]","",record['_(LATITUDE']).split(" ")
                intervention={
                    "data":{
                        "interventionDetails":{
                            u'Descrição':record['_VELOCIDAD'],
                            "Type":"Fiscalização de Velocidade",
                            "_localId":str(uuid.uuid4()),
                        },
                    },
                    'occurred_from': occurred_date.isoformat(),
                    'occurred_to': occurred_date.isoformat(),
                    'geom': "SRID=4326;POINT(%s %s)"%(float(longitude), float(latitude), ),
                    'schema':schema_uuid,
                }
                """
                response = client.post(URL + '/api/records/?archived=False',
                                       json=intervention,
                                       headers={'Content-type': 'application/json', "X-CSRFToken": csrf,
                                                "Referer": URL + "/api/recordtypes/?active=True&format=json"},
                                       cookies=cookies, )

                print(response)
                """
            except:
                print(record['_(LATITUDE'])

    n+=1

    #X,Y,id_acident,data,Ano,X,Y,hora,cod_acid,tipo_acide,carros,caminhao,bicicleta,moto,onibusmicr,van,vuc,carreta,carroca,outros,sem_inform,feridos,mortos

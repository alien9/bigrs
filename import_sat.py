#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, requests, getpass, csv, json
from dateutil import parser
from dateutil.tz import gettz
import pytz #,ogr
tz1 = gettz('America/Sao_Paulo')
TIPOS_COLISAO={
    "CT":"Traseira",
    "CF":"Frontal",
    "CD":"À Direita",
    "CL":"Lateral",
    "TB":"Tombamento",
    "CO":"Colisão com Objeto na Pista",
    "CH":"Colisão com Objeto Fora da Pista",
    "CC":"Colisão com Veículo Estacionado",
    "AT":"Atropelamento",
    "AA":"Atropelamento de Animal"
}


username=input("Usuário:")
password=getpass.getpass("Senha:")

def extract(csv_path):
    """Simply pulls rows into a DictReader"""
    with open(csv_path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            yield row


client=requests.session()
URL="https://driver.alien9.net"
r=client.get(URL+"/api-auth/login/?next=/api/")
csrf=r.cookies.get('csrftoken')
cookies=r.cookies
r=client.post(URL+"/api-auth/login/", data={"username":username,"password":password,"csrfmiddlewaretoken":csrf,"next":"/api/"},cookies=r.cookies,headers={"referer":URL+"/api-auth/login/?next=/api/"})
r=client.get(URL+"/api/recordtypes/?active=True&format=json",cookies=r.cookies,headers={"referer":URL+"/api/"})
j=r.json()
r=client.get(URL+"/api/recordschemas/%s/"%(j['results'][0]["current_schema"]),cookies=r.cookies,headers={"referer":URL+"/api/recordtypes/?active=True&format=json"})
j=r.json()
record=None
for r in extract("acidentes_sp_2010_a_2015.csv"):
    record=r
    dia, mes, ano= record['data'].split('/')
    hora, minuto= record['hora'].split(':')
    stringdate="%s-%s-%s %s:%s:00"%(ano,mes,dia,hora,minuto)
    occurred_date = pytz.timezone('America/Sao_Paulo').localize(parser.parse(stringdate))
    #point = ogr.Geometry(ogr.wkbPoint)
    #point.AddPoint(float(record['X']), float(record['Y']))
    #point.FlattenTo2D()
    tipo=None
    if record['tipo_acide'] in TIPOS_COLISAO:
        tipo=TIPOS_COLISAO[record['tipo_acide']]
    obj = {
        'data': {
            'incidentDetails': {
                "Tipo de Colisão":tipo,
                "acidente_id":record['id_acident'],
            },
            'person': [],
            'vehicle': []
        },
        'schema': str(j['uuid']),
        'occurred_from': occurred_date.isoformat(),
        'occurred_to': occurred_date.isoformat(),
        'geom': "SRID=4326;POINT(%s %s)"%(float(record['X']), float(record['Y']), ),
    }
    response = client.post(URL + '/api/records/',
                           json=obj,
                           headers={'Content-type': 'application/json',  "X-CSRFToken":csrf, "Referer": URL+"/api/recordtypes/?active=True&format=json"},
                           cookies=cookies,)
    print(response.content)

    #X,Y,id_acident,data,Ano,X,Y,hora,cod_acid,tipo_acide,carros,caminhao,bicicleta,moto,onibusmicr,van,vuc,carreta,carroca,outros,sem_inform,feridos,mortos


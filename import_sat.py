#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, requests, getpass, csv, json, uuid
from dateutil import parser
from dateutil.tz import gettz
import pytz #,ogr

tz1 = gettz('America/Sao_Paulo')
TIPOS_COLISAO={
    "CO":"Colisão",
    "CF":"Colisão frontal",
    "CT":"Colisão traseira",
    "CL":"Colisão lateral",
    "CV":"Colisão transversal",
    "CP":"Capotamento",
    "TB":"Tombamento",
    "AT":"Atropelamento",
    "AA":"Atropelamento de animal",
    "CH":"Choque",
    "QM":"Queda moto/bicicleta",
    "QV":"Queda veículo",
    "QD":"Queda ocupante dentro",
    "QF":"Queda ocupante fora",
    "OU":"Outros",
    "SI":"Sem informações",
}

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
n=0
for record in extract("./maps/acidentes_sp_2010_a_2015.csv"):
    print(record)
    n+=1
    if n>20:
        break

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
    if int(record['mortos']) > 0:
        severidade="Fatal"
    else:
        if int(record['feridos']) > 0:
            severidade="Ferimento"
        else:
            severidade="Danos Materiais"
    num_vitimas=int(record['mortos'])+int(record['feridos']) 
    print(num_vitimas)
    num_veiculos=0
    for key in [
        "carros",
        "caminhao",
        "bicicleta",
        "moto",
        "onibusmicr",
        "van",
        "vuc",
        "carreta",
        "carroca",
        "outros",
        ]:
        num_veiculos+=int(record[key])

    obj = {
        'data': {
            'driverIncidentDetails': {
                "Tipo de Colisão":tipo,
                "acidente_id":record['id_acident'],
                "Severidade": severidade,
                "Veículos": num_veiculos,
                "Número de Veículos": num_veiculos,
                "Número de Vítimas": num_vitimas,
            },
            'person': [],
            'vehicle': []
        },
        'schema': str(r.json()['uuid']),
        'occurred_from': occurred_date.isoformat(),
        'occurred_to': occurred_date.isoformat(),
        'geom': "SRID=4326;POINT(%s %s)"%(float(record['X']), float(record['Y']), ),
    }

    _add_local_id(obj['data']['driverIncidentDetails'])
    response = client.post(URL + '/api/records/',
                           json=obj,
                           headers={'Content-type': 'application/json',  "X-CSRFToken":csrf, "Referer": URL+"/api/recordtypes/?active=True&format=json"},
                           cookies=cookies,)

    print(response)
    #X,Y,id_acident,data,Ano,X,Y,hora,cod_acid,tipo_acide,carros,caminhao,bicicleta,moto,onibusmicr,van,vuc,carreta,carroca,outros,sem_inform,feridos,mortos
n=0
print("Veículos")
for record in extract("./maps/Veiculos2010.csv", "\t"):
    n+=1
    if n > 40:
        break
    print(record)
    r=client.get(URL+"/api/records/?jsonb={%22driverIncidentDetails%22:{%22acidente_id%22:{%22_rule_type%22:%22containment%22,%22contains%22:[%22"+record['id_acidente']+"%22]}}}")
    j=r.json()
    if int(j['count'])==1:
        incident=j['results'][0]
        if incident['data']['driverVehicle'] is None:
            incident['data']['driverVehicle']=[]
"""
        incident['data']['driverVehicle'].append({
"Sobrecarregado"
Chassis
:
"4345gu67gj7tjgjjyu"
Danos
:
"Traseira"
Direção
:
"Sul"
Falha
:
"Luzes"
Manobra
:
"Ré"
Marca
:
"Fusca"
Modelo
:
"Fusqueta"
Número do Motor
:
"76576576764654"
Placa
:
"NG-2472"
Seguro
:
""
Tipo de Veículo
:
"Carro"
_localId
:
"2786d539-dade-476c-b833-caa8a5ddcbb9"
            driverVehicle
            :
                [{Falha: "Luzes", Tipo de Veículo: "Carro", Manobra: "Ré", Danos: "Traseira", Seguro: "",…}]
        0
        :
        {Falha: "Luzes", Tipo de Veículo: "Carro", Manobra: "Ré", Danos: "Traseira", Seguro: "",…}
        })
"""

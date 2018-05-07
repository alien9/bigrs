#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, requests, getpass, csv, json, uuid, glob
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
TIPOS_VEICULO={
    "AU":"Auto",
    "MO":"Moto",
    "ON":"Ônibus",
    "CA":"Caminhão",
    "BI":"Bicicleta",
    "MT":"Moto Táxi",
    "OF":"Ônibus Fretado/Internmunicipal",
    "OU":"Ônibus Urbano",
    "MC":"Microônibus",
    "VA":"Van",
    "VC":"Vuc",
    "CM":"Caminhonete/Camioneta",
    "CR":"Carreta",
    "JI":"Jipe",
    "OT":"Outros",
    "SI":"Sem Informação",
    "CO":"Carroça",
}
TIPOS_VITIMA={
    "CD":"Condutor",
    "PS":"passageiro",
    "PD":"Pedestre",
    "OU":"OUtros",
    "SI":"Sem Informação",
}
CLASS_VITIMA={
    "F":"Ferida",
    "M":"Morta",
}
GENERO={
    "M":"Masculino",
    "F":"Feminino",
}
CLASSIFICACAO={
    "F":"Grave",
    "M":"Fatal",
}
url=input("URL:[https://motorista.alien9.net]")
if url=="":
    url="https://motorista.alien9.net"
username=input("Usuário:")
password=getpass.getpass("Senha:")

def extract(csv_path, delimiter=',', quotechar='"'):
    """Simply pulls rows into a DictReader"""
    with open(csv_path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter, quotechar=quotechar)
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
URL=url #"https://driver.alien9.net"
r=client.get(URL+"/api-auth/login/?next=/api/")
csrf=r.cookies.get('csrftoken')
cookies=r.cookies
r=client.post(URL+"/api-auth/login/", data={"username":username,"password":password,"csrfmiddlewaretoken":csrf,"next":"/api/"},cookies=r.cookies,headers={"referer":URL+"/api-auth/login/?next=/api/"})
r=client.get(URL+"/api/recordtypes/?active=True&format=json",cookies=r.cookies,headers={"referer":URL+"/api/"})
j=r.json()
r=client.get(URL+"/api/recordschemas/%s/"%(j['results'][0]["current_schema"]),cookies=r.cookies,headers={"referer":URL+"/api/recordtypes/?active=True&format=json"})
j=r.json()
n=0



for record in extract("./maps/acidentes_sp_2016.csv"):
    print(record)
    n+=1
    #if n>20:
    #    break
    if "data_e_hora" in record:
            stringdate = record['data_e_hora']
    else:
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
        if key in record:
            num_veiculos+=int(record[key])
    if "veiculos" in record:
        num_veiculos=sum([int(n) for n in list(record["veiculos"])])

    obj = {
        'data': {
            'driverIncidentDetails': {
                "Tipo de Incidente":tipo,
                "acidente_id":record['id_acident'],
                "Severidade": severidade,
                "Veículos": num_veiculos,
                "Vítimas": num_vitimas,
            },
            'person': [],
            'vehicle': []
        },
        'schema': str(r.json()['uuid']),
        'occurred_from': occurred_date.isoformat(),
        'occurred_to': occurred_date.isoformat(),
        'geom': "SRID=4326;POINT(%s %s)"%(float(record['x']), float(record['y']), ),
    }

    _add_local_id(obj['data']['driverIncidentDetails'])
    response = client.post(URL + '/api/records/',
                           json=obj,
                           headers={'Content-type': 'application/json',  "X-CSRFToken":csrf, "Referer": URL+"/api/recordtypes/?active=True&format=json"},
                           cookies=cookies,)

    print(response)

    #X,Y,id_acident,data,Ano,X,Y,hora,cod_acid,tipo_acide,carros,caminhao,bicicleta,moto,onibusmicr,van,vuc,carreta,carroca,outros,sem_inform,feridos,mortos

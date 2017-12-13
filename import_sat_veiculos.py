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
    "PS":"Passageiro",
    "PD":"Pedestre",
    "OU":"Outros",
    "SI":"Sem Informação",
}
CLASS_VITIMA={
    "F":"Ferida",
    "M":"Morta",
}
GENERO={
    "M":"Masculino",
    "F":"Feminino",
    "X":"Sem Informação"
}
CLASS_INCIDENTE={
    "F":"Grave",
    "M":"Fatal",
}
username="tiago" #input("Usuário:")
password="peganingas" #getpass.getpass("Senha:")

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
r=client.get(URL+"/api/recordschemas/%s/"%(j['results'][0]["current_schema"]),cookies=r.cookies,headers={"referer":URL+"/api/recordtypes/?active=True&format=json"})
j=r.json()

r=client.get(URL+"/api/records/?format=json")
j_inc=r.json()

print("Encontrados %s incidentes na base. Carregando veículos..."%(j_inc['count']))

n=0
print("Veículos")
total_veiculos=0
for file in glob.glob("./maps/Veiculos*.csv"):
    total_veiculos+=file_len(file)-1
print("%s veículos.                                                           "%(total_veiculos))
veiculos={}
for file in glob.glob("./maps/Veiculos*.csv"):
    for record in extract(file, "\t"):
        n+=1
        tk='tipo_veiculo'
        if 'TIPO_VEICU' in record:
            tk='TIPO_VEICU'
        if record[tk] in TIPOS_VEICULO:
            tipo = TIPOS_VEICULO[record[tk]]
        else:
            tipo="Sem Informação"
        pl="placa"
        if not "placa" in record:
            pl="ID_VEICULO"
        veiculo={
            "Tipo de Veículo":tipo,
            "Placa":record[pl],
            "Idade do condutor":record['idade_condutor'],
            u'Gênero do condutor':GENERO[record['sexo_condutor']],
        }
        _add_local_id(veiculo)
        if "ID_ACIDENT" in record:
            id_a=record["ID_ACIDENT"]
        else:
            id_a=record['id_acidente']
        if not id_a in veiculos:
            veiculos[id_a]=[]
        veiculos[id_a].append(veiculo)
        print("%s de %s"%(n,total_veiculos),end="\r")
n = 0
print("Vítimas                                                                           ")
total_vitimas = 0
for file in glob.glob("./maps/Vitimas*.csv"):
    total_vitimas += file_len(file) - 1
print("%s vítimas.                                                           " % (total_vitimas))

vitimas = {}
for file in glob.glob("./maps/Vitimas*.csv"):
    for record in extract(file, "\t"):
        n+=1
        record = dict((k.lower(), v) for k, v in record.items())
        tipo = "Sem Informação"
        if record['tipo_vitima'] in TIPOS_VITIMA:
            tipo = TIPOS_VITIMA[record['tipo_vitima']]
        classificacao = "Ileso"
        if record['classificacao'] in CLASS_VITIMA:
            classificacao = CLASS_VITIMA[record['classificacao']]

        vitima = {
            u'Idade': record['idade'],
            u'Gênero': GENERO[record['sexo']],
            u'Condição': classificacao,
            u'Tipo de vítima': tipo,
            u'veiculo_id': record['id_veiculo'],
        }
        _add_local_id(vitima)
        if not record['id_acidente'] in vitimas:
            vitimas[record['id_acidente']] = []
        vitimas[record['id_acidente']].append(vitima)
        print("%s de %s" % (n, total_vitimas), end='\r')
print("Inserindo dados")
next=URL+"/api/records/?format=json"
n=0
while next is not None:
    j_inc=client.get(next).json()
    for incident in j_inc["results"]:
        n+=1
        condutores=0
        pedestres=0
        passageiros=0
        incident['data']['driverVehicle'] = veiculos[incident['data']['driverIncidentDetails']['acidente_id'].upper()]
        for vitima in vitimas[incident['data']['driverIncidentDetails']['acidente_id'].upper()]:
            try:
                vitima[u'Veículo']=incident['data']['driverVehicle'][int(vitima['veiculo_id'])-1]['_localId']
            except:
                pass
            vitima.pop('veiculo_id',None)
            if vitima[u'Condição']=="Morta":
                incident["data"]["driverIncidentDetails"]["Severidade"]="Fatal"


        incident['data']['driverPerson'] = vitimas[incident['data']['driverIncidentDetails']['acidente_id'].upper()]
        response = client.patch(URL + '/api/records/' + incident['uuid'] + "/?archived=False",
                                json=incident,
                                headers={'Content-type': 'application/json', "X-CSRFToken": csrf,
                                         "Referer": URL + "/api/recordtypes/?active=True&format=json"},
                                cookies=cookies, )
        print("Incidentes: %s de %s (%s)"%(n,j_inc['count'],incident['uuid']), end='\r')
        next=j_inc["next"]

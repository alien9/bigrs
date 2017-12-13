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
CLASSIFICACAO={
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

print("Encontrados %s incidentes na base. Carregando vítimas..."%(j_inc['count']))
n=0
print("Vítimas")
total_vitimas=0
for file in glob.glob("./maps/Vitimas*.csv"):
    total_vitimas+=file_len(file)-1
vitimas={}
for file in glob.glob("./maps/Vitimas*.csv"):
    for record in extract(file, "\t"):
        n+=1
        record=dict((k.lower(), v) for k,v in record.items())
        tipo="Sem Informação"
        if record['tipo_vitima'] in TIPOS_VITIMA:
            tipo = TIPOS_VITIMA[record['tipo_vitima']]
        classificacao="Ileso"
        if record['classificacao'] in CLASS_VITIMA:
            classificacao = CLASS_VITIMA[record['classificacao']]


        vitima={
            u'Idade':record['idade'],
            u'Gênero':GENERO[record['sexo']],
            u'Condição':classificacao,
            u'Tipo de vítima':tipo,
            u'veiculo_id':record['id_veiculo'],
            u'acidente_id':record['id_acidente'],
        }
        _add_local_id(vitima)
        if not record['id_acidente'] in vitimas:
            vitimas[record['id_acidente']]=[]
        vitimas[record['id_acidente']].append(vitima)
        print("\r%s de %s"%(n,total_vitimas), end='\r')
exit()
n=0
next=URL+"/api/records/?format=json"

while next is not None:
    j_inc=client.get(URL+"/api/records/?format=json").json()
    for incident in j_inc["results"]:
        n+=1
        incident['data']['driverVehicle']=veiculos[incident['data']['driverIncidentDetails']['acidente_id']]
        response = client.patch(URL + '/api/records/' + incident['uuid'] + "/?archived=False",
                                json=incident,
                                headers={'Content-type': 'application/json', "X-CSRFToken": csrf,
                                         "Referer": URL + "/api/recordtypes/?active=True&format=json"},
                                cookies=cookies, )
        print("\rIncidente: %s de %s (%s)"%(n,j_inc['count'],incident['uuid'])),
        next=j_inc["next"]
exit()

for key in veiculos:
    r = client.get(
        URL + "/api/records/?jsonb={%22driverIncidentDetails%22:{%22acidente_id%22:{%22_rule_type%22:%22containment%22,%22contains%22:[%22" +
        key + "%22]}}}")
    j = r.json()
    if int(j['count']) == 1:
        print("\rIncidente %s"%(key)),
exit()
print("Vítimas")
for file in glob.glob("./maps/Vitimas*.csv"):
    for record in extract(file, "\t"):
        n+=1
        #if n > 40:
        #    break
        print(record)
        r = client.get(
            URL + "/api/records/?jsonb={%22driverIncidentDetails%22:{%22acidente_id%22:{%22_rule_type%22:%22containment%22,%22contains%22:[%22" +
            record['id_acidente'] + "%22]}}}")
        j = r.json()
        if int(j['count']) == 1:
            print("ENCONTRADA")
            incident=j['results'][0]
            print(incident)
            if not 'driverPerson' in incident['data']:
                incident['data']['driverPerson']=[]
            tipo="Sem Informação"
            if record['tipo_vitima'] in TIPOS_VITIMA:
                tipo=TIPOS_VITIMA[record['tipo_vitima']]
            condicao="Ileso"
            if record["classificacao"] in CLASSIFICACAO:
                condicao=CLASSIFICACAO[record["classificacao"]]
            veiculo=None
            if 'id_veiculo' in record:
                if len(record['id_veiculo']) > 0:
                    vid=int(record['id_veiculo'])-1
                    if len(incident['data']['driverVehicle']) > vid:
                        veiculo=incident['data']['driverVehicle'][vid]['_localId']
                        print("O veículo é %s"%(veiculo,))
            person={
                "Tipo de vítima":tipo,
                "Veículo":veiculo,
                "Idade":record["idade"],
                "Gênero":record['sexo'],
                "Condição":condicao,
            }
            _add_local_id(person)
            incident['data']['driverPerson'].append(person)
            print(person)
            response = client.patch(URL + '/api/records/'+incident['uuid']+"/?archived=False",
               json=incident,
               headers={'Content-type': 'application/json',  "X-CSRFToken":csrf, "Referer": URL+"/api/recordtypes/?active=True&format=json"},
               cookies=cookies,)
            print(response)

"""

CD - Condutor
PS - Passageiro
PD - Pedestre
OU - Outros
SI - Sem Informação

{'id_acidente': 'D011000033',
 'classificacao': 'F',
 'estado_alcoolizacao': 'BR',
 'data': '          ',
 'escolaridade': '8',
 'tipo_veiculo': 'AU',
 'tipo_vitima': 'PD',
 'sexo': 'M',
 'idade': 'SI',
 'id_veiculo': '01',
 'id_vitima': '001'}

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

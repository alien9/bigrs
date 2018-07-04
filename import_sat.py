#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
from config import *
conn = psycopg2.connect(cstring)

import re, requests, getpass, csv, json, uuid, glob
from dateutil import parser
from dateutil.tz import gettz
import pytz #,ogr
from carrega_csv import *

with open("maps/written") as f:
    existent = f.read().splitlines()

tz1 = gettz('America/Sao_Paulo')

SEXOS={
    "M":"Masculino","F":"Feminino"
}

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
    "QM":"Queda moto",
    "QB":"Queda bicicleta",
    "QV":"Queda veículo",
    "QD":"Queda ocupante dentro",
    "QF":"Queda ocupante fora",
    "OU":"Outros",
    "SI":"Sem informações",
}
TIPOS_RESUMIDOS_COLISAO={
    "CO":"Colisão",
    "CF":"Colisão",
    "CT":"Colisão",
    "CL":"Colisão",
    "CV":"Colisão",
    "CP":"Capotamento",
    "TB":"Capotamento",
    "AT":"Atropelamento",
    "AA":"Atropelamento",
    "CH":"Choque",
    "QM":"Queda",
    "QB":"Queda",
    "QV":"Queda",
    "QD":"Queda",
    "QF":"Queda",
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
TIPOS_VEICULO_RESUMIDO={
    "AU":"Automóvel",
    "MO":"Motocicleta",
    "ON":"Ônibus",
    "CA":"Caminhão",
    "BI":"Bicicleta",
    "MT":"Motocicleta",
    "OF":"Ônibus",
    "OU":"Ônibus",
    "MC":"Ônibus",
    "VA":"Automóvel",
    "VC":"Caminhão",
    "CM":"Automóvel",
    "CR":"Caminhão",
    "JI":"Automóvel",
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
    "SI": "Sem Informação",
}
CLASSIFICACAO={
    "F":"Grave",
    "M":"Fatal",
}
#url=input("URL:[https://motorista.alien9.net]")
#url="http://192.168.0.100:3001" #
url="https://vidasegura.prefeitura.sp.gov.br"
#if url=="":
#url="https://motorista.alien9.net"
username="admin" #input("Usuário:")
password="7zGDwj0kIPTXnEi9Tq-WzyHb1Jccdnq9_GgznEVgWwU" #getpass.getpass("Senha:")
#username="admin"
#password="admin"


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
r=client.get(URL+"/api-auth/login/?next=/api/", verify=False)
csrf=r.cookies.get('csrftoken')
cookies=r.cookies
print("até aqui ok")
r=client.post(URL+"/api-auth/login/", data={"username":username,"password":password,"csrfmiddlewaretoken":csrf,"next":"/api/"},cookies=r.cookies,headers={"referer":URL+"/api-auth/login/?next=/api/"},verify=False)
r=client.get(URL+"/api/recordtypes/?active=True&format=json",cookies=r.cookies,headers={"referer":URL+"/api/"})
j=r.json()
r=client.get(URL+"/api/recordschemas/%s/"%(j['results'][0]["current_schema"]),cookies=r.cookies,headers={"referer":URL+"/api/recordtypes/?active=True&format=json"})
j=r.json()

n=0
print()

for filename in glob.glob("SAT/incidentes.csv"):
    for record in extract(filename,'\t'):
        print(record)
        ano=1984
        n+=1
        if record['id_acident'] in existent:
            print("ja tem %s"%(record['id_acident'],))

        else:
            #if n>20:
            #    break
            if "data_e_hora" in record:
                    stringdate = record['data_e_hora']
            else:
                if len(record['data'])>10:
                    record['data'],nada=record['data'].split(' ')
                ano, mes , dia = record['data'].split('/')
                if int(dia)>int(ano):
                    d=ano
                    ano=dia
                    dia=d
                if re.match("\d+:\d+",record['hora']):
                    hora, minuto= record['hora'].split(':')
                else:
                    if len(record['hora'])>8:
                        nada,hora=record['hora'].split(' ')
                        hora,minuto,segundo=hora.split(':')
                        print(hora+"::"+minuto)
                    else:
                        while len(record['hora'])<4:
                            record['hora']='0'+record['hora']
                        a, hora, minuto, b = re.split('^(\d+)(\d{2})',record['hora'])
                stringdate="%s-%s-%s %s:%s:00"%(ano,mes,dia,hora,minuto)
            occurred_date = pytz.timezone('America/Sao_Paulo').localize(parser.parse(stringdate))

            tipo=None
            if not 'tipo_acide' in record:
                record['tipo_acide']=record['tipo_acidente']
            if record['tipo_acide'] in TIPOS_COLISAO:
                tipo=TIPOS_COLISAO[record['tipo_acide']]
            tipo_resumido=None
            if record['tipo_acide'] in TIPOS_RESUMIDOS_COLISAO:
                tipo_resumido = TIPOS_RESUMIDOS_COLISAO[record['tipo_acide']]
            """
            if not 'mortos' in record:
                a,f,m,b=re.split('^(\d+)(\d{2})',record['vitimas'])
                record['mortos']=m
                record['feridos']=f
            """
            #num_vitimas=int(record['mortos'])+int(record['feridos'])
            #print(num_vitimas)
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
            #if "veiculos" in record:
            #    num_veiculos=sum([int(n) for n in list(record["veiculos"])])
            num_veiculos=0
            #"[{'placa': 'EHP0938', 'tipo_veiculo': 'MO', 'sexo_condutor': 'M', 'id_acidente': 'D011600179', 'idade_condutor': '36', 'categoria_habilitacao': 'SI', 'escolaridade': '8', 'estado_alcoolizacao': 'BR', 'id_veiculo': '1', 'usa_cinto_seguranca': 'X'}, {'placa': 'FKE8500', 'tipo_veiculo': 'AU', 'sexo_condutor': 'M', 'id_acidente': 'D011600179', 'idade_condutor': '36', 'categoria_habilitacao': 'SI', 'escolaridade': '8', 'estado_alcoolizacao': 'BR', 'id_veiculo': '2', 'usa_cinto_seguranca': 'X'}]
            vei=[]
            veiculos_ids={}
            casualties={
                "mortos":0,
                "feridos":0
            }
            if record['id_acident'] in veiculos:
                for v in veiculos[record['id_acident']]:
                    print("veiculo")
                    print(v)
                    tv_res=None
                    if v['tipo_veiculo'] in TIPOS_VEICULO_RESUMIDO:
                        tv_res=TIPOS_VEICULO_RESUMIDO[v['tipo_veiculo']]
                    veiculo = {
                        'Placa': v['placa'],
                        'Tipo de Veículo':tv_res,
                        'Veículo':TIPOS_VEICULO[v['tipo_veiculo']]
                    }
                    _add_local_id(veiculo)
                    if re.match("\\d+",v['id_veiculo']):
                        veiculos_ids[str(int(v['id_veiculo']))]=veiculo
                    vei.append(veiculo)
                    num_veiculos+=1
            vit=[]
            if record['id_acident'] in vitimas:
                for v in vitimas[record['id_acident']]:
                    print(v)
                    condicao='Ferido'
                    if v['classificacao']=='M':
                        condicao='Morto'
                        casualties["mortos"]+=1
                    else:
                        casualties["feridos"]+=1
                    tipo_vitima='Condutor'
                    if v['tipo_vitima'] == 'CD':
                        tipo_vitima = 'Condutor'
                    if v['tipo_vitima'] == 'PS':
                        tipo_vitima = 'Passageiro'
                    if v['tipo_vitima'] == 'PD':
                        tipo_vitima = 'Pedestre'
                    sexo="Sem Informação"
                    if v['sexo']=="F":
                        sexo="Feminino"
                    if v["sexo"]=="M":
                        sexo="Masculino"

                    vitima={
                        'Idade':v['idade'],
                        'Gênero':sexo,
                        'Condição':condicao,
                        'Tipo de Vítima':tipo_vitima
                    }
                    if re.match("\\d+",v['id_veiculo']):
                        if str(int(v['id_veiculo'])) in veiculos_ids:
                            print("Veiculo da vitima")
                            print(veiculos_ids[str(int(v['id_veiculo']))])
                            vitima['Veículo']=veiculos_ids[str(int(v['id_veiculo']))]['_localId']
                            print(vitima)

                    _add_local_id(vitima)
                    vit.append(vitima)
            if int(casualties['mortos']) > 0:
                severidade="Vítimas Fatais"
            else:
                if int(casualties['feridos']) > 0:
                    severidade="Vítimas Feridas"
                else:
                    severidade="Danos Materiais"
 #           try:
  #          if(float(record['x']))!=0:
            obj = {
                'data': {
                    'driverIncidenteDetails': {
                        "Acidente":tipo,
                        "Tipo de Acidente":tipo_resumido,
                        "acidente_id":record['id_acident'],
                        "Severidade": severidade,
                        "Veículos": num_veiculos,
                        "Vítimas": casualties['mortos']+casualties['feridos'],
                        "Mortos": casualties["mortos"],
                        "Feridos":casualties["feridos"]
                    },
                    'driverVíTima': vit,
                    'driverVeíCulo': vei
                },
                'schema': str(r.json()['uuid']),
                'occurred_from': occurred_date.isoformat(),
                'occurred_to': occurred_date.isoformat(),
            }
            try:
                obj["geom"]="SRID=4326;POINT(%s %s)" % (float(record['x']), float(record['y']),)
                cur = conn.cursor()
                print(cur.mogrify(
                    "select get_logradouro_nome((select gid from sirgas_shp_logradouro order by geom <-> st_transform(geomfromewkt(%s), 31983) limit 1))",
                    ("SRID=4326; POINT(" + record['x'] + " " + record['y'] + ")",)))
                cur.execute(
                    "select get_logradouro_nome((select gid from sirgas_shp_logradouro order by geom <-> st_transform(geomfromewkt(%s), 31983) limit 1))",
                    ("SRID=4326; POINT(" + record['x'] + " " + record['y'] + ")",))
                fu = cur.fetchone()
                obj['data']['driverIncidenteDetails']["Endereço"] = fu[0]
                print(fu)
                cur.close()
            except:
                print("sem geometria")
                obj["geom"]="SRID=4326;POINT(%s %s)" % ("0", "0",)
            _add_local_id(obj['data']['driverIncidenteDetails'])
            print(obj)

            if int(ano) > 2014:
                response = client.post(URL + '/api/records/',
                                       json=obj,
                                       headers={'Content-type': 'application/json', "X-CSRFToken": csrf,
                                                "Referer": URL + "/api/recordtypes/?active=True&format=json"},
                                       cookies=cookies,
                                       verify=False
                                       )
                print(response)
                print(response.status_code)
                if response.status_code == 201:
                    fu = open('maps/written', "a")
                    fu.write(record['id_acident'] + "\n")
                    fu.close()


#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re, requests, getpass, csv, json, uuid, datetime
from dateutil import parser
from dateutil.tz import gettz
import pytz #,ogr


#url=input("URL:[https://motorista.alien9.net]")
#url="http://192.168.0.100:3001" #
url="https://vidasegura.prefeitura.sp.gov.br"
#url = 'http://localhost:3001'
#if url=="":
#url="https://motorista.alien9.net"
#username=input("Usuário:")
#password=getpass.getpass("Senha:")
username="admin"
password=getpass.getpass("Senha:")


def extract(csv_path, delimiter=',', quotechar='"'):
    """Simply pulls rows into a DictReader"""
    with open(csv_path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter, quotechar=quotechar)
        for row in reader:
            yield row

def _add_local_id(dictionary):
    dictionary['_localId'] = str(uuid.uuid4())

client=requests.session()
URL=url #"https://driver.alien9.net"
r=client.get(URL+"/api-auth/login/?next=/api/", verify=False)
csrf=r.cookies.get('csrftoken')
cookies=r.cookies
print("até aqui ok")
r=client.post(URL+"/api-auth/login/", data={"username":username,"password":password,"csrfmiddlewaretoken":csrf,"next":"/api/"},cookies=r.cookies,headers={"referer":URL+"/api-auth/login/?next=/api/"},verify=False)
r=client.get(URL+"/api/recordtypes/?active=True&format=json",cookies=r.cookies,headers={"referer":URL+"/api/"})
j=r.json()
for res in j['results']:
    if re.match('Fisca.*', res['label']):
        data_type = res
if not data_type:
    print("data type not found")
    exit()
r=client.get(URL+"/api/recordschemas/%s/"%(data_type["current_schema"]),cookies=r.cookies,headers={"referer":URL+"/api/recordtypes/?active=True&format=json"})
j=r.json()

for c in extract('radar/radares.csv'):
    ano, mes, dia = re.split('\D', re.sub('^\D*|\D$','',c['data de publicação ']))
    stringdate="%s-%s-%s %s:%s:00"%(ano,mes,dia,0,0)
    print(stringdate)
    occurred_date = pytz.timezone('America/Sao_Paulo').localize(parser.parse(stringdate))
    if len(c['data de desativação']) > 0:
        ano, mes, dia = re.split('\D', re.sub('^\D*|\D$', '', c['data de desativação']))
        stringdate = "%s-%s-%s %s:%s:00" % (ano, mes, dia, 0, 0)
        finish_date = pytz.timezone('America/Sao_Paulo').localize(parser.parse(stringdate))
        print(finish_date)
    else:
        finish_date = pytz.timezone('America/Sao_Paulo').localize(parser.parse(stringdate)) + datetime.timedelta(days=36525)
    if re.match('.*,.*', c['lat. Log.']):
        xc = re.split('\s*,\s*', c['lat. Log.'])
        lat = xc[0]
        lng = xc[1]
    else:
        xc = re.split('\s+', c['lat. Log.'])
        lng = xc[0]
        lat = xc[1]

    g = "SRID=4326;POINT(%s %s)" % (lng, lat, )
    print(g)
    obj = {
        'data': {
            "driverIntervencaoDetails": {
                "Endereço": "%s %s" % (c['Endereço'], c['Referência'], ),
                "Tipo": c['tipo']
            },
        },
        "location_text": c['Endereço'],
        'schema': str(j['uuid']),
        'occurred_from': occurred_date.isoformat(),
        'occurred_to': finish_date.isoformat(),
        'geom': g,
    }
    _add_local_id(obj['data']['driverIntervencaoDetails'])
    print(c)
    print(obj)

    response = client.post(URL + '/api/records/',
                                           json=obj,
                                           headers={'Content-type': 'application/json', "X-CSRFToken": csrf,
                                                    "Referer": URL + "/api/recordtypes/?active=True&format=json"},
                                           cookies=cookies,
                                           verify=False
                                           )
    print(response.status_code)
    print(response.content)


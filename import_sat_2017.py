#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2,re
from extract import extract
n=0

try:
    conn = psycopg2.connect("dbname='bigrs' user='bigrs' host='localhost' password='bigrs'")
    cur=conn.cursor()
except:
    print("I am unable to connect to the database")

"""
ruim=cur.execute("select id_acident from incidentes where date_part('year', data_e_hora)=2017")
for r in cur.fetchall():
    gid=str(r[0])
    print(gid)
    cur.execute("delete from incidentes where id_acident=%s",(gid,))
    cur.execute("delete from veiculos where id_acidente=%s", (gid,))
    cur.execute("delete from vitimas where id_acidente=%s", (gid,))
conn.commit()
exit()
"""
for record in extract("./maps/incidentes_2017.csv"):
    print(record)
    n+=1
    dias=re.split("[\s/]",re.sub("\s\d+:\d+:\d+","",record['data']))
    if len(dias)>=3:
        data="%s-%s-%s"%(dias[0],dias[1],dias[2],)
        hora=re.sub("\d+\/\d+\/\d+\s","",record['hora'])
        dataehora="%s %s"%(data,hora)
    else:
        data=""
        dataehora=""
    print(dataehora)
    #feridos,mortos=[int(x) for x in [record['vitimas'][:2],record['vitimas'][2:]]]

    q=cur.mogrify("INSERT INTO public.incidentes(cadlog, "\
      "id_acident, cadloga, cadlogb, alt_num, referencia, "\
      "data, hora, cod_acid, fonte, viatura, dp, talao, sentido, "\
      "pista, veiculos, vitimas, \"dec\", "\
      "distrito, folha, princ_a, princ_b, placa1, tipo_plac1, placa2,"\
      " tipo_plac2, placa3, tipo_plac3, tipo_acide, dia, geom, codigo, veic,"\
      " data_e_hora, mortos, feridos, total_vitimas, lg_gid, data_e_hora_text)"\
      " VALUES "
      "("
      "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
      "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
      "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,geomfromewkt(%s),"
      "%s,%s,%s,%s,%s,%s,%s,%s"
      ")",
        (
            record['cadloga'],
            record['id_acidente'],
            record['cadloga'],
            record['cadlogb'],
            record['alt_num'],
            record['referencia'],
            record['data'],
            record['hora'][:4],
            record['cod_acid'],
            record['fonte'],
            record['viatura'],
            record['dp'],
            record['talao'],
            record['sentido'],
            record['pista'],
            None,
            None,
            record['dec'],
            record['distrito'],
            record['folha'],
            record['princ_a'],
            record['princ_b'],
            record['placa1'],
            record['tipo_placa1'],
            record['placa2'],
            record['tipo_plac2'],
            record['placa3'],
            record['tipo_plac3'],
            record['tipo_acidente'],
            None,
            'SRID=4326;POINT(%s %s 0 0)'%(record['X'],record['Y'],),
            record['cod_acid'],
            None,
            dataehora,
            record['mortos'],
            record['feridos'],
            int(record['mortos'])+int(record['feridos']),
            None,
            dataehora,
        )
    )
    print(q)
    cur.execute(q)

"""
{'FONTE': 'D', 'HORA': '0406', 'PLACA2': 'BPI6402', 'TIPO_PLAC1': 'AU', 'CADLOGA': '18209', 'PLACA3': '', 'FOLHA': '',
'PRINC_A': '18209', 'PLACA1': 'EJH2502', 'ALT_NUM': '177', 'TALAO': '8943', 'SENTIDO': '', 'DP': '63', 'DISTRITO': '53',
'DATA': '2017/10/30 00:00:00.000', 'VEICULOS': '10000000000000000', 'Y': '7401197.63764732', 'TIPO_PLAC3': '', 'CADLOGB': '',
'TIPO_ACIDE': 'CH', 'COD_ACID': '2', 'ID_ACIDENT': 'D101703312', 'REFERENCIA': '', 'MI_PRINX': '0', 'VIATURA': '', 'PRINC_B': '',
'X': '351296.363699566', 'PISTA': '', 'DEC': 'LE1', 'VITIMAS': '0100', 'TIPO_PLAC2': 'AU'}


"""

"""
{'ID_ACIDENT': 'D011700001', 'IDADE_COND': '33', 'CATEGORIA_': 'SI', 'ESTADO_ALC': 'BR',
'PLACA': 'ECS5538', 'TIPO_VEICU': 'MO', 'cod_acid': '4', 'SEXO_CONDU': 'M', 'ESCOLARIDA': '5',
 'ID_VEICULO': '1', 'USA_CINTO_': 'X', 'tipo_acidente': 'AT'}

"""

for record in extract("./maps/Veiculos2017.csv"):
    print(record)
    if not re.match("\d+",record['IDADE_COND']):
        record['IDADE_COND']=None
    q=cur.mogrify("INSERT INTO public.veiculos("\
        "id_veiculo, id_acidente, tipo_veiculo, sexo_condutor, idade_condutor,"\
        "categoria, usa_cinto, est_alcool, escolaridade, placa)"\
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",(
            record['ID_VEICULO'],
            record['ID_ACIDENT'],
            record['TIPO_VEICU'],
            record['SEXO_CONDU'],
            record['IDADE_COND'],
            record['CATEGORIA_'],
            record['USA_CINTO_'],
            record['ESTADO_ALC'],
            record['ESCOLARIDA'],
            record['PLACA'],
    ))
    print(q)
    cur.execute(q)
"""
{'id_veiculo': '2', 'estado_alcoolizacao': 'BR', 'escolaridade': '8', 'placa': '       ',
 'idade_condutor': 'SI', 'tipo_veiculo': 'AU', 'id_acidente': 'D091704137',
  'usa_cinto_seguranca': 'X', 'sexo_condutor': 'X', 'categoria_habilitacao': 'SI'}

{'tipo_acidente': 'AT', 'ESTADO_ALC': 'BR', 'MES_ACID': 'JANEIRO', 'ESCOLARIDA': '4', 'ID_VITIMA': '1',
 'ID_ACIDENT': 'D011700001', 'ID_VEICULO': '1', 'TIPO_USUÁR': 'PE', 'DATA_OBITO': 'NULL', 'SEXO': 'F', 'CLASSIFICA': 'F',
 'IDADE': '19', 'cod_acid': '4', 'TIPO_VEICU': 'MO', 'TIPO_VITIM': 'PD'}


"""
for record in extract("./SAT/vitimas.csv"):
    print(record)
    dias=re.split("\s|\/",record['DATA_OBITO'])
    data_obito=None
    if len(dias)>=3:
        data_obito="%s-%s-%s"%(dias[2],dias[1],dias[0],)
    if not re.match("\d+",record['IDADE']):
        record['IDADE']=None
    q=cur.mogrify("INSERT INTO public.vitimas("\
        "id_vitima, id_acidente, id_veiculo, sexo, idade, fx_etaria,"\
        "tipo_vitima, classifica, tipo_veicu, est_alcool, escolaridade, data_obito"\
        ")"\
        "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",(
            record['ID_VITIMA'],
            record['ID_ACIDENT'],
            record['ID_VEICULO'],
            record['SEXO'],
            record['IDADE'],
            None,
            record['TIPO_VITIM'],
            record['CLASSIFICA'],
            record['TIPO_VEICU'],
            record['ESTADO_ALC'],
            record['ESCOLARIDA'],
            data_obito,
    ))
    print(q)
    cur.execute(q)
conn.commit()

"""
{'escolaridade': '5', 'idade': '34', 'tipo_veiculo': 'MO', 'id_veiculo': '1', 'sexo': 'M', 'data_obito': 'NULL',
 'tipo_vitima': 'CD', 'id_acidente': 'D091704101', 'classificacao': 'F', 'estado_alcoolizacao': 'BR', 'id_vitima': '1'}

"""
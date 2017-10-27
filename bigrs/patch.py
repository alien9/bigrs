#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import walk,listdir,environ
import django,re

environ.setdefault("DJANGO_SETTINGS_MODULE", "bigrs.settings")
django.setup()
from maps.models import *
from sys import argv
from datetime import datetime,timedelta
import ffmpy
import re,glob,os,sys

root='static/video/'
if len(sys.argv)>1:
    root=sys.argv[1]
print(root)

contage_name=input('Selecione o ponto de contagem:\n')
contagens=Contagem.objects.filter(endereco__icontains=contage_name).order_by('endereco')
if not len(contagens):
    print("Contagem não Encontrada.\n")
    exit()
i=1
print("Selecione:")
for cu in contagens:
    print("[%s] %s\n"%(i,cu.endereco))
    i+=1
selected=None
while not selected:
    try:
        selected=contagens[int(input("Escolha um número: "))-1]
    except ValueError:
        pass
    except IndexError:
        pass

print("Escolheu o %s"%(selected.endereco))
c=selected
i=1
l=listdir(root)
l.sort()
for directory in l:
    print("[%s] %s"%(i,directory))
    i+=1
dest=None
while not dest:
    try:
        dest=l[int(input("Escolha o diretório para importar:"))-1]
    except ValueError:
        pass
    except IndexError:
        pass
print("Escolhido %s"%(dest))
horarios=(
    (6, 0),
    (6, 15),
    (6, 30),
    (6, 45),
    (7, 0),
    (7, 15),
    (7, 30),
    (7, 45),
    (8, 0),
    (8, 15),
    (8, 30),
    (8, 45),
    (9, 0),
    (12, 0),
    (12, 15),
    (12, 30),
    (12, 45),
    (13, 0),
    (13, 15),
    (13, 30),
    (13, 45),
    (14, 0),
    (16, 0),
    (16, 15),
    (16, 30),
    (16, 45),
    (17, 0),
    (17, 15),
    (17, 30),
    (17, 45),
    (18, 0),
    (18, 15),
    (18, 30),
    (18, 45),
    (19, 0),
)
horarios_limpos=(
    (6, 0),
    (6, 15),
    (6, 30),
    (6, 45),
    (7, 0),
    (7, 15),
    (7, 30),
    (7, 45),
    (8, 0),
    (8, 15),
    (8, 30),
    (8, 45),
    (12, 0),
    (12, 15),
    (12, 30),
    (12, 45),
    (13, 0),
    (13, 15),
    (13, 30),
    (13, 45),
    (16, 0),
    (16, 15),
    (16, 30),
    (16, 45),
    (17, 0),
    (17, 15),
    (17, 30),
    (17, 45),
    (18, 0),
    (18, 15),
    (18, 30),
    (18, 45),
)
da=None
while not da:
    try:
        ano=int(input("Ano:"))
        mes=int(input("Mês:"))
        dia=int(input("Dia:"))

        da=datetime(ano,
                    mes,
                    dia,
                    6,0,0)
    except ValueError:
        pass
pa=root+dest
l=listdir(pa)
l.sort()

"""
for f in l:
    print(f)
    if re.search('mp4$',f):
        destino=pa+'/' + f
        print(destino)
        m = Movie(contagem=c, movie=destino, data_e_hora_inicio=da) #.strftime('%Y-%m-%d %H:%M:%S'))
        m.save()
    da=da+timedelta(minutes=15)
"""
def cria(files, dia, mes, ano, contagem):
    i=0
    if contagem is None:
        print("Sem contagem não pode.")
        return
    for filename in files:
        arquivo_residual=os.stat(pa+'/'+filename).st_size < 999999
        if horarios[i][0]==14 or horarios[i][0]==9: #ferifique se é mesmo residual
            if not arquivo_residual:
                i+=1
        da=datetime(ano,mes,dia,horarios[i][0],horarios[i][1])
        print("criando movie para %s"%(filename))
        m = Movie(contagem=contagem, movie=pa+'/'+filename, data_e_hora_inicio=da)
        m.save()
        i+=1
cria(l,dia,mes,ano,c)
def conserta_horarios(movies, dia, mes, ano):
    i=0
    for m in movies:
        arquivo_residual=os.stat(m.movie.url).st_size < 999999
        if horarios[i][0]==14 or horarios[i][0]==9: #ferifique se é mesmo residual
            if not arquivo_residual:
                i+=1
        da=datetime(ano,mes,dia,horarios[i][0],horarios[i][1])
        print("File size %s devia ser %s"%(os.stat(m.movie.url).st_size,da.strftime('%Y-%m-%d %H:%M:%S')))
        m.data_e_hora_inicio=da
        m.save()
        i+=1

def cleanup():
    result = [y for x in os.walk(root) for y in glob(os.path.join(x[0], '*.mp4'))]
    movies=[str(m.movie) for m in Movie.objects.all()]
    for f in result:
        if not f in movies:
            print("deletando "+f)
            dir=re.sub('[^/]*$','',f)
            if not os.path.isdir('/home/tiago/temp/'+dir):
                os.makedirs('/home/tiago/temp/'+dir)
            os.rename(f, '/home/tiago/temp/'+f)
result = [os.path.join(dp, f) for dp, dn, filenames in os.walk("/media/tiago/Seagate/LAPA") for f in filenames if os.path.splitext(f)[1] == '.mp4']
result.sort()
bairro=Bairro.objects.last()

def pseudo_import(l):
    i=0
    old_day=99
    for f in l:
        ## /media/tiago/Seagate/LAPA/LA_P7B_2017_05_27/00000114.mp4'"
        s=re.search("LAPA\/LA_([^_]+)_([^_]+)_([^_]+)_([^_]+)\/(.*)",f)
        if s is not None:
            movie=s.group()
            nome_contagem=s.group(1)
            contagens=Contagem.objects.filter(endereco=nome_contagem,bairro=bairro)
            if len(contagens) ==0:
                print("crie contagem %s"%(nome_contagem))
                contagem=Contagem(endereco=nome_contagem,bairro=bairro)
                contagem.save()
            else:
                contagem=contagens[0]

            ano=int(s.group(2))
            mes=int(s.group(3))
            dia=int(s.group(4))
            if dia!=old_day:
                i=0
            old_day=dia
            da=datetime(ano,mes,dia,horarios_limpos[i][0],horarios_limpos[i][1])
            movies=Movie.objects.filter(contagem=contagem, movie=movie, data_e_hora_inicio=da)
            if len(movies)==0:
                print("movie nao ecsiste")
                m = Movie(contagem=contagem, movie=movie, data_e_hora_inicio=da)
                m.save()
            i+=1
            if i==32:
                i=0
            print("movie %s  -  contagem %s"%(movie,nome_contagem,))



    for dir in l:
        print(dir)
        if re.match("^LA_.*"):
            print("este vai")
            files=listdir()


def import_veiculos():
    from openpyxl import load_workbook
    wb = load_workbook('/home/tiago/Downloads/Veiculos_2016_bloom.xlsx')
    line=2
    w=wb['Veiculos_2016']
    while "A%s"%(line,) in w:
        """"
        A id_vitima
        B id_acidente
        C id_veiculo
        D sexo
        E idade
        F tipo_vitima
        G classificacao
        H tipo_veiculo
        I estado_alcoolizacao
        J escolaridade
        K data_obito
        INSERT INTO public.vitimas(
            id, id_vitima, id_acidente, id_veiculo, sexo, idade, fx_etaria,
            tipo_vitima, classifica, tipo_veicu, est_alcool, escolaridade,cd bigr
            data_obito)


        id_veiculo	id_acidente	tipo_veiculo	placa	sexo_condutor	idade_condutor	categoria_habilitacao	usa_cinto_seguranca	estado_alcoolizacao	escolaridade


        """





        query="INSERT INTO public.veiculos(" \
              "id_veiculo, id_acidente, tipo_veiculo, sexo_condutor, idade_condutor, categoria, usa_cinto, est_alcool, escolaridade, placa" \
              ")VALUES(" \
              "'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'" \
              ")"%(
            w['A' + line].value,
            w['A' + line].value,
            w['A' + line].value,
            w['A' + line].value,
            w['A' + line].value,
            w['A' + line].value,
            w['A' + line].value,
            w['A' + line].value,
            w['A' + line].value,
            w['A' + line].value,
            w['A' + line].value,
            w['A' + line].value,
            w['A' + line].value,

        )
        print(query)
        line+=1

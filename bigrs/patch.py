#!/usr/bin/env python
# -*- coding: utf-8 -*-


from maps.models import *
from os import walk,listdir
from sys import argv
from datetime import datetime,timedelta
import ffmpy
import re

if len(argv)>1:
    print('argv')
print(argv)
c=Contagem.objects.last()
f = []
subs='ponto2'
for (dirpath, dirnames, filenames) in walk('static/video/'+subs):
    f.extend(filenames)
    break


c=Contagem.objects.get(pk=22)
dest="ponto2_new"
pa="/media/tiago/Seagate/Pesquisa COUNTcam MINI - Contagem de Pedestres e Veículos com Câmeras/1 - Pesquisa Realizada - São Miguel - 22_03 a 26_03_2017/Ponto 2/P2 26_03_17"
pa="/media/tiago/Seagate/Pesquisa COUNTcam MINI - Contagem de Pedestres e Veículos com Câmeras/3 - Pesquisa Realizada - São Miguel - 05_04 a 09_04_2017/Ponto 1 Chip 3/P1 08_04_17"
pa="/media/tiago/Seagate/Pesquisa COUNTcam MINI - Contagem de Pedestres e Veículos com Câmeras/3 - Pesquisa Realizada - São Miguel - 05_04 a 09_04_2017/Ponto 1 Chip 3/P1 09_04_17"
pa="/media/tiago/Seagate/Pesquisa COUNTcam MINI - Contagem de Pedestres e Veículos com Câmeras/1 - Pesquisa Realizada - São Miguel - 22_03 a 26_03_2017/Ponto 3 A/P3A 23_03_17"
pa="/media/tiago/Seagate/Pesquisa COUNTcam MINI - Contagem de Pedestres e Veículos com Câmeras/1 - Pesquisa Realizada - São Miguel - 22_03 a 26_03_2017/Ponto 3 A/P3A 25_03_17"
pa="/media/tiago/Seagate/Pesquisa COUNTcam MINI - Contagem de Pedestres e Veículos com Câmeras/1 - Pesquisa Realizada - São Miguel - 22_03 a 26_03_2017/Ponto 3 A/P3A 26_03_17"

pa="/media/tiago/Seagate/Pesquisa COUNTcam MINI - Contagem de Pedestres e Veículos com Câmeras/4 - Pesquisa Realizada - São Miguel - 03_05 a 07_05_2017/Ponto 3B - Chip 1/"
pa="/media/tiago/Seagate/Pesquisa COUNTcam MINI - Contagem de Pedestres e Veículos com Câmeras/4 - Pesquisa Realizada - São Miguel - 03_05 a 07_05_2017/Ponto 3C - Chip 4/"

da=datetime(2017,3,26,6,0,0)
l=listdir(pa)
l.sort()
for f in l:
    s=da.strftime('%Y_%m_%d_%H_%M_%S')
    print(s)
    destino='static/video/' + dest
    if not os.path.isdir(destino):
        os.makedirs(destino)
    destino+='/'+s+'_'+f.replace('.ASF','.mp4')
    if not os.path.isfile(destino):
        print(destino)
        ff = ffmpy.FFmpeg(
            inputs={pa+'/'+f: None},
            outputs={destino: None}
        )
        ff.run()

        m = Movie(contagem=c, movie=destino, data_e_hora_inicio=da)
        m.data_e_hora_inicio=da
        m.save()
    da=da+timedelta(minutes=15)

pa='static/video/'+dest
l=listdir(pa)
l.sort()
for f in l:
    print(f)
    if re.search('mp4$',f):
        sd=str(f).split("_")
        da=datetime(int(sd[0]), int(sd[1]), int(sd[2]), int(sd[3]), int(sd[4]), int(sd[5][0:2]))
        print(da)
        destino=pa+'/' + f
        print(destino)
        ds=da.strftime('%Y_%m_%d_%H_%M_%S')
        m = Movie(contagem=c, movie=destino, data_e_hora_inicio=da)
        m.data_e_hora_inicio=da
        m.save()

for filename in f:
    sd=str(filename).split("_")
    print(sd)
    da=datetime(int(sd[0]), int(sd[1]), int(sd[2]), int(sd[3]), int(sd[4]), int(sd[5][0:2]))
    print(da)
    ds=da.strftime('%Y_%m_%d_%H_%M_%S')
    m=Movie(contagem=c,data_e_hora_inicio=ds,movie='static/video/'+subs+'/'+str(filename))
    m.save()


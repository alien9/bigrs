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
    print(destino)
    ff = ffmpy.FFmpeg(
        inputs={pa+'/'+f: None},
        outputs={destino: None}
    )
    ff.run()
    da=da+timedelta(minutes=15)
    m = Movie(contagem=c, movie=destino, data_e_hora_inicio=da)
    m.save()

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
        m = Movie(contagem=c, movie=destino, data_e_hora_inicio=da)
        m.save()

for filename in f:
    sd=str(filename).split("_")
    print(sd)
    da=datetime(int(sd[0]), int(sd[1]), int(sd[2]), int(sd[3]), int(sd[4]), int(sd[5][0:2]))
    print(da)
    m=Movie(contagem=c,data_e_hora_inicio=da,movie='static/video/'+subs+'/'+str(filename))
    m.save()


#!/usr/bin/env python
# -*- coding: utf-8 -*-


from maps.models import *
from os import walk
from sys import argv
from datetime import datetime

if len(argv)>1:
    print('argv')
print(argv)
c=Contagem.objects.last()
f = []
subs='ponto4'
for (dirpath, dirnames, filenames) in walk('static/video/'+subs):
    f.extend(filenames)
    break

f=Movie.objects.all()

for filename in f:
    sd=str(filename.movie).split("_")
    print(sd)
    da=datetime(int(sd[0][20:24]), int(sd[1]), int(sd[2]), int(sd[3]), int(sd[4]), int(sd[5][0:2]))
    print(da)
    filename.data_e_hora_inicio=da
    filename.save()
    #m=Movie(contagem=c,data_e_hora_inicio=da,movie='static/video/'+subs+'/'+str(filename))
    #m.save()


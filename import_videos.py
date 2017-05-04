#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os,time,ffmpy
from os import walk

if len(sys.argv)==3:
    path=sys.argv[1]
    dest=sys.argv[2]
else:
    path='.'
    dest='.'

os.makedirs(dest)
def itera(p):
    for (dirpath, dirnames, filenames) in walk(p):
        for dir in dirnames:
            print(dir)
            itera(dir)
        for f in filenames:
            print((dirpath+'/'+f).replace(' ','\ '))
            print(os.path.isfile((dirpath+'/'+f)))
            mtime = os.path.getctime((dirpath+'/'+f))
            print(mtime)

            s=time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(mtime))
            print(s+f.replace('.ASF','.mp4'))

            ff = ffmpy.FFmpeg(
                inputs={dirpath+'/'+f: None},
                outputs={dest+'/'+s+f.replace('.ASF','.mp4'): None}
            )
            ff.run()

itera(path)



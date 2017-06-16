#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ffmpy
import re,glob,os


converts = [val for sublist in [[os.path.join(i[0], j) for j in i[2]] for i in os.walk('static/video')] for val in sublist if re.search("ASF$",val)]
print("Terei que converter %s arquivo(s)"%(len(converts)))
for filename in converts:
    mp4=filename.replace('.ASF','.mp4')
    if os.path.exists(mp4):
        os.remove(mp4)
    print("Convertendo %s para %s"%(filename,mp4))
    ff = ffmpy.FFmpeg(
        inputs={filename: None},
        outputs={mp4: '-crf 28 -strict experimental'}
    )
    ff.run()
    os.remove(filename)

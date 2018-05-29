#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, requests, getpass, csv, json, uuid, glob
from dateutil import parser
from dateutil.tz import gettz
import pytz #,ogr
from csvutils import *
fu=open('maps/written',"a")
for filename in glob.glob("maps/incidente*.csv"):
    for record in extract(filename):
        fu.write(record['id_acident']+"\n")
        if record['id_acident']=='D031000746':
            print("cabo")
            fu.close()
            exit()
        print(record['id_acident'])
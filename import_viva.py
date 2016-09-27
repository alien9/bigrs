import sys,os,re
import csv,codecs

with codecs.open('temp_20160831_VIVA_Inquerito_MicroDado_2011_35.CSV', 'r', 'cp1252') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=';', quotechar='',quoting=csv.QUOTE_NONE)
    for row in spamreader:
        print(";".join(row))


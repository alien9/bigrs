import re
with open("reducoes.csv", 'r', encoding='cp1252') as infile:
    for line in infile:
        words=re.sub("\n|\r$","",line,).split(";")
        print(words)
        print("UPDATE vias_velocidade_alterada set velocidade_antes='%s' where codlog='%s';"%(words[4],words[1].zfill(6),))


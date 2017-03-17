#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs,psycopg2,re,sys

file='/home/tiago/Dropbox/Dados e Cartografias - MobiLab/Mapas/Auxiliares/OD_viagens-a-pe/viagens_ape.csv'
cstring="dbname='bigrs' user='bigrs' host='localhost' port='5432' password='bigrs'"
conn = psycopg2.connect(cstring)
cur = conn.cursor()
"""
if "clean" in sys.argv:
    print("limpando os caminhos absurdos")
    cur.execute("select o_geom,d_geom,id from od where geom is not null")
    r=cur.fetchall()
    for d in r:
    #geocodifica
        cur.execute(
            "select gid,source,target,st_linemerge(geom) from sirgas_shp_logradouro order by geom <-> st_transform(ST_GeomFromWKb(%s::geometry),31983) limit 1",
            (d[0],))
        origem = cur.fetchone()
        cur.execute("select gid,source,target,st_linemerge(geom) from sirgas_shp_logradouro order by geom <-> st_transform(ST_GeomFromWKb(%s::geometry),31983) limit 1",(d[1],))
        destino=cur.fetchone()
        cur.execute("select st_distance(st_geomfromewkb(%s::geometry),st_transform(ST_GeomFromWKb(%s::geometry),31983)),st_distance(st_geomfromewkb(%s::geometry),st_transform(ST_GeomFromWKb(%s::geometry),31983))",(origem[3],d[0],destino[3],d[1]))
        distancia_origem, distancia_destino=cur.fetchone()
        print("oriegem a %s"%(distancia_origem,))
        print("destino a %s"%(distancia_destino,))
        if distancia_origem>100 and distancia_destino>100:
            print("vou deletar este: %s"%(d[2]))
            cur.execute("update od set geom=null where id=%s",(d[2],))
            conn.commit()
    cur.close()
    conn.close()
    exit()

if "reset" in sys.argv:
    cur.execute("delete from od_2007_v2d;")
    f=codecs.open(file, 'rb', 'cp1252')
    i=0
    for line in f.readlines():
        i+=1
        a=line.split(";")
        if re.match("\d+",a[0]):
            origem = "SRID=22523;POINT(%s %s)" % (a[24].replace(",", "."), a[25].replace(",", "."));
            destino = "SRID=22523;POINT(%s %s)" % (a[18].replace(",", "."), a[19].replace(",", "."));
            print(cur.mogrify("insert into od(id,o_geom,d_geom) values(%s,st_transform(geomfromewkt(%s),4326),st_transform(geomfromewkt(%s),4326))", (a[0], origem,destino)))
            cur.execute("insert into od(id,o_geom,d_geom) values(%s,st_transform(geomfromewkt(%s),4326),st_transform(geomfromewkt(%s),4326))", (a[0], origem,destino))
            conn.commit()
    f.close()
"""
query="select o_geom,d_geom,gid from od_2007_v2d where geom is null and o_geom is not null and d_geom is not null"
for a in sys.argv:
    m=re.match("id=(\d+)",a)
    if m:
        query="select o_geom,d_geom,gid from od_2007_v2d where gid=%s"%(m.group(1),)

#insaerção concluida. Fazer geocodificação reversa
cur.execute(query)
r=cur.fetchall()
cursor = conn.cursor()
for d in r:
    print(d)
    #cria pontos
    #cursor.execute("update od_2007_v2d set o_geom=st_transform(st_geomfromewkt('SRID=22523;POINT('||co_o_x||' '||co_o_y||')'),31983),d_geom=st_transform(st_geomfromewkt('SRID=22523;POINT('||co_d_x||' '||co_d_y||')'),31983)")
    #geocodifica
    cursor.execute(
        "select gid,source,target,st_linemerge(geom) from segmento_viario order by geom <-> ST_GeomFromWKb(%s::geometry) limit 1",
        (d[0],))
    origem = cursor.fetchone()
    print(origem)
    cursor.execute("select gid,source,target,st_linemerge(geom) from segmento_viario order by geom <-> ST_GeomFromWKb(%s::geometry) limit 1",(d[1],))
    destino=cursor.fetchone()
    print(destino)
    cursor.execute(
        "select st_distance(st_geomfromewkb(%s::geometry),ST_GeomFromWKb(%s::geometry)),st_distance(st_geomfromewkb(%s::geometry),ST_GeomFromWKb(%s::geometry))",
        (origem[3], d[0], destino[3], d[1]),
    )
    print(cursor.mogrify(
        "select st_distance(st_geomfromewkb(%s::geometry),ST_GeomFromWKb(%s::geometry)),st_distance(st_geomfromewkb(%s::geometry),ST_GeomFromWKb(%s::geometry))",
        (origem[3], d[0], destino[3], d[1]),
    ))

    distancia_origem, distancia_destino=cursor.fetchone()
    print("oriegem a %s"%(distancia_origem,))
    print("destino a %s"%(distancia_destino,))
    if distancia_origem<1000 or distancia_destino<1000:
        print(str(d[2])+": "+str(origem[1])+" to "+str(destino[2]))
        #roteiriza
        cursor.execute(
            "select * from pgr_dijkstra('SELECT gid as id,source, target, st_length(geom) as cost, st_length(geom) as reverse_cost FROM segmento_viario', %s,%s)",
            (origem[1],destino[2],)
        )
        res=cursor.fetchall();
        #junta tudo
        for ru in res:
            print("part")
            if ru[3]>0:
                cursor.execute("insert into od_segmento(segmento_gid,od_gid) VALUES (%s,%s)",(ru[3],d[2],))
            print(ru[3])
            if ru[3]>0 and ru[3]!=origem[0] and ru[3]!=destino[0]:
                print("grande")
                cursor.execute("update od_2007_v2d set geom=case when geom is null then (select geom from segmento_viario where gid=%s) else st_multi(bigrs.joinlinestrings(st_linemerge(geom),(select st_linemerge(geom) from segmento_viario where gid=%s))) end where gid=%s", (ru[3],ru[3],d[2]))
        if len(res) < 3:
            print("cria nova geometria")
            if len(res) < 2:
                print("um unico segmento")
                cursor.execute(
                    "update od_2007_v2d set geom=st_multi(st_transform(ST_GeomFromWKb(%s::geometry),31983)) where gid=%s",
                    (origem[3], d[2],))
            else:
                print("dois segimertnos")
                cursor.execute(
                    "update od_2007_v2d set geom=st_multi(st_union(ST_GeomFromWKb(%s::geometry),ST_GeomFromWKb(%s::geometry))) where gid=%s",
                    (origem[3], destino[3], d[2],))
                cursor.execute(
                    "select st_numgeometries(geom) from od_2007_v2d where gid=%s",
                    (d[2],))
                numge=cursor.fetchone()[0]
                if numge>1:
                    print("mais complexo")
                    cursor.execute("select st_distance(st_pointn(st_geometryn(geom,1),1),st_pointn(st_geometryn(geom,2),1)), st_distance(st_pointn(st_geometryn(geom,1),1),st_pointn(st_geometryn(geom,2),st_numpoints(st_geometryn(geom,2)))) from od_2007_v2d where gid=%s",(d[2],))
                    ds=cursor.fetchone()
                    print(ds)
                    cursor.execute(
                        "update od_2007_v2d set geom=st_multi(bigrs.joinlinestrings(st_geometryn(geom,1), st_geometryn(geom,2))) where gid=%s",
                        (d[2],))
                else:
                    print("resolvido")

            cursor.execute("select st_linelocatepoint(st_linemerge(geom),st_transform(ST_GeomFromWKb(%s::geometry),31983)),st_linelocatepoint(st_linemerge(geom),st_transform(ST_GeomFromWKb(%s::geometry),31983)) from od_2007_v2d where gid=%s",(d[0],d[1],d[2]))
            posicao_inicial,posicao_final=cursor.fetchone()
            print(posicao_inicial)
            print(posicao_final)

            if posicao_inicial<posicao_final:
                cursor.execute(
                    "update od_2007_v2d set geom=st_multi(st_linesubstring(st_linemerge(geom),%s,%s)) where gid=%s",
                    (posicao_inicial,posicao_final, d[2],))
            elif posicao_inicial>posicao_final:
                cursor.execute(
                    "update od_2007_v2d set geom=st_multi(st_linesubstring(st_linemerge(geom),%s,%s)) where gid=%s",
                    (posicao_final, posicao_inicial, d[2],))
            conn.commit()
        else:
            cursor.execute("update od_2007_v2d set geom=st_multi(st_union(geom, "
                           "case when st_distance(geom,st_pointn(%s,1))<st_distance(geom,st_pointn(%s,st_numpoints(%s))) then "
                           " ST_LineSubstring(%s,0,st_linelocatepoint(%s,st_transform(ST_GeomFromWKb(%s::geometry),31983))) "
                           " else "
                           " ST_LineSubstring(%s,st_linelocatepoint(%s,st_transform(ST_GeomFromWKb(%s::geometry),31983)),1) "
                           "end"
                           ")) where gid=%s",
                           (origem[3], origem[3], origem[3], origem[3], origem[3], d[0], origem[3], origem[3], d[0], d[2],))
            cursor.execute("update od_2007_v2d set geom=st_multi(st_union(geom, "
                           "case when st_distance(geom,st_pointn(%s,1))<st_distance(geom,st_pointn(%s,st_numpoints(%s))) then "
                           " ST_LineSubstring(%s,0,st_linelocatepoint(%s,st_transform(ST_GeomFromWKb(%s::geometry),31983))) "
                           " else "
                           " ST_LineSubstring(%s,st_linelocatepoint(%s,st_transform(ST_GeomFromWKb(%s::geometry),31983)),1) "
                           "end"
                           ")) where gid=%s",
                           (destino[3], destino[3], destino[3], destino[3], destino[3], d[1], destino[3], destino[3], d[1],
                            d[2],))
            conn.commit()
conn.commit()
cur.close()
conn.close()




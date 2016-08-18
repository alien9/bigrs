library(RPostgreSQL)
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname="bigrs",host="localhost",port=5433,user="bigrs",password="bigrs")

myTable <- dbReadTable(con, c("tmp","test_tbl"))

rs <- dbSendQuery(con,"select distinct nome,codlog from vias_velocidade_alterada")
m<-dbFetch(rs)
dbClearResult(rs)


# query executada com mapa de velocidades alteradas
rs <- dbSendQuery(con,"select i.data_e_hora,i.mortos,i.feridos,i.cod_acid,i.tipo_acide,i.veiculos from incidentes i join (select bigrs.st_sp_buffer(geom,100) as geom from vias_velocidade_alterada where rua = 'AV PAULISTA') v on st_contains(v.geom,i.geom)='t'")

# query executada com eixos normais
rs <- dbSendQuery(con,"select i.data_e_hora,i.mortos,i.feridos,i.cod_acid,i.tipo_acide,i.veiculos from incidentes i join (select bigrs.st_sp_buffer(geom,100) as geom from sirgas_shp_logradouro where lg_nome='TITO' AND lg_titulo='MAL' AND lg_tipo = 'AV') v on st_contains(v.geom,i.geom)='t'")

m<-dbFetch(rs)
m$week <- as.Date("1970-01-01")+7*trunc(as.numeric(m$data_e_hora)/(3600*24*7))
plot(ddply(m, .(data_e_hora), summarize, mortos=sum(mortos),feridos=sum(feridos)))

plot(aggregate(mortos ~ week, m, sum))

dbClearResult(rs)

dbDisconnect(con)
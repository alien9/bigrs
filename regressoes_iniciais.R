#funcoes para geracao de dummies de mes ano
mestring <- function(x){
  y= c()
  for (i in x)
    if (i<10)
      y=c(y,(paste("0",i,sep="")))
    else
      y = c(y,i)
    
    return(y)
}
mesano <- function(mes,ano){
    return(as.Date(paste(ano,mestring(mes),"01",sep="-",format="%Y-%m-%d")))
}


#install.packages("RPostgreSQL")
library("RPostgreSQL")
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname="bigrs",host="localhost",port=5433,user="bigrs",password="bigrs")

rs <- dbSendQuery(con,"select i.data_e_hora,i.mortos,i.feridos,i.cod_acid,i.tipo_acide, v.data_vigor, v.rua from incidentes i join (select bigrs.st_sp_buffer(geom,100) as geom, data_vigor, rua from vias_velocidade_alterada) v on st_contains(v.geom,i.geom)='t'")
resultados <- dbFetch(rs)
resultados<-cbind(resultados, "mes" = as.numeric(format(resultados$data_e_hora,"%m")), "ano" = as.numeric(format(resultados$data_e_hora,"%Y")), "horas" = as.numeric(format(resultados$data_e_hora,"%H")))

#ds_reg <- cbind(ds_reg, "dum_fer" = (ds_reg$feridos>0), "dum_mor" = (ds_reg$mortos>0))
#ds_reg <-cbind(ds_reg, "intervencao" =(as.Date(ds_reg$data_e_hora)-as.Date(ds_reg$data_vigor))>=0)

agregados <- aggregate(list("mortos"=resultados$mortos, "feridos" = resultados$feridos), by = list("dia_incidente"= as.Date(resultados$data_e_hora), "dia_alteracao" = resultados$data_vigor, "rua" = resultados$rua), FUN = sum)

agregados = cbind(agregados, "intervencao" = (agregados$dia_incidente-agregados$dia_alteracao>=0), "mesano" = mesano(as.numeric(format(agregados$dia_incidente,"%m")), as.numeric(format(agregados$dia_incidente,"%Y"))))

agregados = cbind(agregados, "id" = paste(agregados$dia_alteracao,agregados$rua,sep=""))

agregados = cbind(agregados, "mortos_ou_feridos" = agregados$mortos+ agregados$feridos)

#base restrita às vias que sofreram alteração
agregadosrestrict = agregados[as.numeric(format(agregados$dia_alteracao,"%Y"))>=2015,]

#pacote de modelos para painel
#install.packages("plm")
library('plm')


#modelo 0: controle por dummies mensais
modelo0<- lm(mortos_ou_feridos~intervencao+factor(mesano), data=agregadosrestrict)

#modelo1: controle por efeito fixo na via e dummies mensais
modelo1<- lm(mortos_ou_feridos~intervencao+factor(rua)+factor(mesano), data=agregadosrestrict)


#resultado sem var robusta a autocorr
summary(modelo0)
summary(modelo1)

#resultados com var robusta a autocorr
coefs0 <- coeftest(modelo0,vcov=vcovHC(modelo0,type = "HC0", cluster="rua",adjust=T))
coefs1 <- coeftest(modelo1,vcov=vcovHC(modelo1,type = "HC0", cluster="rua",adjust=T))



dbClearResult(rs)

dbDisconnect(con)

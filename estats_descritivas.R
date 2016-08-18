#install.packages("RPostgreSQL")
mestring <- function(x){
  y= c()
  for (i in x)
    if (i<10)
      y=c(y,(paste("0",i,sep="")))
    else
      y = c(y,i)
  
  return(y)
}

library("RPostgreSQL")
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname="bigrs",host="localhost",port=5433,user="bigrs",password="bigrs")

rs <- dbSendQuery(con,"select i.data_e_hora,i.mortos,i.feridos,i.cod_acid,i.tipo_acide,i.veiculos from incidentes i join (select bigrs.st_sp_buffer(geom,100) as geom from vias_velocidade_alterada) v on st_contains(v.geom,i.geom)='t'")

resultados <- dbFetch(rs)


resultados<-cbind(resultados, "mes" = as.numeric(format(resultados$data_e_hora,"%m")), "ano" = as.numeric(format(resultados$data_e_hora,"%Y")), "horas" = as.numeric(format(resultados$data_e_hora,"%H")) )

agregados <- aggregate(list("mortos"=resultados$mortos, "feridos" = resultados$feridos), by = list("m" = resultados$mes, "y" = resultados$ano), FUN = sum)



plot(as.Date(paste(agregados$y,mestring(agregados$m),"01",sep="-"), format= "%Y-%m-%d"),agregados$feridos,pch=20,col="blue",ylab="Feridos em vias c/alter", xlab="meses")

plot(as.Date(paste(agregados$y,mestring(agregados$m),"01",sep="-"), format= "%Y-%m-%d"), agregados$mortos,pch=20, col="red",ylab="Mortos em vias c/ alter", xlab="meses")

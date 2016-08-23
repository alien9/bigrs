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

rob_pois <- function(x) 
{
  cov.x <- vcovHC(x, type="HC0")
  std.err <- sqrt(diag(cov.x))
  r.est <- cbind("Estimate"= coef(x), "Robust SE" = std.err,  "Pr(>|z|)" = 2*pnorm(abs(coef(x)/std.err), lower.tail = FALSE), LL = coef(x) - 1.96 * std.err, UL = coef(x) + 1.96 * std.err)
  return (r.est)
}
#install.packages("RPostgreSQL")
library("RPostgreSQL")
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname="bigrs",host="localhost",port=5433,user="bigrs",password="bigrs")

rs <- dbSendQuery(con,"select distinct on(modelo.gid, modelo.data_vigor) modelo.gid, modelo.data_e_hora, modelo.mortos, modelo.feridos, modelo.tipo_acide, modelo.data_vigor, modelo.nome, modelo.tipo, modelo.veloc_apos, modelo.velocidade_antes from (select i.gid, i.data_e_hora,i.mortos,i.feridos, i.tipo_acide, v.data_vigor,v.tipo, v.nome, v.veloc_apos, v.velocidade_antes from incidentes i join (select bigrs.st_sp_buffer(geom,100) as geom, data_vigor, tipo, nome, veloc_apos, velocidade_antes  from vias_velocidade_alterada where data_vigor>='2015-03-01') v on st_contains(v.geom,i.geom)='t' where data_e_hora>='2015-03-01 00:00:00' order by i.gid asc, v.veloc_apos desc NULLS LAST, v.data_vigor asc NULLS LAST) modelo")
resultados <- dbFetch(rs)
colnames(resultados)[7] = "rua"
colnames(resultados)[8] = "tipo_rua"
resultados<-cbind(resultados, "mes" = as.numeric(format(resultados$data_e_hora,"%m")), "ano" = as.numeric(format(resultados$data_e_hora,"%Y")), "horas" = as.numeric(format(resultados$data_e_hora,"%H")))

#ds_reg <- cbind(ds_reg, "dum_fer" = (ds_reg$feridos>0), "dum_mor" = (ds_reg$mortos>0))
#ds_reg <-cbind(ds_reg, "intervencao" =(as.Date(ds_reg$data_e_hora)-as.Date(ds_reg$data_vigor))>=0)
for(i in unique(resultados$rua[is.na(resultados$tipo_rua)]))
{
  if (grepl("EXPR",i) | grepl("EXPRESSA",i) & !is.na(i))
  {
    resultados$tipo_rua[resultados$rua==i] = "EXPRESSA"
  }
  else
  {
    resultados$tipo_rua[resultados$rua==i] = strsplit(i," ")[[1]][length(strsplit(i," ")[[1]])]    
  }
}
agregados <- aggregate(list("mortos"=resultados$mortos, "feridos" = resultados$feridos), by = list("dia_incidente"= as.Date(resultados$data_e_hora), "dia_alteracao" = resultados$data_vigor, "rua" = resultados$rua, "tipo_rua" = resultados$tipo_rua), FUN = sum)
agregados_veloc <- aggregate(list("mortos"=resultados$mortos, "feridos" = resultados$feridos), by = list("dia_incidente"= as.Date(resultados$data_e_hora), "dia_alteracao" = resultados$data_vigor, "rua" = resultados$rua, "tipo_rua" = resultados$tipo_rua, "vel_antes"=resultados$velocidade_antes, "vel_apos" = resultados$veloc_apos), FUN = sum)

agregados = cbind(agregados, "intervencao" = (agregados$dia_incidente-agregados$dia_alteracao>=0), "mesano" = mesano(as.numeric(format(agregados$dia_incidente,"%m")), as.numeric(format(agregados$dia_incidente,"%Y"))))
agregados_veloc = cbind(agregados_veloc, "intervencao_vel" = (agregados_veloc$dia_incidente-agregados_veloc$dia_alteracao>=0)*(agregados_veloc$vel_antes-agregados_veloc$vel_apos), "mesano" = mesano(as.numeric(format(agregados_veloc$dia_incidente,"%m")), as.numeric(format(agregados_veloc$dia_incidente,"%Y"))))

agregados = cbind(agregados, "id" = paste(agregados$dia_alteracao,agregados$rua,sep=""))

agregados = cbind(agregados, "mortos_ou_feridos" = agregados$mortos+ agregados$feridos)
agregados_veloc = cbind(agregados_veloc, "mortos_ou_feridos" = agregados_veloc$mortos+ agregados_veloc$feridos)
agregados_veloc = cbind(agregados_veloc, "intervencao_sqr" = agregados_veloc$intervencao_vel^2)
#pacote de modelos para painel
#install.packages("plm")
library('plm')


#modelo 0: controle por dummies mensais
modelo0<- lm(mortos_ou_feridos~intervencao+factor(mesano), data=agregados)

#modelo1: controle por efeito fixo na via e dummies mensais
modelo1<- lm(mortos_ou_feridos~intervencao+factor(rua)+factor(mesano), data=agregados)

#modelo1: controle por tipo de via e dummies mensais
modelo2<- lm(mortos_ou_feridos~intervencao+factor(tipo_rua)+factor(mesano), data=agregados)

modelovel0<- lm(mortos_ou_feridos~intervencao_vel +factor(mesano), data=agregados_veloc)
modelovel2<- lm(mortos_ou_feridos~intervencao_vel +factor(mesano)+factor(tipo_rua), data=agregados_veloc)
modelovel1<- lm(mortos_ou_feridos~intervencao_vel  +factor(mesano)+factor(rua), data=agregados_veloc)

modelovelsqr <- lm(mortos_ou_feridos~intervencao_vel +intervencao_sqr +factor(mesano)+factor(rua), data=agregados_veloc)

require("lmtest")
#resultados com var robusta a autocorr
coefs0 <- coeftest(modelo0,vcov=vcovHC(modelo0,type = "HC0", cluster="rua",adjust=T))
coefs1 <- coeftest(modelo1,vcov=vcovHC(modelo1,type = "HC0", cluster="rua",adjust=T))
coefs2 <- coeftest(modelo2,vcov=vcovHC(modelo2,type = "HC0", cluster="rua",adjust=T))


#<- pdata.frame(agr, index = c("firm", "year"), drop.index = TRUE, row.names = TRUE

plot(density(agregados$mortos_ou_feridos))

#modelo poisson

pois2 <- glm(mortos_ou_feridos~intervencao+factor(tipo_rua)+factor(mesano), family="poisson", data=agregados)

pois1 <- glm(mortos_ou_feridos~intervencao+factor(rua)+factor(mesano), family="poisson", data=agregados)

pois0 <- glm(mortos_ou_feridos~intervencao+factor(mesano), family="poisson", data=agregados)


#summary(pois1)

#summary(pois2)

#install.packages("AER")
library(AER)
round(rob_pois(pois0), digits=5)
round(rob_pois(pois1), digits=5)
round(rob_pois(pois2), digits=5)
dispersiontest(pois2,trafo = 2, alternative="two.sided")

#install.packages("pscl")
library("pscl")


dbClearResult(rs)

dbDisconnect(con)

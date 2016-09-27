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
  cov.x <- vcovHC(x, type="HC0", cluster="rua")
  std.err <- sqrt(diag(cov.x))
  r.est <- cbind("Estimate"= coef(x), "Robust SE" = std.err,  "Pr(>|z|)" = 2*pnorm(abs(coef(x)/std.err), lower.tail = FALSE), LL = coef(x) - 1.96 * std.err, UL = coef(x) + 1.96 * std.err)
  return (r.est)
}

#install.packages("RPostgreSQL")
library("RPostgreSQL")
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname="bigrs",host="localhost",port=5433,user="bigrs",password="bigrs")

#rs <- dbSendQuery(con,"select distinct on(modelo.gid, modelo.data_vigor) modelo.gid, modelo.data_e_hora, modelo.mortos, modelo.feridos, modelo.tipo_acide, modelo.data_vigor, modelo.nome, modelo.tipo, modelo.veloc_apos, modelo.velocidade_antes from (select i.gid, i.data_e_hora,i.mortos,i.feridos, i.tipo_acide, v.data_vigor,v.tipo, v.nome, v.veloc_apos, v.velocidade_antes from incidentes i join (select bigrs.st_sp_buffer(geom,100) as geom, data_vigor, tipo, nome, veloc_apos, velocidade_antes  from vias_velocidade_alterada where data_vigor>='2015-03-01') v on st_contains(v.geom,i.geom)='t' where data_e_hora>='2015-03-01 00:00:00' order by i.gid asc, v.veloc_apos desc NULLS LAST, v.data_vigor asc NULLS LAST) modelo")

rs <- dbSendQuery(con,"select modelo.gid, modelo.data_e_hora, modelo.mortos, modelo.feridos, modelo.tipo_acide, v.data_vigor, v.tipo, v.nome, v.veloc_apos, v.velocidade_antes, v.classifica from
(
select modi.gid, modi.data_e_hora,modi.mortos,modi.feridos, modi.tipo_acide, moda.geom  from 
(select distinct on (i.gid) i.gid, i.data_e_hora,i.mortos,i.feridos, i.tipo_acide, nearest_neighbourcrit('vias_velocidade_alterada', 'geom', 'data_vigor', '2015-03-01',  i.geom) as nrst from
(select * from incidentes where data_e_hora >='2015-01-01 00:00:00') i 
join 
(select bigrs.st_sp_buffer(geom,50) as buf, geom from vias_velocidade_alterada where data_vigor>= '2015-03-01') a
on st_contains(a.buf,i.geom)='t')  modi join (select geom, gid from vias_velocidade_alterada) moda on modi.nrst=moda.gid ) modelo 
join (select data_vigor, geom, tipo, nome, veloc_apos, velocidade_antes, classifica from vias_velocidade_alterada where data_vigor>= '2015-03-01') v on modelo.geom=v.geom")
                  

resultados <- dbFetch(rs)
colnames(resultados)[8] = "rua"
colnames(resultados)[7] = "tipo_rua"
resultados<-cbind(resultados, "mes" = as.numeric(format(resultados$data_e_hora,"%m")), "ano" = as.numeric(format(resultados$data_e_hora,"%Y")), "horas" = as.numeric(format(resultados$data_e_hora,"%H")))

resultados<-cbind(resultados, "dia_da_semana" = weekdays(resultados$data_e_hora))

resultados<-cbind(resultados, "dia_incidente" = as.Date(resultados$data_e_hora))
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

agregados <- aggregate(list("mortos"=resultados$mortos, "feridos" = resultados$feridos), by = list("dia_incidente"= resultados$dia_incidente, "dia_alteracao" = resultados$data_vigor, "rua" = resultados$rua, "velocidade_apos" = resultados$veloc_apos, "tipo_rua" = resultados$tipo_rua), FUN = sum)




cc<-dbSendQuery(con,"select data_vigor, tipo, nome, veloc_apos, velocidade_antes, classifica, st_length(st_transform(geom,32723)) as comprimento from vias_velocidade_alterada where data_vigor>= '2015-03-01'")
comp <-dbFetch(cc)
colnames(comp)[3]="rua"
colnames(comp)[2]="tipo_rua"

for(i in unique(comp$rua[is.na(comp$tipo_rua)]))
{
  if (grepl("EXPR",i) | grepl("EXPRESSA",i) & !is.na(i))
  {
    comp$tipo_rua[comp$rua==i] = "EXPRESSA"
  }
  else
  {
    comp$tipo_rua[comp$rua==i] = strsplit(i," ")[[1]][length(strsplit(i," ")[[1]])]    
  }
}

s = unique(comp[,c("rua", "tipo_rua", "data_vigor")])
for (l in 1:length(s[,1]))
{
  k = ((s$rua[l]==comp$rua)&(s$tipo_rua[l]==comp$tipo_rua)&(s$data_vigor[l]==comp$data_vigor))
  condicao= k&(!is.na(comp$velocidade_antes))
  print(mean(comp$velocidade_antes[condicao]))
  if(sum(mean(comp$velocidade_antes[condicao])==comp$velocidade_antes[condicao])==length(comp$velocidade_antes[condicao]))
  {
    print(s$rua[l])
    comp$velocidade_antes[k&(is.na(comp$velocidade_antes))]  = mean(comp$velocidade_antes[condicao])
    
  }  
}

comprimento <- aggregate(list("comprimento"= comp$comprimento), by = list("dia_alteracao" = comp$data_vigor, "rua" = comp$rua, "velocidade_apos" = comp$veloc_apos, "tipo_rua" = comp$tipo_rua), FUN = sum)
velocidade <- aggregate(list("velocidade_antes"=comp$velocidade_antes), by = list("dia_alteracao" = comp$data_vigor, "rua" = comp$rua, "velocidade_apos" = comp$veloc_apos, "tipo_rua" = comp$tipo_rua), FUN = mean)
velocidade$velocidade_antes[is.nan(velocidade$velocidade_antes)] = NA

agregados_velocidade =merge(x = agregados, y=velocidade, all.x = TRUE, by = c("dia_alteracao", "rua", "velocidade_apos", "tipo_rua"))
agregados_velocidade =merge(x = agregados_velocidade, y=comprimento, all.x = TRUE, by = c("dia_alteracao", "rua", "velocidade_apos", "tipo_rua"))

agregados_velocidade = cbind(agregados_velocidade, "intervencao" = (agregados_velocidade$dia_incidente-agregados_velocidade$dia_alteracao>=0), "mesano" = mesano(as.numeric(format(agregados_velocidade$dia_incidente,"%m")), as.numeric(format(agregados_velocidade$dia_incidente,"%Y"))))

agregados_velocidade = cbind(agregados_velocidade, "intervencao_vel" = (agregados_velocidade$dia_incidente-agregados_velocidade$dia_alteracao>=0)*(agregados_velocidade$velocidade_antes-agregados_velocidade$velocidade_apos))


agregados_velocidade = cbind(agregados_velocidade, "mortos_ou_feridos" = agregados_velocidade$mortos+ agregados_velocidade$feridos)



agregados_velocidade<-cbind(agregados_velocidade, "dia_da_semana" = weekdays(agregados_velocidade$dia_incidente))
agregados_velocidade$velocidade_antes[agregados_velocidade$velocidade_antes==-10] = NA
agregados_velocidade$intervencao_vel[agregados_velocidade$intervencao_vel==-10]=NA



agregados_velocidade= agregados_velocidade[agregados_velocidade$comprimento>100,]
agregados_velocidade$comprimento = agregados_velocidade$comprimento/1000


write.csv(agregados_velocidade, file = "agreg.csv")



#pacote de modelos para painel
#install.packages("plm")
library('plm')


#modelo 0: controle por dummies mensais
modelo1<- lm(feridos/comprimento~intervencao+factor(mesano)+factor(dia_da_semana), data=agregados_velocidade)


#modelo1: controle por tipo de via e dummies mensais
modelo2<- lm(feridos/comprimento~intervencao+factor(tipo_rua)+factor(mesano)+factor(dia_da_semana), data=agregados_velocidade)


#modelo1: controle por efeito fixo na via e dummies mensais
modelo3<- lm(feridos/comprimento~intervencao+factor(rua)+factor(mesano)+factor(dia_da_semana), data=agregados_velocidade)


semodelo1 <- sqrt(diag(plm:vcovHC(modelo1, type = "HC0", cluster="rua",adjust=T)))
semodelo2 <- sqrt(diag(plm:vcovHC(modelo2, type = "HC0", cluster="rua",adjust=T)))
semodelo3 <- sqrt(diag(plm:vcovHC(modelo3, type = "HC0", cluster="rua",adjust=T)))




require("lmtest")
#resultados com var robusta a autocorr







#<- pdata.frame(agr, index = c("firm", "year"), drop.index = TRUE, row.names = TRUE

hist(agregados_velocidade$mortos_ou_feridos)

detach(package:plm)

#modelo poisson


pois1 <- glm(feridos~intervencao+factor(mesano)+factor(dia_da_semana)+offset(log(comprimento)), family="poisson", data=agregados_velocidade)


pois2 <- glm(feridos~intervencao+factor(mesano)+factor(dia_da_semana)+factor(tipo_rua)+offset(log(comprimento)), family="poisson", data=agregados_velocidade)


pois3 <- glm(feridos~intervencao+factor(mesano)+factor(dia_da_semana)+factor(rua)+offset(log(comprimento)), family="poisson", data=agregados_velocidade)



#summary(pois1)

#summary(pois2)

#install.packages("AER")
library(AER)

dispersiontest(pois1,trafo = 2)

dispersiontest(pois2,trafo = 2)

dispersiontest(pois3,trafo = 2)


#install.packages("pscl")
#library("pscl")
require(mass)

dbClearResult(rs)

dbDisconnect(con)


require("stargazer")

sepois1 = sqrt(diag(plm::vcovHC(pois1, type="HC0")))

sepois2 = sqrt(diag(vcov(pois2, type="HC0")))

sepois3 = sqrt(diag(vcov(pois3, type="HCO")))

detach(package:AER)
detach(package:sandwich)
stargazer(modelo1, modelo2, modelo3, pois2, pois1, pois3, title = "Poisson para razâo feridos/km", se =list(semodelo1, semodelo2, semodelo3, sepois1, sepois2, sepois3), out = "tabela1.tex", omit =c("rua","tipo_rua"), omit.labels = c("Efeito fixo de via", "Tipos de rua"), dep.var.labels = "Feridos/km de via")




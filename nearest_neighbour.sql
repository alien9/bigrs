select * from vias_velocidade_alterada where rua~'GUIDO CALOI'


update vias_velocidade_alterada set velocidade_antes=90 where rua~'NACOES UNIDAS' and velocidade_antes is null and veloc_apos=70;
update vias_velocidade_alterada set velocidade_antes=70 where rua~'GUIDO CALOI' and velocidade_antes is null and veloc_apos=50;


select distinct classifica from vias_velocidade_alterada
select classifica, tipo, count(*) from vias_velocidade_alterada group by tipo,classifica

select count(*), classifica, velocidade_antes from vias_velocidade_alterada group by classifica, velocidade_antes

alter table vias_velocidade_alterada add origem_velocidade_antes varchar(100)

select * from vias_velocidade_alterada where classifica is null

SELECT               
  pg_attribute.attname, 
  format_type(pg_attribute.atttypid, pg_attribute.atttypmod) 
FROM pg_index, pg_class, pg_attribute, pg_namespace 
WHERE 
  pg_class.oid = 'vias_velocidade_alterada'::regclass AND 
  indrelid = pg_class.oid AND 
  nspname = 'public' AND 
  pg_class.relnamespace = pg_namespace.oid AND 
  pg_attribute.attrelid = pg_class.oid AND 
  pg_attribute.attnum = any(pg_index.indkey)
 AND indisprimary


select st_distance(st_transform(a.geom,32723),st_transform(i.geom,32723)) as d, a.rua, i.mortos, i.feridos, i.data_e_hora, i.gid

select nearest_neighbour('vias_velocidade_alterada','geom',(select geom from incidentes limit 1))

create or replace function bigrs.nearest_neighbour(t varchar, f varchar, g geometry) returns integer as $B$
declare
result integer;
kid varchar;
begin
SELECT               
  pg_attribute.attname into kid
FROM pg_index, pg_class, pg_attribute, pg_namespace 
WHERE 
  pg_class.oid = t::regclass AND 
  indrelid = pg_class.oid AND 
  nspname = 'public' AND 
  pg_class.relnamespace = pg_namespace.oid AND 
  pg_attribute.attrelid = pg_class.oid AND 
  pg_attribute.attnum = any(pg_index.indkey)
 AND indisprimary;
EXECUTE 
        'SELECT '||kid||' from '||quote_ident(t)||' 
ORDER BY '||quote_ident(f)||' <-> st_transform(ST_GeomFromEWKt('''||st_asewkt(g)||'''),32723)
        limit 1'
        INTO result;
    RETURN result;
--SELECT name, gid
--FROM geonames
--ORDER BY geom <-> st_setsrid(st_makepoint(-90,40),4326)
--LIMIT 10;
end;
$B$ language 'plpgsql'

select count(*) from 
(select distinct geom from vias_velocidade_alterada) 
a
select count(*) from
vias_velocidade_alterada

select aa.geom,b.rua  from
(select * from
(
select count(*) as n, geom from vias_velocidade_alterada where date_part('YEAR', data_vigor)=2015 group by geom
) a 
where a.n>1 
) aa
join vias_velocidade_alterada b 
on b.geom=aa.geom




select a.gid, a.nn, b.rua from
(
select distinct i.gid,nearest_neighbour('vias_velocidade_alterada', 'geom', i.geom) as nn
from
(select bigrs.st_sp_buffer(geom,100) as buf,geom,rua from vias_velocidade_alterada where rua~'MORVAN') a join
incidentes i
on st_contains(a.buf,i.geom)='t'
) a join vias_velocidade_alterada b 
on b.gid=a.nn

order by d


select classifica, count(*) from vias_velocidade_alterada group by classifica 
update vias_velocidade_alterada set velocidade_antes=60,origem_velocidade_antes='CTB' where classifica~'Arterial' and velocidade_antes is NULL


select distinct velocidade_antes,veloc_apos,classifica,inicio,date_part('YEAR',data_vigor) from vias_velocidade_alterada where classifica~'Coletora' 

select distinct velocidade_antes,veloc_apos,classifica,inicio,date_part('YEAR',data_vigor) from vias_velocidade_alterada where classifica~'Local' 




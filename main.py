from flask import Flask,request,render_template, send_from_directory, session, Response, jsonify
import psycopg2,json,memcache,unicodedata,re,numpy,datetime,calendar
from numpy import *
import scipy as sp
from pandas import *
from rpy2.robjects.packages import importr
import rpy2.robjects as ro
import pandas.rpy.common as com
from datetime import date
import array

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

@app.route('/')
def index():
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    mes = mc.get('mes')
    ano = mc.get('ano')
    if not mes:
        conn = psycopg2.connect("dbname='bigrs' user='bigrs' host='localhost' port='5433' password='bigrs'")
        cur = conn.cursor()
        cur.execute("select date_part('year',data_e_hora),date_part('month',data_e_hora) from incidentes order by data_e_hora desc limit 1")
        r=cur.fetchone()
        mes=r[1]
        ano=r[0]
        mc.set('mes',mes)
        mc.set('ano',ano)
    h={'mes':int(mes),'ano':int(ano)}
    return render_template('index.html',**h)


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('images', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@app.route('/icons/<path:path>')
def send_icon(path):
    return send_from_directory('icons', path)

@app.route('/search', methods=['GET','POST'])
def search():
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    streets = mc.get('streets')
    if not streets:
        #print("executando query")
        streets={}
        conn = psycopg2.connect("dbname='bigrs' user='bigrs' host='localhost' port='5433' password='bigrs'")
        cur = conn.cursor()
        cur.execute("select distinct lg_codlog,lg_tipo,lg_titulo,lg_prep,lg_nome from sirgas_shp_logradouro")
        old=""
        for row in cur.fetchall():
            nome=row[4]
            if nome is not None:
                if nome!=old:
                    old=nome
                    k=nome[:2]
                    if not k in streets:
                        streets[k]=[]
                    streets[k]+=[row]
        mc.set('streets',streets)
    if 'term' in request.form:
        term=purge(request.form['term'])
    else:
        term="PAULISTA"

    k=term[:2].upper()
    if k in streets:
        j=streets[k]
        return Response(json.dumps(j), mimetype='application/json', status=200)
    else:
        return json.dumps([])

def purge(s):
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

@app.route('/geocode', methods=['GET','POST'])
def geocode():
    codlog=request.form['codlog']
    numero=request.form['numero']
    conn = psycopg2.connect("dbname='bigrs' user='bigrs' host='localhost' port='5433' password='bigrs'")
    cur = conn.cursor()
    print(codlog)
    cur.execute("select bigrs.geocode(%s, %s)", (codlog,numero,))
    r=cur.fetchone()
    return r[0]

@app.route('/reverse', methods=['GET','POST'])
def reverse():
    p=request.values.getlist('point[]')
    conn = psycopg2.connect("dbname='bigrs' user='bigrs' host='localhost' port='5433' password='bigrs'")
    cur = conn.cursor()
    cur.execute("select bigrs.reverse_geocode(%s, %s)", (p[0],p[1],))
    r=cur.fetchone()
    res=r[0]
    j={}
    if res is not None:
        j=json.loads(res)
        cur.execute("select st_asgeojson(st_transform(geom,4326)) from sirgas_shp_logradouro where lg_codlog=%s", (j['codlog'],))
        j['geometry']=cur.fetchall();
    return json.dumps(j)

@app.route('/report',methods=['GET','POST'])
def report():
    p=request.values.get('codlog')
    h = {'codlog':p}
    conn = psycopg2.connect("dbname='bigrs' user='bigrs' host='localhost' port='5433' password='bigrs'")
    cur = conn.cursor()
    cur.execute("select lg_total_length from logradouro_details where lg_codlog=%s", (p,))
    r=cur.fetchone()
    h['length']=round(float(r[0]))
    cur.execute("select * from incidentes where st_contains(st_transform((select st_buffer(st_union(geom),50) from sirgas_shp_logradouro where lg_codlog=%s),31983), geom)='t'", (p,))

    r = cur.fetchall()
    print(r)
    return render_template('report.html',**h)

@app.route('/vector',methods=['GET','POST'])
def vector():
    p=request.values.get('layer')
    p=re.sub("\W","",p)
    with open('vector/%s.geojson'%(p,), 'r') as f:
        data = f.read()
    f.closed
    return data
def prepare_parameters(request):
    h={}
    h['tipo_regiao'] = request.values.get('adm')
    h['tipo_regiao'] = re.sub("\W", "", h['tipo_regiao'])
    periodo = request.values.get('periodo')
    h['veiculos'] = ",".join(request.values.getlist('tipo_veiculo[]')).split(",")
    if periodo == 'mes':
        h['data_inicio'] = date(int(request.values.get('ano')), int(request.values.get('mes')), 1)
        h['data_final'] = date(int(request.values.get('ano')), int(request.values.get('mes')),
                          calendar.monthrange(int(request.values.get('ano')), int(request.values.get('mes')))[1])
    else:
        h['data_inicio'] = date(int(request.values.get('ano')), 1, 1)
        h['data_final'] = date(int(request.values.get('ano')), 12, 31)
    h['tipo'] = request.values.get('tipo')
    h['contagem'] = request.values.get('contagem')
    return h

def get_query(request):
    params=prepare_parameters(request)
    #p = request.values.get('adm')
    #p = re.sub("\W", "", p)
    periodo = request.values.get('periodo')
    #ano = int(request.values.get('ano'))
    #veiculos = ",".join(request.values.getlist('tipo_veiculo[]')).split(",")
    #if periodo == 'mes':
        #data_inicio = date(int(request.values.get('ano')), int(request.values.get('mes')), 1)
        #data_final = date(int(request.values.get('ano')), int(request.values.get('mes')),
        #                  calendar.monthrange(int(request.values.get('ano')), int(request.values.get('mes')))[1])
    #else:
        #data_inicio = date(int(request.values.get('ano')), 1, 1)
        #data_final = date(int(request.values.get('ano')), 12, 31)
    tipo = request.values.get('tipo')
    contagem = request.values.get('contagem')
    qtipo = "count(*)"
    if params['tipo'] == 'mortos':
        qtipo = "sum(mortos)"
    if params['tipo'] == 'feridos':
        qtipo = "sum(feridos)"
    if params['tipo'] == 'vitimas':
        qtipo = "sum(mortos+feridos)"
    if params['tipo_regiao'] == 'distritos':
        table = "sirgas_shp_distrito_polygon p"
        popt = "distritos_populacao dp on dp.distrito_gid=s.gid"
    else:
        table = "sirgas_shp_subprefeitura p"
        popt = "subprefeituras_populacao dp on dp.subprefeitura_gid=s.gid"
    vtipo = ""
    vwhere = ""
    if len(params['veiculos']) < 14 and len(params['veiculos']) > 0:
        vtipo = " join veiculos v on v.id_acidente=i.id_acident"
        vwhere = "and v.tipo_veiculo in('" + "','".join(params['veiculos']) + "')"
    if contagem == 'cem_mil':
        query = "select s.gid,contagem/populacao*100000 from (select p.gid," + qtipo + "::float as contagem from incidentes i join " + table + " on st_contains(p.the_geom, i.geom) = 't' " + vtipo + " where i.data_e_hora between %s and %s " + vwhere + " group by p.gid) s join " + popt + " where dp.ano=%s;"
        parameters = (params['data_inicio'].strftime('%Y-%m-%d'), params['data_final'].strftime('%Y-%m-%d'), ano)
    else:
        query = "select p.gid," + qtipo + " from incidentes i join " + table + " on st_contains(p.the_geom, i.geom) = 't' " + vtipo + " where i.data_e_hora between %s and %s " + vwhere + " group by p.gid;"
        parameters = (params['data_inicio'].strftime('%Y-%m-%d'), params['data_final'].strftime('%Y-%m-%d'),)

    return query,parameters


@app.route('/theme',methods=['GET','POST'])
def theme():
    r={}
    conn = psycopg2.connect("dbname='bigrs' user='bigrs' host='localhost' port='5433' password='bigrs'")
    cur = conn.cursor()
    query,parameters=get_query(request)
    #print(cur.mogrify(query,parameters))
    cur.execute(query,parameters)
    r['items'] = cur.fetchall()
    values = [x[1] for x in r['items']]
    size=7
    cuts=range(0, 100, 16)
    r['percentiles']=[]
    if len(values) > 0:
        r['percentiles']=numpy.percentile(values,cuts).tolist()
    return json.dumps(r)

def movingaverage(interval, window_size):
    window= numpy.ones(int(window_size))/float(window_size)
    print(window)
    print(interval)
    return numpy.convolve(interval, window, 'same')
def running_mean(l, N):
    print(l)
    sum = 0
    result = list( NaN for x in l)
    for i in range( 0, N):
        sum = sum + l[i]
    for i in range( N, len(l)):
        result[i - N//2] = sum / N
        sum = sum - l[i - N] + l[i]
    result[len(l)-N//2] = sum/N
    print(result)
    return result
@app.route('/history',methods=['GET','POST'])
def history():
    conn = psycopg2.connect("dbname='bigrs' user='bigrs' host='localhost' port='5433' password='bigrs'")
    cur = conn.cursor()
    r={}
    tipo = request.values.get('tipo')
    params=prepare_parameters(request)
    #print(params)
    if params['tipo_regiao']=='subprefeituras':
        cur.execute("select st_asewkt(st_transform(geom,4326)) from sirgas_shp_subprefeitura where gid=%s",(request.values.get('feature_id'),))
    elif params['tipo_regiao']=='distritos':
        cur.execute("select st_asewkt(st_transform(geom,4326)) from sirgas_distritos_polygon where gid=%s",(request.values.get('feature_id'),))
    else:
        cur.execute("select st_asewkt(st_transform(st_buffer(geom,50),4326)) from sirgas_shp_logradouro where lg_codlog=%s",(request.values.get('feature_id'),))
    geometry=cur.fetchone()[0]
    query="select count(*) as total,sum(feridos::integer) as vitimas,sum(mortos::integer) as mortos,date_part('year',data_e_hora) as ano,date_part('month',data_e_hora) as mes from incidentes i where st_contains(st_geomfromewkt(%s),i.geom)='t' and data_e_hora>'2010-12-31 23:59:59' group by ano,mes order by ano,mes"
    print(query)
    datasets = importr('datasets')
    cur.execute(query,(geometry,))
    ds=numpy.array(cur.fetchall())
    grdevices=importr('grDevices')
    graphics=importr('graphics')
    base = importr("base")
    import rpy2.robjects.numpy2ri
    rpy2.robjects.numpy2ri.activate()
    #grdevices.pdf(file='report.pdf')
    #grdevices.png(file='report.png')

    graphics.par(mfrow=array.array('i', [2, 1]))
    datas = ds[:, [3,4]]
    x=[date(int(elem[0]),int(elem[1]),1).strftime("%Y-%m-%d") for elem in datas]
    x=rpy2.robjects.StrVector(x)
    #x=[int(elem[0]) for elem in datas]
    print(x)
    x = base.as_Date(x, format="%Y-%m-%d")
    y=ds[:,[0]]
    #kwargs = {'ylab':"Ocorrências",'xlab':'Meses','xaxt':"n", 'type':"b", 'col':"blue"}
    graphics.par(bg='white')

    kwargs = {'x':x,'y':y,'ylab':"Ocorrências",'xlab':'Meses','type':"l", 'col':"blue"}
    graphics.plot(**kwargs)
    graphics.lines(x,rpy2.robjects.FloatVector(running_mean(y,12)))
    graphics.grid(lty='dashed',col='darkgrey')
    y = ds[:, [1]]

    kwargs = {'x': x, 'y': y, 'ylab': "Mortos/Feridos", 'xlab': 'Meses', 'type': "l",
              'col': "blue"}
    graphics.plot(**kwargs)
    graphics.par(new=True)
    graphics.plot(**{'x':x, 'y':ds[:, [2]], 'type':'l', 'axes':False, 'xlab':'', 'ylab':''})
    graphics.axis(**{'side':4, 'col':'black', 'las':1})
    graphics.grid(lty='dashed', col='darkgrey')
    graphics.par(new=False)
    grdevices.dev_copy(grdevices.png,'report.png')
    grdevices.dev_off()

    grdevices.dev_print(grdevices.pdf, 'report.pdf')
    grdevices.graphics_off()

    return json.dumps(r)

app.run(host='0.0.0.0',debug=True)
from django.shortcuts import render,redirect
from django.db import connection
from django.http import JsonResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
import json,time,memcache,re,calendar,os,numpy,unicodedata
from datetime import date
from bigrs.settings import *
from django.core.files.storage import FileSystemStorage
from maps.models import *

# Create your views here.
@login_required(login_url='/auth')
def index(request):
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    mes = mc.get('mes')
    ano = mc.get('ano')
    if not mes:
        conn = connection.cursor().connection
        cur = conn.cursor()
        cur.execute("select date_part('year',data_e_hora),date_part('month',data_e_hora) from incidentes order by data_e_hora desc limit 1")
        r=cur.fetchone()
        mes=r[1]
        ano=r[0]
        mc.set('mes',mes)
        mc.set('ano',ano)
    return render(request, "index.html",{'geoserver':geoserver,'mes':int(mes),'ano':int(ano),'user':request.user})

def geojson(request):
    conn = connection.cursor().connection #psycopg2.connect(cstring)
    cur = conn.cursor()

    ano = request.GET.get('ano','2015')

    cur.execute("select st_x(geom),st_y(geom),data_e_hora,gid from incidentes where data_e_hora between %s and %s",
                ("%s-01-01 00:00:00" % (ano,), "%s-12-31 23:59:59" % (ano),))
    j = {
        'type': 'FeatureCollection',
        'features': []
    }
    for record in cur:
        j['features'].append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [record[0], record[1]],
            },
            'properties': {
                'data_e_hora': time.mktime(record[2].timetuple())
            }
        })
    return JsonResponse(j)

def theme(request):
    r={}
    conn = connection.cursor().connection
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
    return JsonResponse(r)

def get_query(request):
    params=prepare_parameters(request)
    #p = request.values.get('adm')
    #p = re.sub("\W", "", p)
    periodo = request.GET.get('periodo')
    #ano = int(request.values.get('ano'))
    #veiculos = ",".join(request.values.getlist('tipo_veiculo[]')).split(",")
    #if periodo == 'mes':
        #data_inicio = date(int(request.values.get('ano')), int(request.values.get('mes')), 1)
        #data_final = date(int(request.values.get('ano')), int(request.values.get('mes')),
        #                  calendar.monthrange(int(request.values.get('ano')), int(request.values.get('mes')))[1])
    #else:
        #data_inicio = date(int(request.values.get('ano')), 1, 1)
        #data_final = date(int(request.values.get('ano')), 12, 31)
    tipo = request.GET.get('tipo')
    contagem = request.GET.get('contagem')
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

def prepare_parameters(request):
    h={}
    h['tipo_regiao'] = request.GET.get('adm')
    h['tipo_regiao'] = re.sub("\W", "", h['tipo_regiao'])
    periodo = request.GET.get('periodo')
    h['veiculos'] = ",".join(request.GET.getlist('tipo_veiculo[]')).split(",")
    if periodo == 'mes':
        h['data_inicio'] = date(int(request.GET.get('ano')), int(request.GET.get('mes')), 1)
        h['data_final'] = date(int(request.GET.get('ano')), int(request.GET.get('mes')),
        calendar.monthrange(int(request.GET.get('ano')), int(request.GET.get('mes')))[1])
    else:
        h['data_inicio'] = date(int(request.GET.get('ano')), 1, 1)
        h['data_final'] = date(int(request.GET.get('ano')), 12, 31)
    h['tipo'] = request.GET.get('tipo')
    h['contagem'] = request.GET.get('contagem')
    return h

def vector(request):
    dir=os.path.join(os.path.dirname(BASE_DIR), 'vector')
    p=request.GET.get('layer')
    p=re.sub("\W","",p)
    with open(os.path.join(dir,'%s.geojson'%(p,)), 'r') as f:
        data = f.read()
    f.closed
    return JsonResponse(json.loads(data))

def reverse(request):
    p=request.POST.getlist('point[]')
    conn = connection.cursor().connection
    cur = conn.cursor()
    cur.execute("select bigrs.reverse_geocode(%s, %s)", (p[0],p[1],))
    r=cur.fetchone()
    res=r[0]
    j={}
    if res is not None:
        j=json.loads(res)
        cur.execute("select st_asgeojson(st_transform(geom,4326)) from sirgas_shp_logradouro where lg_codlog=%s", (j['codlog'],))
        j['geometry']=cur.fetchall();
    return JsonResponse(j)

def conta(request):
    j={'result':'ok'}
    return JsonResponse(j)

def contador(request,contador_id):
    if request.user.is_authenticated:
        filename=Contagem.objects.get(pk=contador_id).movie.url
        print(filename)
        return render(request,'contador.html', {'arq':filename, 'root':VIDEO_URL_ROOT,'geoserver':geoserver})
    else:
        print("nao autenticado")
        return render(request,'login.html')

def lista_contagens(request):
    if not request.user.is_authenticated:
        return render(request,'login.html')
    contagens=Contagem.objects.all()
    return render(request,'lista.html',{'contagens':contagens})

def nova_contagem(request):
    if not request.user.is_authenticated:
        return render(request,'login.html')
    if request.method == 'POST' and request.FILES['file']:
        myfile = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(VIDEO_FILES_ROOT+'/'+myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        contagem=Contagem(
            author = request.user,
            nome_do_arquivo = myfile.name,
            endereco=request.POST.get('endereco')
        )
        contagem.save()
    return redirect(lista_contagens)


def auth(request):
    if request.POST:
        print("é post")
    else:
        print("é get")
    print(request.user)
    if request.user.is_authenticated():
        return redirect(index)
    user=authenticate(username=request.POST.get('login'),password=request.POST.get('password'))
    print(request.POST)
    print(user)
    if user is not None:
        login(request, user)
        return redirect(index)
    else:
        return render(request,'login.html')


def log_out(request):
    logout(request)
    return redirect(index)

def purge(s):
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

def search(request):
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    streets = mc.get('streets')
    if not streets:
        #print("executando query")
        streets={}
        conn = connection.cursor().connection
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
    if 'term' in request.POST:
        term=purge(request.POST.get('term'))
    else:
        term="PAULISTA"

    k=term[:2].upper()
    if k in streets:
        j=streets[k]
        return JsonResponse(j, safe=False)
    else:
        return JsonResponse([])
    return None


def geocode(request):
    codlog=request.POST.get('codlog')
    numero=request.POST.get('numero')
    conn = connection.cursor().connection
    cur = conn.cursor()
    cur.execute("select bigrs.geocode(%s, %s)", (codlog,numero,))
    r=cur.fetchone()
    return JsonResponse(json.loads(r[0]),safe=False)

def social_error(request):
    return render(request,'socialauth-error.html')
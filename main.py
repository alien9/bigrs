from flask import Flask,request,render_template, send_from_directory, session, Response, jsonify
import psycopg2,json,memcache,unicodedata

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

@app.route('/')
def index():
    return render_template('index.html')


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
    return r[0]
@app.route('/report',methods=['GET','POST'])
def report():
    p=request.values.get('codlog')
    h = {'codlog':p}
    conn = psycopg2.connect("dbname='bigrs' user='bigrs' host='localhost' port='5433' password='bigrs'")
    cur = conn.cursor()
    cur.execute("select lg_total_length from logradouro_details where lg_codlog=%s", (p,))
    r=cur.fetchone()
    h['length']=round(float(r[0]))
    cur.execute("select * from incidentes where st_contains(st_transform((select st_buffer(st_union(geom),5 0) from sirgas_shp_logradouro where lg_codlog=%s),32723), geom)='t'", (p,))

    r = cur.fetchall()
    print(r)
    return render_template('report.html',**h)


app.run(host='0.0.0.0',debug=True)
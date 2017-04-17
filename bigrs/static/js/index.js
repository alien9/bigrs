var size=7;
var colors=new Array(size);
//colors[0]='64c800';
//colors[size-1]='c86400';
colors[0]='FFFFFF';
colors[size-1]='FF0000';
var c0=[parseInt(colors[0].substr(0,2),16),parseInt(colors[0].substr(2,2),16),parseInt(colors[0].substr(4,2),16)];
var c1=[parseInt(colors[size-1].substr(0,2),16),parseInt(colors[size-1].substr(2,2),16),parseInt(colors[size-1].substr(4,2),16)];
var interval=[(c1[0]-c0[0])/size,(c1[1]-c0[1])/size,(c1[2]-c0[2])/size];
for(var i=1;i<colors.length-1;i++){
    colors[i]=lpad(Math.round(c0[0]+i*interval[0]).toString(16))+lpad(Math.round(c0[1]+i*interval[1]).toString(16))+lpad(Math.round(c0[2]+i*interval[2]).toString(16));
}
var map;
var hash=[];
var layers={};
function select(i){
    var j=0;
    $('#search_results').children('a').each(function () {
        if(j==i){
            $(this).addClass('selected');
        }else{
            $(this).removeClass('selected');
        }
        j++;
    });
}
/**
 * Elements that make up the popup.
 */
var container;
var content;
var closer;

var selected_marker;
var points;
var featurething;
var zoom;
var center;
var vectorSource;

function intersects(a,b){
    var ta=a.split('|');
    var i=0;
    while(i<ta.length){
        if(ta[i].match(b)) return true;
        i++;
    }
    return false;
}


//setHeatMap();
function setHeatMap(){
    var h=getForm();
    //console.debug(h);
    h['FORMAT']='image/png';
    h['VERSION']='1.1.1';
    h['STYLES']='';
    h['LAYERS']='BIGRS:incidentes_params';
    var ano=h.ano;
    if(points==null){
        $.ajax('/geojson', {data:h,dataType:'json',success:function(j){
            var geojsonObject = j;
            var features = new ol.format.GeoJSON().readFeatures(geojsonObject, {
                featureProjection: 'EPSG:3857'
            });
            if(features.length){
                points = new ol.source.Vector({
                  'features': features
                });
                setHeatMap();
            }
        }});
        return;
    }

    if(layers['heatmap']){
        map.removeLayer(layers['heatmap']);
        delete(layers['heatmap']);
    }

    var features=[];
    var features = [];
    points.getFeatures().forEach(function(fu){
        var p=fu.getProperties();
        if(p.tipo_acide && p.tipo_acide.match(h.regex_tipo_acide)){
            if(intersects(p.tipo_veiculo,h.regex_tipo_veiculo)){
                features.push(fu);
            }
        }
    });
    var new_points = new ol.source.Vector({
      'features': features
    });
    layers['heatmap'] =  new ol.layer.Heatmap({
        source: new_points,
        radius: 2
    });
    map.addLayer(layers['heatmap']);
    isLoadingTheme=false;
    setModal(isLoadingTheme);
}

function getQuantile(value,quantiles){
for(var i=0;i<quantiles.length;i++){
    if(value<quantiles[i]) return i-1;
}
return i-1;
}
function hexToRgb(hex) {
var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
return result ? 'rgba('+parseInt(result[1], 16)+','+parseInt(result[2], 16)+','+parseInt(result[3], 16)+',0.5)': null;
}
function getForm(){
    var month=$('select[name=mes]').val();
    var year=$('input[name=ano]').val();
    if(month>12) month=12;
    if(month<1) month=1;
    var p=$('input[name=periodo]:checked').val();
    var d=new Date(year,month,0);
    var df=year+'-'+(1+parseInt(d.getMonth()))+'-'+d.getDate();
    if(p=='ano'){
        month=1;
        df=year+'-12-31';
    }
    var tipo_acidente=$('input[name=tipo_acidente]:checked').map(function(){
            return $(this).val();
        }).get();
    var cql_filter="tipo_acide in('"+(tipo_acidente.join(",").split(",").join("','"))+"')";
    var tipo_veiculo=$('input[name=tipo_veiculo]:checked').map(function(){
        return $(this).val();
    }).get();
    return {
        feature_id:$('input[name=feature_id]').val(),
        adm:$('input[name=adm]:checked').val(),
        tipo:$('input[name=tipo]:checked').val(),
        periodo:$('input[name=periodo]:checked').val(),
        mes:$('select[name=mes]').val(),
        ano:$('input[name=ano]').val(),
        contagem:$('input[name=contagem]:checked').val(),
        viewparams:"data_inicio:"+year+'-'+month+"-01;data_final:"+df,
        'tipo_veiculo':tipo_veiculo,

        cql_filter:cql_filter,
        regex_tipo_acide:new RegExp(tipo_acidente.join("|").replace(/\,/g,'|')),
        regexp_tipo_veiculo:new RegExp(tipo_veiculo.join('|').replace(/\,/g,'|'))
    };
}
var isLoadingTheme=false;
function loadTheme(){
    var h=getForm();
    if(isLoadingTheme) return;
    isLoadingTheme=true;
    setModal(isLoadingTheme);
    if(h.adm=='heatmap'){
        $('#filters_box .dados a,#filters_box .periodo a,#filters_box .contagem a').addClass('inactive');
        setHeatMap();
        return;
    }else{
        $('#filters_box a').removeClass('inactive');

    }
    $.ajax('/theme',{dataType:'json','data':h,success:function(j){
        var theme={};
        for(var i=0;i<j.items.length;i++){
            var k=getQuantile(j.items[i][1],j.percentiles);
            theme[j.items[i][0]]=hexToRgb(colors[k]);
        }
        var l=layers[h.adm];
        if(!l) {
            return;
            isLoadingTheme=false;
        }
        var s=l.getSource();
        if(s.getFeatures){
            var f=layers[h.adm].getSource().getFeatures();
            for(var i=0;i<f.length;i++){
                f[i].color=theme[f[i].get('gid')];
            }
            layers[h.adm].getSource().clear();
            layers[h.adm].getSource().addFeatures(f);
        }
        $("table#table_legenda").html('');
        for(var i=1;i<j.percentiles.length;i++){
            var tr=$('<tr></tr>');
            var td=$('<td></td>').addClass('legend_color').css('background-color','#'+colors[i-1]);
            tr.append(td);
            tr.append($('<td></td>').text(Math.round(j.percentiles[i-1])+' a '+Math.round(j.percentiles[i]))    );
            $("table#table_legenda").append(tr);
        }
        isLoadingTheme=false;
        setModal(isLoadingTheme);
    }});
}

function getStyles(feature, resolution){
var nome=$('input[name=adm]:checked').val();
switch(nome){
    case 'distritos':
        return new ol.style.Style({
          stroke: new ol.style.Stroke({
            color: 'gray',
            width: 1
          }),
          fill: new ol.style.Fill({
            color: (feature.color)?feature.color:hexToRgb('#'+colors[0])
          }),
          text: (resolution<20)?new ol.style.Text({
            font: '10px Verdana, sans-serif',
            text: feature.get('ds_nome'),
            fill: new ol.style.Fill({color: 'black'}),
            stroke: new ol.style.Stroke({color: 'white', width: 0.5})
          }):null
        });
     break;
     case 'subprefeituras':
        return new ol.style.Style({
          stroke: new ol.style.Stroke({
            color: 'gray',
            width: 1
          }),
          fill: new ol.style.Fill({
            color: (feature.color)?feature.color:hexToRgb('#'+colors[0])
          }),
          text: (resolution<100)?new ol.style.Text({
            font: '10px Verdana, sans-serif',
            text: feature.get('sp_nome'),
            fill: new ol.style.Fill({color: 'black'}),
            stroke: new ol.style.Stroke({color: 'white', width: 0.5})
          }):null
        });
     break;
 }
}

function addVector(g,nome){
  var source = new ol.source.Vector({
    features: (new ol.format.GeoJSON()).readFeatures(g)
  });
  var distritos = new ol.layer.Vector({
    source: source,
    style: getStyles
  });
  distritos.getSource().on('change',function(e){
    if(distritos.getSource().getState()=='ready'){
        loadTheme();
    }
  })
  map.addLayer(distritos);
  return distritos;
}

var projection = new ol.proj.Projection({
  code: 'EPSG:4326',
  units: 'degrees',
  axisOrientation: 'neu'
});

function fixHeight(){
    var h=$('body').height()-$('#cabecalho').height();
    $("#mapa").css('height',h+'px');
    map.updateSize();
    setModal(isLoadingTheme);
}

var selected=0;
function start(){
    var tiled = new ol.layer.Tile({
        visible: true,
        source: new ol.source.TileWMS({
          url: GEOSERVER+'/geoserver/BIGRS/wms',
          params: {'FORMAT': 'image/png',
                   'VERSION': '1.1.1',
                   tiled: true,
                STYLES: '',
                LAYERS: 'BIGRS:sirgas_shp_logradouro',
             tilesOrigin: -46.83525376879412 + "," + -24.012624936562503
          }
        })
    });
    container = document.getElementById('popup');
    content = document.getElementById('popup-content');
    closer = document.getElementById('popup-closer');
    var iconFeature = new ol.Feature({
        geometry: new ol.geom.Point(ol.proj.transform([-46.5, -23.5], projection, 'EPSG:3857')),
    });

    var iconStyle = new ol.style.Style({
        image: new ol.style.Icon({
          anchor: [0.5, 32],
          anchorXUnits: 'fraction',
          anchorYUnits: 'pixels',
          src: '/static/images/blue.png'
        })
    });
    iconFeature.setStyle(iconStyle);
    vectorSource = new ol.source.Vector({
      features: []
    });
    var vectorLayer = new ol.layer.Vector({
        source : vectorSource
    });

    zoom=12;
    var c=document.cookie.match(/zoom=(\d+)/);
    if(c) zoom=parseFloat(c.pop());
    center=ol.proj.fromLonLat([-46.5, -23.5]);
    c=document.cookie.match(/center=([^;]+);/);
    if(c) {
        c=c.pop().split(/,/);
        center=[parseFloat(c[0]),parseFloat(c[1])];
    }
    popup = new ol.Overlay(/** @type {olx.OverlayOptions} */ ({
      element: container,
      autoPan: true,
      autoPanAnimation: {
        duration: 250
      }
    }));
    closer.onclick = function() {
      popup.setPosition(undefined);
      closer.blur();
      return false;
    };
    map = new ol.Map({
        target: 'mapa',
        layers: [
          tiled
        ],
        overlays:[popup],
        view: new ol.View({
          'center': center,
          'zoom': zoom,
          minZoom: 10,
          maxZoom: 19
        })
    });
    var savecenter=function(){
        var center=map.getView().getCenter();
        if(isNaN(center[0]) || isNaN(center[1])) center=ol.proj.fromLonLat([-46.5, -23.5]);
        document.cookie="center="+center;
        document.cookie="zoom="+map.getView().getZoom();
    };

    map.on("moveend",savecenter);

    map.on("zoomend",savecenter);

    map.on("click", function(e){
        var isFeature=false;
        var coordinate=e.coordinate;
        var f;
        map.forEachFeatureAtPixel(e.pixel, function (feature, layer) {
            f=feature;
            isFeature=true;
        })
        console.debug(isFeature);
        if(isFeature){
            console.debug(f.getProperties());
            var hdms = ol.coordinate.toStringHDMS(ol.proj.transform(coordinate, 'EPSG:3857', 'EPSG:4326'));
            var html=$('#popup_template').html();
            if(f.getProperties().sp_id){ // subprefeitura
                console.debug(f.getProperties());
                $('input[name=feature_id]').val(f.getProperties().gid)
                html=html.replace(/\$name/,f.getProperties().sp_nome);
                content.innerHTML = html;
                $(content).find('a.marker_remove').hide();
            }else if(f.getProperties().ds_nome){ // distrito
                console.debug(f.getProperties());
                $('input[name=feature_id]').val(f.getProperties().gid)
                html=html.replace(/\$name/,f.getProperties().ds_nome);
                content.innerHTML = html;
                $(content).find('a.marker_remove').hide();
            }else if(f.getProperties().name){ //logradouro
                $('input[name=feature_id]').val(f.getProperties().codlog)
                console.debug(f.getProperties());
                html=html.replace(/\$name/,f.getProperties().name);
                selected_marker=f;
                content.innerHTML = html;
                $(content).find('a.marker_remove').show();
            }

            popup.setPosition(coordinate);
            $(content).find('a.marker_remove').click(function(){
                if(selected_marker)vectorSource.removeFeature(selected_marker);
                selected_marker=null;
                popup.setPosition(undefined);
                closer.blur();
            });
            $(content).find('a.marker_history').click(function(){
                $.ajax('/history',{dataType:'json',data:getForm(),success:function(h){
                    console.debug(h);
                }});
            });
            return;
        }else{
            if(featurething && vectorSource){
                vectorSource.removeFeature(featurething);
                featurething=null;
            }
        }
        var lonlat = ol.proj.toLonLat(map.getCoordinateFromPixel(e.pixel));
        $.ajax('/reverse',{'method':'post',dataType:'json', data:{point:lonlat,csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()}, success:function(j){
            featurething = new ol.Feature({
                name: j.endereco,
                number: j.numero,
                codlog: j.codlog,
                geometry: new ol.geom.Point(ol.proj.transform([j.x,j.y], 'EPSG:4326', 'EPSG:3857'))
            });
            featurething.setStyle(iconStyle);
            vectorSource.addFeature( featurething );
        },error:function(e){
            alert(e.statusText);
        }});
    });
    with(map.getView()){
        setZoom(zoom);
        setCenter(center);
    }
    //map.addLayer(layers['heatmap']);
    map.addLayer(vectorLayer);

    function geocode(){
        var codlog=$("input[name=codlog]").val();
        var a=$("input[name=search]").val().match(/\d+$/);
        var numero='0';
        if(a) numero=a.pop();
        $.ajax('/geocode', {method:'post',dataType:'json',data:{'numero':numero,'codlog':codlog,csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()}, success:function(j){
            map.getView().setCenter(ol.proj.fromLonLat([j['x'], j['y']]));
        }});
    }
    var term="";
    var load=function(j){
        $("#search_results").html('');
        hash=j;
        var n=0;
        for(var i=0;i<j.length;i++){
            var a=$.extend([],j[i]);
            var id=a.shift();
            var t=a.join(" ").replace(/\s+/,' ');
            if(t.match(new RegExp(replaceDiacritics(term).toUpperCase()))){
                $("#search_results").append('<a href="javascript:void(0);" codlog="'+id+'">'+t+"</a>");
                n++;
                if(n>=20) break;
            }
        }
        select(selected);
        $('#search_results a').click(function(){
            selected=0;
            var a=$(this);
            $("input[name=search]").val(a.text()+" ");
            $("input[name=codlog]").val(a.attr('codlog'));
            $('#search_results').html('');
            $('input[name=search]').focus();
        });
    };
    $("input[name=search]").keyup(function(e){
        var text=$("input[name=search]").val();
        if(text.length==0) $("#search_results").html('');
        if(term.substr(0,2)==text.substring(0,2)){
            term=text;
            load(hash);
        }else{
            term=text;
            if(term.length<2)return;
            $.ajax('/search',{data:{'term':term,csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()},dataType:'json',method:'post',success:load});
        }
        switch(e.which){
            case 38:
                selected--;
                if(selected<0) selected=$('#search_results').children('a').length-1;
                select(selected);
            break;
            case 40:
                selected++;
                if(selected>$('#search_results').children('a').length-1) selected=0;
                select(selected);
            break;
            case 13:
                var ab=$('#search_results').children('a');
                if(ab.length>0){
                    var a=$(ab[selected]);
                    $("input[name=search]").val(a.text()+" ");
                    $("input[name=codlog]").val(a.attr('codlog'));
                    $('#search_results').html('');
                }else{
                    geocode();
                }
                break;
        }
    });
    $('input[name=adm]').change(function(){
        var w=$(this).val();
        for(var k in layers){
            layers[k].setVisible(false);
        }
        if(!layers[w]){
            if(w!='adm'){
                $.ajax('/vector',{dataType:'json',data:{layer:w},success:function(g){
                    layers[w]=addVector(g,w);
                }});
            }
        }else{
            layers[w].setVisible(true);
        }
    })
    $('input[type=radio],input[type=checkbox],select,input[type=text]').change(function(){
        loadTheme();
    });
    $('input[type=text]').keypress(function(k){
        if(k.keyCode==13) loadTheme();
    });

    $('div#filters_box a').click(function(e){
        if($(e.target).hasClass('inactive')) return;
        $(this).parent().siblings().find('div').hide();
        $(this).parent().find('div').toggle();
    });
    $('input[name=periodo]').click(function(){
        $('select[name=mes]').prop('disabled', !($(this).val()=='mes'));
    });
    $('select[name=mes]').prop('disabled', !($('input[name=periodo]:checked').val()=='mes'));
    fixHeight();
    loadTheme();
    $(window).resize(fixHeight);
}
function setModal(s){
    if(s){
        $('.modal').css('height', ($('body').height()-$('#cabecalho').height()+$('#header').height())+'px');
    }else{
        $('.modal').css('height', 0);
    }
}
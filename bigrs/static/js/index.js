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
    if(!a)return false;
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
    h['csrfmiddlewaretoken']=$('input[name=csrfmiddlewaretoken]').val();
    h['LAYERS']='BIGRS:incidentes_params';
    var ano=h.ano;
    if(points==null){
        $.ajax('/geojson', {data:h,method:'post',dataType:'json',success:function(j){
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
    var d=[new Date(),new Date()];
    d[0].setYear(h.ano);
    d[0].setMonth(0);
    d[0].setDate(1);
    d[0].setHours(0);
    d[0].setMinutes(0);
    d[0].setSeconds(0);
    d[1].setYear(h.ano);
    d[1].setMonth(0);
    d[1].setDate(1);
    d[1].setHours(0);
    d[1].setMinutes(0);
    d[1].setSeconds(0);
    if(h.periodo=='mes'){
        d[1].setMonth(d[1].getMonth()+1);
    }
    if(h.periodo=='ano'){
        d[1].setYear(d[1].getFullYear()+1);
    }
    console.debug(d);
    var t=[
        d[0].getTime()/1000,
        d[1].getTime()/1000
    ];
    console.debug(t);
    points.getFeatures().forEach(function(fu){
        var p=fu.getProperties();
        if(p.tipo_acide && p.tipo_acide.match(h.regex_tipo_acide)){
            if(intersects(p.tipo_veiculo,h.regex_tipo_veiculo)){
                if((p.data_e_hora>t[0])&&(p.data_e_hora<t[1])){
                    features.push(fu);
                }
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
    for(var k in layers){
        layers[k].setVisible(false);
    }
    $("#legenda").hide();
    if(h.adm=='heatmap'){
        $('#filters_box .dados a,#filters_box .contagem a').addClass('inactive');

        setHeatMap();
        return;
    }else{
        $('#filters_box a').removeClass('inactive');

    }
    if((h.adm=='distritos')||(h.adm=='subprefeituras')||(h.adm=='gets')){
        var w=h.adm;

        if(!layers[w]){
            console.debug("não tem o layer "+w);
            if(w!='heatmap'){
                $.ajax('/vector',{dataType:'json',data:{layer:w},success:function(g){
                    isLoadingTheme=false;
                    console.debug('adding a layer');
                    layers[w]=addVector(g,w);
                    loadTheme();
                }});
                return;
            }
        }else{
            layers[w].setVisible(true);
        }
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
        console.debug(s);
        console.debug('features');
        if(s.getFeatures){
            var f=layers[h.adm].getSource().getFeatures();
            console.debug(f);
            for(var i=0;i<f.length;i++){
                f[i].color=theme[f[i].get('gid')];
                console.debug(f[i].color);
            }
            layers[h.adm].getSource().clear();
            layers[h.adm].getSource().addFeatures(f);
        }
        console.debug(j.percentiles);
        $("table#table_legenda").html('');
        var d=getDescription();
        var tr=$('<tr><td colspan="2" class="legenda_text"></td></tr>');
        for(var k in d){
            var sp=$('<span>'+k+': '+d[k]+'</span><br>');
            tr.find('td').append(sp);
        }
        $("table#table_legenda").append(tr);
        for(var i=1;i<j.percentiles.length;i++){
            var tr=$('<tr></tr>');
            var td=$('<td></td>').addClass('legend_color').css('background-color','#'+colors[i-1]);
            tr.append(td);
            if(i==0)
                tr.append($('<td></td>').text(Math.round(j.percentiles[i-1])+' a '+Math.round(j.percentiles[i]))    );
            else
                tr.append($('<td></td>').text('até '+Math.round(j.percentiles[i]))    );
            $("table#table_legenda").append(tr);

        }
        var lp;
        try{
            lp=JSON.parse(getCookie('leg_position'));
        }catch(e){
            lp={"top":60, "left":$('body').width()-300};
        }
        $("#legenda").css('left', lp.left+'px');
        $("#legenda").css('right', lp.left+'px');

        $("#legenda").fadeIn();
        isLoadingTheme=false;
        setModal(isLoadingTheme);
    }});
}

function getStyles(feature, resolution){
console.debug("gettong style");
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
     case 'gets':
        console.debug("estilo da gets")
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
            text: feature.get('descricao'),
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
  /*
  distritos.getSource().on('change',function(e){
    if(distritos.getSource().getState()=='ready'){
        loadTheme();
    }
  })
  */
  console.debug("addding layer");
  console.debug(distritos);

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
    var a;
    if(a=getCookie('adm')){
        $('input[name=adm][value='+a+']').prop('checked',true);
    }

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
        var h=getForm();
        if(h.adm!='heatmap'){
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
                }
                $('.ol-popup-closer').onclick = function() {
                  popup.setPosition(undefined);
                  $('.ol-popup-closer').blur();
                  return false;
                };
                /*else if(f.getProperties().name){ //logradouro
                    $('input[name=feature_id]').val(f.getProperties().codlog)
                    console.debug(f.getProperties());
                    html=html.replace(/\$name/,f.getProperties().name);
                    selected_marker=f;
                    content.innerHTML = html;
                    $(content).find('a.marker_remove').show();
                }*/

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
                //return;
            }else{
                if(featurething && vectorSource){
                    vectorSource.removeFeature(featurething);
                    featurething=null;
                }
            }
        }
        var lonlat = ol.proj.toLonLat(map.getCoordinateFromPixel(e.pixel));

        console.debug(lonlat);
        $.ajax('/reverse',{'method':'post',dataType:'json', data:{point:lonlat,csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()}, success:function(j){
            console.debug(j);
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
    /*$('input[name=adm]').change(function(){
        var w=$(this).val();
        setCookie('adm',w);
        for(var k in layers){
            layers[k].setVisible(false);
        }
        if(!layers[w]){
            if(w!='heatmap'){
                $.ajax('/vector',{dataType:'json',data:{layer:w},success:function(g){
                    console.debug('adding a layer');
                    layers[w]=addVector(g,w);
                }});
            }
        }else{
            layers[w].setVisible(true);
        }
    });*/
    $('input[value=inverter]').change(function(){
        console.debug($(this).closest('.menu').find('input[type=checkbox][value!=inverter]'));
        $(this).closest('.menu').find('input[type=checkbox][value!=inverter]').each(function(){
            $(this).prop('checked',!$(this).is(':checked'));
        });
        loadTheme();
    });
    $('input[type=checkbox][name=tipo_veiculo],input[type=checkbox][name=tipo_acidente]').click(function(){
        loadTheme();
    });

    $('input[type=radio],select,input[type=text]').change(function(){
        setCookie($(this).attr('name'),$(this).val());
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
    var isDragging;
    var offset={};
    $('#legenda').mousedown(function(e){
        offset=$('#legenda').offset();
        offset.left=e.pageX-offset.left;
        offset.top=e.pageY-offset.top;
        isDragging='#legenda';
        $('#drop').show();
    });
    $('#legenda, #drop').mouseup(function(){
        isDragging=null;
        $('#drop').hide();
        setCookie('leg_position',JSON.stringify($('#legenda').offset()));
    });
    $('#legenda').mousemove(function(e){
        if(!isDragging) return;
        console.debug('mi');
        $(isDragging).css('left', (e.pageX-offset.left)+'px');
        $(isDragging).css('top', (e.pageY-offset.top)+'px');
    });
}
function setModal(s){
    if(s){
        $('.modal').css('height', ($('body').height()-$('#cabecalho').height()+$('#header').height())+'px');
    }else{
        $('.modal').css('height', 0);
    }
}
function getDescription(){
    var tipos_de_incidente=[];
    var tipos_de_veiculo=[];
    $('input[name=tipo_acidente]').each(function(){
        if($(this).is(':checked')){
            tipos_de_incidente.push($(this).parent().text());
        }
    });
    $('input[name=tipo_veiculo]').each(function(){
        if($(this).is(':checked')){
            tipos_de_veiculo.push($(this).parent().text());
        }
    });
    return {
        'Divisão':$('input[name=adm]').val(),
        'Dados':$('input[name=tipo]').val(),
        'Período':($('input[name=periodo]').val()=='mes')?$("select[name=mes] option:selected" ).text()+" de "+$('input[name=ano]').val():$('input[name=ano]').val(),
        'Contagem':$('input[name=contagem]').val(),
        'Tipo de incidente':tipos_de_incidente.join(', '),
        'Tipo de veículo':tipos_de_veiculo.join(', ')
    };
}
function setCookie(cookie, value){
    var now = new Date();
    var time = now.getTime();
    var expireTime = time + 1000*36000;
    now.setTime(expireTime);
    document.cookie = cookie+'='+value+';expires='+now.toGMTString()+';path=/';
}
function getCookie(cookie){
    var a=document.cookie.match(new RegExp(cookie+"=([^;]*);?"));
    if(a) return a.pop();
}
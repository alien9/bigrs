var k;
var rasta;
var travels;
var CURRENT_DIRECTION=0;
var pressing=false;
var fila={};
var local_id=1;
var map;
function start(){

    if(typeof MAP_CENTER != "undefined"){
        //map.getView().setZoom(17);
        //map.getView().setCenter(ol.proj.transform(MAP_CENTER, 'EPSG:4326', 'EPSG:3857'));
    }else{
        //map.getView().fit(bounds, map.getSize());
    }
    console.debug(MAP_CENTER);
    latlng=MAP_CENTER;
    var format = 'image/png';
    get_url=function(bounds){
        var res = this.map.getResolution();
        var x = Math.round((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
        var z=this.map.getZoom();
        var y = -1+Math.pow(2,z)+Math.round((bounds.top - this.maxExtent.top) / (res * this.tileSize.h));
        c=this.serviceVersion+"/"+this.layername+"/"+z+"/"+x+"/"+y+"."+this.type;
        return this.url+c;
    }
    var tiled = new OpenLayers.Layer.TMS( "TMS", "http://bigrs.alien9.net:8080/geoserver/gwc/service/tms/",
        {
            layername:'BIGRS%3Aquadras_e_logradouros@3857@png',
            type:'png',
            maxZoomLevel:22,
            minZoomLevel:17,
            getURL:get_url
        }
    );
    map = new OpenLayers.Map( {
        div:'map',
        projection:"EPSG:900913",
        displayProjection:"EPSG:4326",
        resolutions:[
            1.194328566789627,
            0.5971642833948135,
            0.29858214169740677,
            0.14929107084870338
        ]
    });
    map.isValidZoomLevel = function(zoomLevel) {
       return ( (zoomLevel != null) &&
          (zoomLevel >= 17) && // set min level here, could read from property
          (zoomLevel < 22 ));
    }
    map.addLayer(tiled);
    zoom=17;



    var labellayer = new OpenLayers.Layer.WMS( "Labels",
                    "http://bigrs.alien9.net:8080/geoserver/BIGRS/wms",
                    {
                        'FORMAT': 'image/png',
                        'VERSION': '1.1.1',
                        STYLES: 'logradouros labels small',
                        LAYERS: 'BIGRS:labels',
                    isBaselayer: false, transparent: true});
    map.addLayer(labellayer);
    map.setCenter(new OpenLayers.LonLat(MAP_CENTER).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913")), 17);
    vectors = new OpenLayers.Layer.Vector("Travels", {
            styleMap: new OpenLayers.StyleMap({'default':{
                fillOpacity: 0.5,
                pointRadius: 8,
                label : "${name}",
                fontSize: "12px",
                fontFamily: "Courier New, monospace",
                fontWeight: "bold",
                labelAlign: "center",
                labelXOffset: "${xOffset}",
                labelYOffset: "${yOffset}",
                labelOutlineColor: "white",
                labelOutlineWidth: 3
            }})
        });
    map.addLayer(vectors);
    var arrowheads = new OpenLayers.Layer.Vector( "Heads" );
    map.addLayer(arrowheads);
    var i=0;
    features=[];
    vectors.events.register("beforefeatureadded", vectors, function(e){
        e.feature.attributes={name:"_"+(vectors.features.length+1)};
    });
    for(var j=0;j<linhas.length;j++){
        if(linhas[j].geometry!=""){
            var r=linhas[j].geometry;
            var g;
            if(g=r.match(/\((.*)\)/)){
                var pts=g[1].split(/,/);
                if(pts.length>1){
                    var k=0;
                    var points=[];
                    while(k<pts.length){
                        xy=pts[k].split(" ");
                        points.push(new OpenLayers.Geometry.Point(xy[0],xy[1]));
                        k++;
                    }
                    var line = new OpenLayers.Geometry.LineString(points);
                    console.debug(line);
                    var lineFeature = new OpenLayers.Feature.Vector(line, null, {});
                    lineFeature.attributes={name:""+(i+1)};
                    lineFeature.style = {
                        fontFamily: "arial, monospace",
                        fontWeight: "bold",
                        fontColor: "black",
                        label : ""+(i+1),
                        labelAlign: "center",//set to top right
                        labelOutlineColor: "white",
                        labelOutlineWidth: 3,
                        strokeColor:(CURRENT_DIRECTION==i)?'red':'black'
                    };

                    vectors.addFeatures([lineFeature]);
                }
            }
         }
        i++;
    }
    vectors.addFeatures(features);
    drawHeads();
    $('body').keyup(keyup);
    setKeyboard();
    $("#teclado_numerico").focus(function(){
        $("#teclado_numerico").addClass('focus');
    });
    $("#teclado_numerico").blur(function(){
        $("#teclado_numerico").removeClass('focus');
    });

    requestFocus();
    upload();

}
function requestFocus(){
$("#teclado_numerico").focus();
}


function fixHeight(){
    var h=$('body').height();
    $('.main').css('height',h+"px");
    $('video').css('width',($('body').width()-300)+'px')
}
function collectpoints(){
    var i=0;
    features.forEach(function(f){
        var tr;
        if($('#points_table').children().length<=i){
            tr=document.createElement('tr');
            tr.innerHTML='<td>'+(i+1)+'</td><td class="nome"><input type="text" name="latitude"><input type="text" name="longitude"></td>';
            $('#points_table').append(tr);
        }else{
            tr=$('#points_table').children()[i];
        }
        reverse_geocode(ol.proj.transform(f.getGeometry().getCoordinates(), 'EPSG:3857', 'EPSG:4326'),tr);
        i++;
    });
}
function reverse_geocode(p,tr){
    console.log("reverse geocode happening");
    if((p[1]!=$(tr).find('[name=latitude]').val())||(p[0]!=$(tr).find('[name=longitude]').val())){
        $(tr).find('[name=latitude]').val(p[1]);
        $(tr).find('[name=longitude]').val(p[0]);
        $.ajax('/reverse_geocode',{dataType:'json',method:'post', data:{latitude:p[1],longitude:p[0],csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()}, success:function(h){
            if(h.nome.length>0)
                $(tr).find('td.nome').text(h.nome);
            else
                $(tr).find('td.nome').text(" * ");
        }});
    }
}


function drawtext(e){
    return [new ol.style.Style({
            fill: new ol.style.Fill({
                color: 'rgba(255, 255, 255, 0.2)'
            }),
            stroke: new ol.style.Stroke({
                color: '#000000',
                width: 2
            }),
            image: new ol.style.Circle({
                radius: 10,
                fill: new ol.style.Fill({
                  color: '#ffcc33'
                })
            })
        }),new ol.style.Style({
            text: new ol.style.Text({
                text: ""+e.getProperties().alias,
                fill: new ol.style.Fill({
                    color: '#000'
                }),
                scale:1.6
            })
    })];

}
function keyup(e){
    console.log(e.keyCode);
    if(e.keyCode>48 && e.keyCode<58){
        var n=parseInt(e.keyCode-48);
        console.debug(n)
        if(vectors.features[n-1]){
            for(var i=0;i<vectors.features.length;i++){
                vectors.features[i].style.strokeColor='black';
                vectors.redraw();
            }
            vectors.features[n-1].style.strokeColor='red';
            vectors.redraw();
            CURRENT_DIRECTION=n-1;
            drawHeads();
        }
        var od;
        $("#od").text($("#od").text()+n);

        console.log(n);
    }else if((e.keyCode==189)||(e.keyCode==187)){
        $("#od").text($("#od").text()+"→");
    }
    var k;
    switch(e.keyCode){
        case 33:
        case 105:
        //9
        k=9;
        break;
        case 38:
        case 104:
        //8
        k=8;
        break;
        case 36:
        case 103:
        //7
        k=7;
        break;
        case 39:
        case 102:
        //6
        k=6;
        break;
        case 12:
        case 101:
        //5
        k=5;
        break;
        case 37:
        case 100:
        //4
        k=4;
        break;
        case 34:
        case 99:
        //3
        k=3;
        break;
        case 40:
        case 98:
        //2
        k=2;
        break;
        case 35:
        case 97:
        //1
        k=1;
        break;
        case 45:
        case 96:
        //0
        k='0';
        break;
        case 46:
        case 108:
        //.
        k='_';
        break;

        case 75:
            if($("#teclado_numerico").is(":visible"))
                $("#teclado_numerico").fadeOut();
            else
                $("#teclado_numerico").fadeIn();
        break;

        case 90:
            CURRENT_DIRECTION--;
            if(CURRENT_DIRECTION<0)
                CURRENT_DIRECTION=travels.length-1;
            setTravel(travels[CURRENT_DIRECTION]);
        break;
        case 88:
            CURRENT_DIRECTION++;
            if(CURRENT_DIRECTION>=travels.length)
                CURRENT_DIRECTION=0;
            setTravel(travels[CURRENT_DIRECTION]);
        break;
        default:
        break;
    }
    if(k!=null){
        if(pressing)
            return;
        pressing=true;
        $('.t'+k).css({'backgroundColor':'white'});
        $('.t'+k).stop().animate({'backgroundColor':'#aaa'}, {
            duration:100,
            complete:function(){
                pressing=false;
            }
        });
        var p = videojs('my-video');
        var t;
        if(t=$(".t"+k).attr('tipo')){
            if(!contado[t])contado[t]=0;
            var veiculo={
                ts:p.currentTime(),
                spot_id:linhas[CURRENT_DIRECTION].id,
                tipo:t,
                local_id:local_id,
                contagem_id:contagem_id
            };
            contado[t]++;
            fila[local_id]=veiculo;
            local_id++;
            setContagem();
        }
    }
}
function getOd(){
    var a;
    if(a=$("#od").text().split(/\s*→\s*/))
        return a;
    return null;
}

function setTravel(p){
    var t=p.origin[3]+" → "+p.destin[3];
    $("#od").text(t);
}
function setKeyboard(){
    $(".subtecla").css("class","subtecla");
    $(".tecla").removeAttr('tipo');
    for(var k in tipos){
        $(".t"+k+" .subtecla").addClass(tipos[k]);
        $(".t"+k).attr('tipo',tipos[k]);
    }
}
function setContagem(){
    for(var tipo in contado){
        $("#contagem-"+tipo).text(contado[tipo]);
    }
}
function upload(){
    $.ajax('/conta',{method:'POST',data:{fila:JSON.stringify(fila),csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()},success:function(h){
        for(var local_id in h){
            delete(fila[local_id]);
        }
        setTimeout(upload,3000);
    }});
}

function drawHeads(){
    var feat=[];
    var arrowheads=map.getLayersByName("Heads")[0];
    arrowheads.destroyFeatures();
    for(var i=0;i<vectors.features.length;i++){
        var v=vectors.features[i];
        if(v.geometry && v.geometry.components && (v.geometry.components.length>1)){
            var p=[v.geometry.components[v.geometry.components.length-2],v.geometry.components[v.geometry.components.length-1]];
            var modulus=Math.sqrt(Math.pow(p[1].y-p[0].y,2.0)+Math.pow(p[1].x-p[0].x,2.0));
            var size=10*map.getResolution();
            var dx=size*(p[1].x-p[0].x)/modulus;
            var dy=size*(p[1].y-p[0].y)/modulus;
            var a=[p[1].x-dx,p[1].y-dy]; //centro da base da cabeça
            var mu=0.5;
            var avb=[dy*mu,-1*dx*mu];
            mu=-0.5;
            var amb=[dy*mu,-1*dx*mu]
            var b=[a[0]+amb[0],a[1]+amb[1]];
            var c=[a[0]+avb[0],a[1]+avb[1]];
            var linearRing = new OpenLayers.Geometry.LinearRing([
                new OpenLayers.Geometry.Point(
                    p[1].x,p[1].y
                ),
                new OpenLayers.Geometry.Point(
                    b[0],b[1]
                ),
                new OpenLayers.Geometry.Point(
                    c[0],c[1]
                )
            ]);
            var geometry = new OpenLayers.Geometry.Polygon([linearRing]);
            var polygonFeature = new OpenLayers.Feature.Vector(geometry, null, {});
            if(CURRENT_DIRECTION==i){
                polygonFeature.style.fillColor='red';
                polygonFeature.style.strokeColor='red';
            }
            arrowheads.addFeatures([polygonFeature]);
        }
    }
}
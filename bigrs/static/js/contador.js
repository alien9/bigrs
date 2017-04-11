var k;
var rasta;
var travels;
var CURRENT_DIRECTION=0;
var pressing=false;
var fila={};
var local_id=1;
function start(){
    fixHeight();
    $( window ).resize(fixHeight);
    k=$('.control').offset().left;
    $('.control').mousedown(function(e){
        rasta=true;
    });
    $('body').mouseup(function(){
        rasta=false;
    });
    $("body,#slider").mousemove(function(e){
        if(!rasta) return;
        var left=e.pageX-$("#slider").offset().left-$('.control').width()/2;
        if(left<0) left=0;
        if(left>$("#slider").width()-$('.control').width())left=$("#slider").width()-$('.control').width();
        $('.control').css('left',left);
        setSpeed(left/($('#slider').width()-$('.control').width()));
    });
    var bounds = [-5213822.973694572, -2738592.792872979,
                    -5160539.474795484, -2674513.9204534707];
    var format = 'image/png';
    var tiled = new ol.layer.Tile({
    source: new ol.source.TileWMS({
          url: 'http://bigrs.alien9.net:8080/geoserver/BIGRS/wms',
          params: {'FORMAT': format,
                   'VERSION': '1.1.1',
                   tiled: true,
                STYLES: '',
                LAYERS: 'BIGRS:quadras_e_logradouros',
             tilesOrigin: -5213822.973694572 + "," + -2738592.792872979
          }
        })
    });
    var untiled = new ol.layer.Image({
        source: new ol.source.ImageWMS({
            ratio: 1,
            url: 'http://bigrs.alien9.net:8080/geoserver/BIGRS/wms',
            params: {'FORMAT': format,
                   'VERSION': '1.1.1',
                STYLES: 'logradouros labels small',
                LAYERS: 'BIGRS:labels',
            }
        })
    });
    var projection = new ol.proj.Projection({
      code: 'EPSG:3857',
      units: 'm',
      axisOrientation: 'neu'
    });

    //var
    map = new ol.Map({
        controls: [],//.extend([mousePositionControl]),
        target: 'map',
        layers: [
            tiled,untiled
        ],
        view: new ol.View({
            projection: projection
        }),
        interaction: ol.interaction.defaults({
            doubleClickZoom :false,
            dragAndDrop: false,
            keyboardPan: false,
            keyboardZoom: false,
            mouseWheelZoom: false,
            pointer: false,
            select: false
        })
    });
    //var
    features = new ol.Collection();
    var vectorSource=new ol.source.Vector({features: features});
    //var
    featureOverlay = new ol.layer.Vector({
        source: vectorSource,
        style: drawtext
    });
    featureOverlay.setMap(map);
    for(var i=0;i<pontos.length;i++){
        var thing = new ol.geom.Point([pontos[i][0],pontos[i][1]]);
        var featurething = new ol.Feature({
            label: pontos[i][3],
            geometry: thing
        });
        vectorSource.addFeature( featurething );
    }
    if(typeof MAP_CENTER != "undefined"){
        map.getView().setZoom(17);
        map.getView().setCenter(ol.proj.transform(MAP_CENTER, 'EPSG:4326', 'EPSG:3857'));
    }else{
        map.getView().fit(bounds, map.getSize());
    }
    $('body').keyup(keyup);
    travels=[];
    for(var i=0;i<pontos.length;i++){
        for(var j=0;j<pontos.length;j++){
            if (i!=j){
                var h={
                    'origin':pontos[i],
                    'destin':pontos[j],
                };
                console.debug(h);
                travels.push({
                    'origin':pontos[i],
                    'destin':pontos[j]
                });
            }
        }
    }
    setTravel(travels[CURRENT_DIRECTION]);
    setKeyboard();
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
    console.debug(e);
    return [new ol.style.Style({
            fill: new ol.style.Fill({
                color: 'rgba(255, 255, 255, 0.2)'
            }),
            stroke: new ol.style.Stroke({
                color: '#ffcc33',
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
                text: ""+e.getProperties().label,
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
        var n=e.keyCode-48;
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
                origem:travels[CURRENT_DIRECTION].origin[4],
                destino:travels[CURRENT_DIRECTION].destin[4],
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
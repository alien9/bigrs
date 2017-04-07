var k;
var rasta;
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
                STYLES: '',
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
    //var
    featureOverlay = new ol.layer.Vector({
        source: new ol.source.Vector({features: features}),
        style: drawtext
    });
    featureOverlay.setMap(map);
    var modify = new ol.interaction.Modify({
        features: features,
        // the SHIFT key must be pressed to delete vertices, so
        // that new vertices can be drawn at the same position
        // of existing vertices
        deleteCondition: function(event) {
          return ol.events.condition.shiftKeyOnly(event) &&
              ol.events.condition.singleClick(event);
        }
    });

    features.on("add", function (e) {
        e.element.label=""+(features.getLength());
        collectpoints();
    });


    map.addInteraction(modify);
    modify.on('modifyend', function(e) {
        collectpoints();
    });


    var draw; // global so we can remove it later

    function addInteraction() {
        draw = new ol.interaction.Draw({
          features: features,
          type: "Point"
        });
        map.addInteraction(draw);
    }

    var dragPan;
    map.getInteractions().forEach(function(interaction) {
      if (interaction instanceof ol.interaction.DragPan) {
        dragPan = interaction;
      }
    }, this);
    if (dragPan) {
      map.removeInteraction(dragPan);
    }
    /**
    * Handle change event.
    */

    addInteraction();

    if(typeof MAP_CENTER != "undefined"){
        map.getView().setCenter(ol.proj.transform(MAP_CENTER, 'EPSG:4326', 'EPSG:3857'));
        map.getView().setZoom(18);
    }else{
        map.getView().fit(bounds, map.getSize());
    }
    $('body').keyup(keyup);
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
            $(tr).find('td.nome').text(h.nome);
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
                radius: 7,
                fill: new ol.style.Fill({
                  color: '#ffcc33'
                })
            })
        }),new ol.style.Style({
            text: new ol.style.Text({
                text: ""+e.label,
                fill: new ol.style.Fill({
                    color: '#fff'
                })
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

    switch(e.keyCode){
        default:
        break;
    }
}
function getOd(){
    var a;
    if(a=$("#od").text().split(/\s*→\s*/))
        return a;
    return null;
}
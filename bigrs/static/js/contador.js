var k;
var rasta;
function start(){
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
//http://bigrs.alien9.net:8080/geoserver/BIGRS/wms?service=WMS&version=1.1.0&request=GetMap&layers=BIGRS:sirgas_shp_quadraviaria_&styles=&bbox=313086.375,7360294.0,361095.90625,7416448.5&width=656&height=768&srs=EPSG:31983&format=application/openlayers
    var map = new ol.Map({
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

        target: 'map',
        controls: ol.control.defaults({
          attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
            collapsible: false
          })
        }),
        view: new ol.View({
          center: [0, 0],
          zoom: 2
        })
      });

}
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
    var projection = new ol.proj.Projection({
      code: 'EPSG:3857',
      units: 'm',
      axisOrientation: 'neu'
    });
    var map = new ol.Map({
        controls: ol.control.defaults({
            attribution: false
        }),//.extend([mousePositionControl]),
        target: 'map',
        layers: [
            tiled
        ],
        view: new ol.View({
            projection: projection
        })
    });
    map.getView().fit(bounds, map.getSize());
}

function fixHeight(){
    var h=$('body').height();
    console.log(h+"px");
    $('.main').css('height',h+"px");
}
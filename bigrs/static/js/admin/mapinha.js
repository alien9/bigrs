(function($) {

function reverse_geocode(p,tr){
console.debug(tr);
    $.ajax('/reverse_geocode',{dataType:'json',method:'post', data:{latitude:p.lat,longitude:p.lon,csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()}, success:function(h){
        $(tr).val(h.nome);
    }});
}
$(document).ready(function(){
    latlng=MAP_CENTER.match(/(-?[\d\.]+) (-?[\d\.]+)/);
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
        div:'submap',
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

    geodjango_location.layers.vector.events.register("featureadded",geodjango_location.layers.vector, function(e){
        var g=e.feature.geometry;
        map.setCenter(new OpenLayers.LonLat(g.x,g.y).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913")), 17);
    });

    layer = new OpenLayers.Layer.WMS( "OpenLayers WMS",
                    "http://vmap0.tiles.osgeo.org/wms/vmap0",
                    {
                        layers: 'BIGRS:labels',
                        styles: 'logradouros labels small'
                    } );
    map.addLayer(layer);

    vectors = new OpenLayers.Layer.Vector("Points", {
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
    var i=0;
    features=[];
    while($("#spot_set-"+i).length){
        if($("#id_spot_set-"+i+"-x").val()!=""){
             features.push(new OpenLayers.Feature.Vector(
                        new OpenLayers.Geometry.Point(
                            $("#id_spot_set-"+i+"-x").val(),$("#id_spot_set-"+i+"-y").val()
                        ), {
                            type: 5 + parseInt(5 * Math.random()),
                            name:i+1
                        }
                    )
             );
         }
        i++;
    }
    vectors.addFeatures(features);

    dc=new OpenLayers.Control.DrawFeature(vectors, OpenLayers.Handler.Point);
    map.addControl(dc);
    dc.activate();
    map.setCenter(new OpenLayers.LonLat(latlng[1],latlng[2]).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913")), zoom);
    vectors.events.register("beforefeatureadded", vectors, function(e){
        e.feature.attributes={name:vectors.features.length+1};
    });
    vectors.events.register("featureadded", vectors, function(e){
        console.debug(e.feature.geometry);
        var i=vectors.features.length-1;
        $('#id_spot_set-'+i+'-x').val(e.feature.geometry.x);
        $('#id_spot_set-'+i+'-y').val(e.feature.geometry.y);
        $('#spot_set-group table td[colspan=6] a').click();
        $('#id_spot_set-'+i+'-alias').val(i+1);
        $("#id_spot_set-"+i+"-DELETE").prop('checked', false);
        reverse_geocode(new OpenLayers.LonLat(e.feature.geometry.x,e.feature.geometry.y).transform(new OpenLayers.Projection("EPSG:900913"),new OpenLayers.Projection("EPSG:4326")),'#id_spot_set-'+i+'-endereco');
    })
    $("#clean_submap").click(function(){
        vectors.destroyFeatures();
        var i=0;
        while($("#id_spot_set-"+i+"-DELETE").length){
            if($("#id_spot_set-"+i+"-x").val()!=""){
                $("#id_spot_set-"+i+"-DELETE").prop('checked', true);
            }
            i++;
        }
    });
    $("#undo").click(function(){
        var fu=features.pop();
        vectors.removeFeatures(fu);
        var i=fu.attributes.name-1;
        $("#id_spot_set-"+i+"-DELETE").prop('checked', true);
    });

});
})(django.jQuery);

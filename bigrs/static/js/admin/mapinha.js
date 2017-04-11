(function($) {

function reverse_geocode(p,tr){
console.debug(tr);
    $.ajax('/reverse_geocode',{dataType:'json',method:'post', data:{latitude:p.lat,longitude:p.lon,csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()}, success:function(h){
        console.debug("GEOCODED");
        console.debug(h);
        if(h.nome.length){
            if(h.nome[0].length)
                $(tr).val(h.nome[0]);
            else
                $(tr).val(' * ');
        }else{
            $(tr).val(' * ');
        }
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
    var arrowheads = new OpenLayers.Layer.Vector( "Heads" );
    map.addLayer(arrowheads);
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

    dc=new OpenLayers.Control.DrawFeature(vectors, OpenLayers.Handler.Path);
    map.addControl(dc);
    dc.activate();
    if(!latlng)
        latlng=[-23,5486,-46,6392];
    map.setCenter(new OpenLayers.LonLat(latlng[1],latlng[2]).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913")), zoom);
    vectors.events.register("beforefeatureadded", vectors, function(e){
        e.feature.attributes={name:vectors.features.length+1};
    });
    vectors.events.register("featureadded", vectors, function(e){
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
        var fu=vectors.features.pop();
        console.debug(fu);
        var i=fu.attributes.name-1;
        console.debug(i);
        vectors.removeFeatures(fu);
        $("#id_spot_set-"+i+"-DELETE").prop('checked', true);
        $("#spot_set-"+i+" .inline-deletelink").click();
    });

});
})(django.jQuery);
function drawHeads(){
    var feat=[];
    for(var i=0;i<vectors.features.length;i++){
        var v=vectors.features[i];
        if(v.geometry && v.geometry.components && (v.geometry.components.length>1)){
            var p=[v.geometry.components[v.geometry.components.length-2],v.geometry.components[v.geometry.components.length-1]];
            console.debug(p);
            var m=(p[1].y-p[0].y)/(p[1].x-p[0].x);


            var modulus=Math.sqrt(Math.pow(p[1].y-p[0].y,2.0)+Math.pow(p[1].x-p[0].x,2.0));
            console.debug(modulus);

            var size=10;
            var dx=10*(p[1].x-p[0].x)/modulus;
            var dy=10*(p[1].y-p[0].y)/modulus;
            console.debug(dx);
            console.debug(dy);
            var a=[p[1].x-dx,p[1].y-dy];
            var mu=1
            var avb=[dy*mu,-1*dx*mu];
            mu=-1;
            var amb=[dy*mu,-1*dx*mu]

            var b=[a[0]+amb[0],a[1]+amb[1]];
            var c=[a[0]+avb[0],a[1]+avb[1]];


console.debug([dx,dy]);
console.debug(avb);
console.debug(amb);

            feat.push(new OpenLayers.Feature.Vector(
                new OpenLayers.Geometry.Point(
                    p[1].x-dx,p[1].y-dy
                ), {
                    type: 5 + parseInt(5 * Math.random()),
                    name:i+1
                })
             );
             feat.push(new OpenLayers.Feature.Vector(
                new OpenLayers.Geometry.Point(
                    b[0],b[1]
                ), {
                    type: 5 + parseInt(5 * Math.random()),
                    name:i+1
                })
             );
             feat.push(new OpenLayers.Feature.Vector(
                new OpenLayers.Geometry.Point(
                    c[0],c[1]
                ), {
                    type: 5 + parseInt(5 * Math.random()),
                    name:i+1
                })
             );
        }
    }
    var arrowheads=map.getLayersByName("Heads")[0];
    arrowheads.addFeatures(feat);
}
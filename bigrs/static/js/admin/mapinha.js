(function($) {

function reverse_geocode(p,tr){
    $.ajax('/reverse_geocode',{dataType:'json',method:'post', data:{latitude:p.lat,longitude:p.lon,csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()}, success:function(h){
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
    zoom=parseInt($("#id_zoom").val());
    var labellayer = new OpenLayers.Layer.WMS( "Labels",
                    "http://bigrs.alien9.net:8080/geoserver/BIGRS/wms",
                    {
                        'FORMAT': 'image/png',
                        'VERSION': '1.1.1',
                        STYLES: 'logradouros labels small',
                        LAYERS: 'BIGRS:labels',
                    isBaselayer: false, transparent: true});
    map.addLayer(labellayer);

    geodjango_location.layers.vector.events.register("featureadded",geodjango_location.layers.vector, function(e){
        var g=e.feature.geometry;
        map.setCenter(new OpenLayers.LonLat(g.x,g.y).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913")), 17);
    });

    vectors = new OpenLayers.Layer.Vector("Travels", {
            styleMap: new OpenLayers.StyleMap({'default':{
                fillOpacity: 0.5,
                pointRadius: 8,
                label : "${label}",
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
        var vid=vectors.features.length;
        var f;
        var attrs={};
        if(f=$('#id_spot_set-'+vid+'-alias')){
            attrs.label=$('#id_spot_set-'+vid+'-alias').val();
        }
        attrs.name=""+(vectors.features.length+1);
        e.feature.attributes=attrs;

    });
    var sty=function(i) {
        var label=$('#id_spot_set-'+i+'-alias').val();
        return {
            fontFamily: "arial, monospace",
            fontWeight: "bold",
            fontColor: "black",
            label : label,
            labelAlign: "center",//set to top right
            labelOutlineColor: "white",
            labelOutlineWidth: 3
        };
    };

    while($("#spot_set-"+i).length){
        if($("#id_spot_set-"+i+"-geometry").val()!=""){
            var r=$("#id_spot_set-"+i+"-geometry").val();
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
                    lineFeature.attributes={label:$("#id_spot_set-"+i+"-alias").val(),name:""+(vectors.features.length)};
                    lineFeature.style = sty(vectors.features.length);
                    vectors.addFeatures([lineFeature]);
                }
            }
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
    drawHeads();

    vectors.events.register("featureremoved", vectors, function(e){
        drawHeads();
    });
    vectors.events.register("featureadded", vectors, function(e){
        var i=vectors.features.length-1;
        $('#id_spot_set-'+i+'-geometry').val(e.feature.geometry);
        $('#id_spot_set-'+i+'-alias').val(i+1);
        $("#id_spot_set-"+i+"-DELETE").prop('checked', false);
        if(e.feature.geometry.components && e.feature.geometry.components.length>1){
            reverse_geocode_line([
                e.feature.geometry.components[e.feature.geometry.components.length-1],
                e.feature.geometry.components[0],
            ],[
                "#id_spot_set-"+i+"-endereco_destino",
                "#id_spot_set-"+i+"-endereco_origem"
            ]);
        }
        $("id_spot_set-"+i+"-geom").val(e.feature.geometry);
        console.debug(e.feature.geometry);
        drawHeads();
    });
    var reverse_geocode_line=function(ps,textareas){
        var p=ps.pop();
        var field=textareas.pop();
        p=new OpenLayers.LonLat(p.x,p.y).transform(new OpenLayers.Projection("EPSG:900913"), new OpenLayers.Projection("EPSG:4326"));
        $.ajax('/reverse_geocode',{dataType:'json',method:'post', data:{latitude:p.lat,longitude:p.lon,csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()}, success:function(h){
            console.debug(h);
            if(h.nome.length){
                if(h.nome[0].length)
                    $(field).val(h.nome[0]);
                else
                    $(field).val(' * ');
            }else{
                $(field).val(' * ');
            }
            if(ps.length){
                reverse_geocode_line(ps,textareas);
            }
        }});
    };


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
        var fu;
        if(!(fu=vectors.features.pop())) return;
        console.debug(fu);
        var i=fu.attributes.name-1;
        console.debug(i);
        vectors.removeFeatures(fu);
        $("#id_spot_set-"+i+"-DELETE").prop('checked', true);
        $("#spot_set-"+i+" .inline-deletelink").click();
    });
    map.events.register("zoomend", map, function(e){
        drawHeads();
        $("#id_zoom").val(map.getZoom());
    });
});
})(django.jQuery);
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
            arrowheads.addFeatures([polygonFeature]);
        }
    }
}
from django.contrib import admin
from django.contrib.gis.admin.options import GeoModelAdmin

# Register your models here.
from maps.models import *

class ContagemAdmin(GeoModelAdmin):
    list_display = ('endereco',)
    default_lon = -46.5
    default_lat = -23.5
    wms_name = "Quadra Viária"
    wms_url = "http://bigrs.alien9.net:8080/geoserver/BIGRS/wms"
    wms_layer = "BIGRS:sirgas_shp_quadraviaria_"
    default_zoom = 16
    units=True
    num_zoom = 18
admin.site.register(Contagem,ContagemAdmin)
from django.contrib import admin

# Register your models here.
from maps.models import *

class ContagemAdmin(admin.ModelAdmin):
    list_display = ('endereco',)

admin.site.register(Contagem,ContagemAdmin)
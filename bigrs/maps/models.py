from django.db import models
from django.contrib.gis.db import models as gis_models

class Contagem(models.Model):
    class Meta:
        verbose_name_plural = "Contagens"
    author = models.ForeignKey('auth.User')
    data_e_hora_inicio=models.DateTimeField(auto_now_add=True, blank=True)
    endereco=models.TextField(max_length = 100)
    data_e_hora_final = models.DateTimeField(null=True)
    movie = models.FileField(upload_to='static/video', null=True)
    location=gis_models.PointField(srid=4326,blank=True,null=True)

class Contado(models.Model):
    author = models.ForeignKey('auth.User')
    contagem=models.ForeignKey(Contagem)
    tipo=models.TextField(max_length=100)
    data_e_hora_final = models.DateTimeField(auto_now_add=True, blank=True)

class Spot(models.Model):
    contagem=models.ForeignKey(Contagem)
    location = gis_models.PointField(srid=4326)
    endereco = models.TextField(max_length=100)
    alias = models.TextField(max_length=10)


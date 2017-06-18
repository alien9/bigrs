from django.db import models
from django.contrib.gis.db import models as gis_models
import exifread,ffmpy,re,os
from django.core.files.base import File

class Bairro(models.Model):
    nome=models.TextField(max_length=100)

class Contagem(models.Model):
    class Meta:
        verbose_name_plural = "Contagens"
    endereco=models.TextField(max_length = 100)
    location=gis_models.PointField(srid=4326,blank=True,null=True)
    bairro=models.ForeignKey(Bairro,null=True)

class Movie(models.Model):
    class Meta:
        verbose_name_plural = "Vídeos"
    contagem=models.ForeignKey(Contagem)
    data_e_hora_inicio = models.DateTimeField()
    movie = models.FileField(upload_to='static/video', null=True)
    is_contado=models.BooleanField(default=False)

class Contado(models.Model):
    author = models.ForeignKey('auth.User')
    contagem=models.ForeignKey(Contagem)
    movie=models.ForeignKey(Movie)
    tipo=models.TextField(max_length=100)
    timestamp=models.IntegerField()
    data_e_hora = models.DateTimeField()
    spot=models.ForeignKey("Spot")

class Spot(models.Model):
    contagem=models.ForeignKey(Contagem)
    endereco_origem = models.TextField(max_length=100)
    endereco_destino = models.TextField(max_length=100)
    alias = models.TextField(max_length=10)
    geometry=models.TextField(max_length=2000)
    bi=models.BooleanField(default=False)
    keys = models.ManyToManyField("Key", blank=True)

class Key(models.Model):
    def __str__(self):
        return self.name
    name=models.TextField(max_length=50)
    icon=models.TextField(max_length=100)

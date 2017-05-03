from django.db import models
from django.contrib.gis.db import models as gis_models
import exifread,ffmpy,re,os
from django.core.files.base import File

class Contagem(models.Model):
    class Meta:
        verbose_name_plural = "Contagens"
    author = models.ForeignKey('auth.User')
    data_e_hora_inicio=models.DateTimeField(auto_now_add=True, blank=True)
    endereco=models.TextField(max_length = 100)
    data_e_hora = models.DateTimeField()
    movie_clip = models.FileField(upload_to='static/video', null=True)
    location=gis_models.PointField(srid=4326,blank=True,null=True)
    def save(self):
        p = re.compile('\.ASF$')
        super(Contagem,self).save()
        if p.search(self.movie.path):
            old_path=self.movie.path
            new_path=re.sub(p,'.mp4',self.movie.path)
            ff = ffmpy.FFmpeg(inputs={old_path:None},outputs={new_path:None})
            ff.run()
            self.movie.save(os.path.basename(new_path), File(open(new_path ,"rb")), save=True)
            os.remove(old_path)
            self.save()

class Movie(models.Model):
    class Meta:
        verbose_name_plural = "Vídeos"
    contagem=models.ForeignKey(Contagem)
    data_e_hora_inicio = models.DateTimeField(auto_now_add=True, blank=True)
    movie = models.FileField(upload_to='static/video', null=True)


class Contado(models.Model):
    author = models.ForeignKey('auth.User')
    contagem=models.ForeignKey(Contagem)
    tipo=models.TextField(max_length=100)
    data_e_hora = models.DateTimeField()
    spot=models.ForeignKey("Spot")

class Spot(models.Model):
    contagem=models.ForeignKey(Contagem)
    endereco_origem = models.TextField(max_length=100)
    endereco_destino = models.TextField(max_length=100)
    alias = models.TextField(max_length=10)
    geometry=models.TextField(max_length=2000)
    keys = models.ManyToManyField("Key", blank=True)

class Key(models.Model):
    def __str__(self):
        return self.name
    name=models.TextField(max_length=50)
    icon=models.TextField(max_length=100)

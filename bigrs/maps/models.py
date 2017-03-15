from django.db import models

class Contagem(models.Model):
    class Meta:
        verbose_name_plural = "Contagens"
    author = models.ForeignKey('auth.User')
    data_e_hora_inicio=models.DateTimeField(auto_now_add=True, blank=True)
    endereco=models.TextField(max_length = 100)
    data_e_hora_final = models.DateTimeField(null=True)
    nome_do_arquivo=models.TextField(max_length=100)
    movie = models.FileField(upload_to='static/video', null=True)

class Contado(models.Model):
    author = models.ForeignKey('auth.User')
    contagem=models.ForeignKey(Contagem)
    tipo=models.TextField(max_length=100)
    data_e_hora_final = models.DateTimeField(auto_now_add=True, blank=True)



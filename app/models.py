from __future__ import unicode_literals
import datetime
from enum import unique
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.contrib.postgres.fields import ArrayField
from datetime import date

# Create your models here.
class User(AbstractUser):
    TIPO_USUARIO = (
        ('CLIENTE', 'cliente'),
        ('ENTRENADOR', 'entrenador'),
    )
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True, null=True)
    points = models.IntegerField(default=0)
    avatar = models.ImageField(null=True, default="avatar.svg")
    tipo = models.CharField(max_length=10,choices=TIPO_USUARIO, default='CLIENTE')


class Ejercicio(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=200)

    def __str__(self) -> str:
        return str(self.id)    # Apareceran con el nombre en la pestaña de admin
    

class RutinaPorDefecto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200, null="False", unique="true")
    series = models.IntegerField(default=0)
    def __str__(self) -> str:
        return self.nombre


class EjercicioRutinaPorDefecto(models.Model):
    id = models.AutoField(primary_key=True)
    rutina = models.ForeignKey(RutinaPorDefecto, on_delete=models.CASCADE)
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    repeticiones = models.IntegerField(default=0)

    def __str__(self) -> str:
        return getattr(self.ejercicio, 'nombre')


class Rutina(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200, null="False")
    series = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)

    class Meta:
        unique_together = ('nombre', 'user')
    def __str__(self) -> str:
        return self.nombre


class EjercicioRutina(models.Model):
    id = models.AutoField(primary_key=True)
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE)
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    repeticiones = models.IntegerField(default=0)
    #tiempo = models.IntegerField(default=0)
    #descanso = models.IntegerField(default=0)
    #fecha = models.DateField(auto_now=True)

    def __str__(self) -> str:
        return getattr(self.ejercicio, 'nombre')   # Devuelve el nombre del logro


class DescripcionLogro(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200, unique=True)
    nivel1 = models.CharField(max_length=2000)
    nivel2 = models.CharField(max_length=2000)
    nivel3 = models.CharField(max_length=2000)
    tiempo = models.CharField(max_length=20)

    def __str__(self) -> str:
        return str(self.id)     # Devuelve el id


class Logro(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion_logro = models.ForeignKey(DescripcionLogro, on_delete=models.CASCADE)
    nivel = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    en_curso = models.IntegerField(default=0)
    class Meta:
        unique_together = ('descripcion_logro', 'user')

    def __str__(self) -> str:
        return getattr(self.descripcion_logro, 'nombre')   # Devuelve el nombre del logro


class DescripcionReto(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion_logro = models.ForeignKey(DescripcionLogro, on_delete=models.CASCADE)
    nivel1 = models.CharField(max_length=2000)
    nivel2 = models.CharField(max_length=2000)
    nivel3 = models.CharField(max_length=2000)
    valor1 = models.IntegerField(default=1, null=False) # Num de repeticiones
    valor2 = models.IntegerField(default=1, null=False)
    valor3 = models.IntegerField(default=1, null=False)
   
    def __str__(self) -> str:
        return str(self.id)    


class EjercicioReto(models.Model):
    id = models.AutoField(primary_key=True)
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    descripcion_reto = models.ForeignKey(DescripcionReto, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return getattr(self.ejercicio, 'nombre')   # Devuelve el nombre del ejercicio


class Reto(models.Model):
    id = models.AutoField(primary_key=True)
    logro = models.ForeignKey(Logro, on_delete=models.CASCADE)
    descripcion_reto = models.ForeignKey(DescripcionReto, on_delete=models.CASCADE)
    nivel = models.IntegerField(default=1, null=False)
    inicio = models.DateField(default = datetime.date.today,blank=False)
    fin = models.DateField(default = datetime.date.today, blank=False)
    conseguido = models.DateField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)

    class Meta:
        unique_together = ('logro', 'user')
        
    def is_past_due(self):
        return date.today() > self.fin  # Devuelve true si ya pasó la fecha de fin

    def __str__(self) -> str:
        logro = getattr(self.logro,'descripcion_logro')
        return logro.nombre    # Devuelve el nombre del logro al que está asociado  
      
      
class Repeticion(models.Model):
    id = models.AutoField(primary_key=True)
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    repeticiones = models.IntegerField(default=1, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)

    class Meta:
        unique_together = ('ejercicio', 'user')
        
    def str(self) -> str:
        return str(self.repeticiones)


class Room(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=2000, unique=True, blank=False)
    nombre_display = models.CharField(max_length=2000, blank=False)
    descripcion = models.CharField(max_length=2000, blank=False)
    def str(self) -> str:
      return str(self.nombre)

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    #end_time = models.DateTimeField()
    useremail = models.EmailField()
    @property
    def get_html_url(self):
        url = reverse('event_edit', args=(self.id,))
        return f'<a href="{url}"> {self.title} </a>'


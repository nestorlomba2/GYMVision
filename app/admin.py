from django.contrib import admin
from .models import Ejercicio, Rutina, EjercicioRutina, RutinaPorDefecto, EjercicioRutinaPorDefecto, User, Reto, DescripcionReto, EjercicioReto, Logro, DescripcionLogro, Repeticion, Room, Event

# Register your models here.
admin.site.register(Ejercicio)
admin.site.register(Rutina)
admin.site.register(EjercicioRutina)
admin.site.register(RutinaPorDefecto)
admin.site.register(EjercicioRutinaPorDefecto)
admin.site.register(User)
admin.site.register(Reto)
admin.site.register(Event)
admin.site.register(DescripcionReto)
admin.site.register(EjercicioReto)
admin.site.register(Logro)
admin.site.register(DescripcionLogro)
admin.site.register(Repeticion)
admin.site.register(Room)

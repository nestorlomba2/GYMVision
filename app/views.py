
from urllib import request
from matplotlib.style import context
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from .Biceps_curl import biceps_curl
from .Elevaciones_frontales import elevaciones_frontales
from .Zancadas import zancadas
from .Elevaciones_laterales import elevaciones_laterales
from .Extension_triceps import extension_triceps
from .Sentadillas import sentadillas
import re
from django.views.generic import TemplateView, ListView
from matplotlib.style import context
from .forms import CreateUserForm, Rutina_personalizada, UserForm, Ejercicio_rutina_personalizada, CreateRoom, EventForm
from .models import *
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm, Rutina_personalizada, Ejercicio_rutina_personalizada, InicializarLogro, CrearReto, ActualizarRepeticiones
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control, never_cache
from django.core.cache import cache
from django.urls import reverse_lazy
from django.contrib.sessions.models import Session
from .utils import Calendar
from django.utils.safestring import mark_safe
import json
import websockets
import asyncio
import calendar
from django.db.models import Q  # Permite multiples condiciones en el exclude
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


def offline_layout(request):
    return render(request, 'offline.html')

  
################################ Pagina principal ################################
@login_required(login_url='login')
def home_page(request):
    cache.clear()
    context = {}
    return render(request, 'home.html', context)


################################ Login, register, logout ################################
def login_page(request):

    #clear cache from session
    cache.clear()
    # cache.clear()
    # cache.delete('session_id')
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']

            try:
                user = User.objects.get(username=username)
                
            except:
                messages.error(request, 'Username does not exist')
                return redirect('login')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # request.session['username'] = username
                return redirect('home')
            else:
                messages.info(request, 'Username or password is incorrect')
                return redirect('login')
        else:        
            context = {}
            return render(request, 'login.html', context)


def register_page(request):    
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)
                user = User.objects.get(username=user).id

                for i in range(1, 15):
                    #Inicializamos los logros en la base de datos con la info del nivel
                    logro_form = InicializarLogro({'descripcion_logro': i, 'nivel': 1, 'user': user, 'en_curso': 0})
                    if logro_form.is_valid():
                        # print("Guardado logro")
                        logro_form.save()
                    else:
                        print(user)
                        print(logro_form.errors)
                        print("Error en el formulario logro")

               
                for j in range(1, 8):
                    #Inicializamos las repeticiones a 0
                    reps_form = ActualizarRepeticiones({'ejercicio': j, 'repeticiones': 0, 'user': user})
                    if reps_form.is_valid():
                        reps_form.save()
                        # print("Guardado reps")
                    else:
                        print(user)
                        print(reps_form.errors)
                        print("Error en el formulario repeticiones")

                        
                return redirect('login')
        context = {'form': form}
        return render(request, 'register.html', context)

def logout_user(request):
    logout(request)
    return redirect('login')


################################ Actualizar perfil ################################
@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('retos', pk=user.id)

    return render(request, 'updateUser.html', {'form': form})


################################ Rutinas por defecto ################################
@login_required(login_url='login')
def rutinas_all(request):
    ejercicios = EjercicioRutinaPorDefecto.objects.all()
    rutinas = RutinaPorDefecto.objects.all()

    context = {'ejercicios': ejercicios, 'rutinas':rutinas}
    return render(request, 'rutinas_home.html', context)


################################ Rutinas personalizadas ################################
def crearRutinaPersonalizada(request, pk):
    user_id = pk
    context = {'user_id': user_id}

    if request.method == "POST":

        nombre_rutina = request.POST['nombre']
        series = request.POST['series']
        # user_id = int(request.POST['user_id'])

        form = Rutina_personalizada({'nombre':nombre_rutina, 'series':series, 'user':user_id})

        if form.is_valid():
            form.save()
            print("enviado rutina personalizada")
     
            repeticiones = request.POST.getlist('repeticiones')   # Te devuelve el array
            for ejercicio in request.POST.getlist('ejercicios'):

                reps = repeticiones[int(ejercicio)] # Debemos incluir la conversion a int
                rutina_id = Rutina.objects.get(nombre=nombre_rutina, user=user_id).id

                # Django detecta si es una string, por lo que es necesaria la conversion
                form_ej= Ejercicio_rutina_personalizada({'rutina':rutina_id, 'ejercicio':int(ejercicio), 'repeticiones':reps})  

                if form_ej.is_valid():
                    form_ej.save()
                    print("enviado ejercicio rutina")
                else:
                    print (form.errors)
                    print("Error en el formulario ejercicio rutina")
                    
            rutina = Rutina.objects.get(user=user_id, nombre=nombre_rutina)
            ejercicios = EjercicioRutina.objects.all()
            context = {'nombre_rutina':nombre_rutina, 'rutina':rutina, 'ejercicios':ejercicios}
            return render(request, 'correccion.html', context)

        else:
            print("Error en el formulario rutina personalizada")
            print (form.errors)
            context = {'error':"Ya existe una rutina con este nombre", 'nombre':nombre_rutina, 'user_id':user_id}
            return render(request, 'rutinas.html', context)

    return render(request, 'rutinas.html', context)


def borrarRutina(request):
    if request.method == "POST":
        rutina_id = request.POST['rutina_id']
        rutina = Rutina.objects.get(id=rutina_id)
        rutina.delete()
        print("rutina eliminada")

    return render(request, 'mis_rutinas.html')


################################ Correccion ################################
def correccion(request, nombre_rutina, pk):
    rutina = Rutina.objects.get(user=pk,nombre=nombre_rutina)
    ejercicios = EjercicioRutina.objects.all()

    context = {'nombre_rutina':nombre_rutina, 'rutina':rutina, 'ejercicios':ejercicios}
    return render(request, 'correccion.html', context)


def correccion_por_defecto(request, nombre_rutina):
    rutina = RutinaPorDefecto.objects.get(nombre=nombre_rutina)
    ejercicios = EjercicioRutinaPorDefecto.objects.all()

    context = {'nombre_rutina':nombre_rutina, 'rutina':rutina, 'ejercicios':ejercicios}
    return render(request, 'correccion.html', context)


################################ Pantallas del perfil de usuario [retos, logros, misRutinas] ################################
def userProfile_retos(request, pk):
    user_id = pk
    retos = Reto.objects.filter(user=user_id)
    descripcion_retos = DescripcionReto.objects.all()
    repeticiones = Repeticion.objects.filter(user=user_id)
    ejercicios_reto = EjercicioReto.objects.all()

    context = {'user_id': user_id, 'retos': retos, 'descripciones': descripcion_retos, 'repeticiones':repeticiones, 'ejercicios_reto':ejercicios_reto}
    return render(request, 'retos.html', context)


def userProfile_logros(request, pk):
    user_id = pk
    logros = Logro.objects.filter(user=user_id)
    descripciones = DescripcionLogro.objects.all()

    context = {'user_id':user_id, 'logros':logros, 'descripciones':descripciones}
    return render(request, 'logros.html', context)


def userProfile_rutinas(request, pk):
    user = User.objects.get(id=pk)
    
    rutinas = Rutina.objects.filter(user=user)  # Obtengo todas las rutinas
    ejercicios = EjercicioRutina.objects.all()
    
    context = {'user_id': pk, 'user': user, 'rutinas':rutinas, 'ejercicios':ejercicios}
    return render(request, 'mis_rutinas.html', context)  


################################ Paso de logros a retos y viceversa ################################
def actualizarLogro(request):   # Ponemos el logro en curso al crear el reto [logros.html]
    if request.method == "POST":

        user_id = request.POST['user_id']
        descripcion_logro = request.POST['descripcion_logro']
        logro = Logro.objects.get(descripcion_logro=descripcion_logro, user=user_id)
        logro.en_curso = request.POST['en_curso']
        logro.save()

    return render(request, 'logros.html')


def crearReto(request): # Creamos el reto asociado al usuario [logros.html]
    if request.method == "POST":    

        user_id = request.POST['user_id']
        logro = request.POST['logro']
        logro_id = Logro.objects.get(descripcion_logro=logro, user=user_id).id
        nivel = int(request.POST['nivel'])
        inicio = datetime.today()  

        descripcion_reto = DescripcionReto.objects.get(descripcion_logro=logro)
   
        if request.POST['mes'] != '0':
            fin = datetime.today() + relativedelta(months=int(request.POST['mes']))

        if request.POST['semanas'] != '0':
            fin = datetime.today() + relativedelta(weeks=int(request.POST['semanas']))

        if request.POST['dias'] != '0':
            fin = datetime.today()

        form = CrearReto({'logro':logro_id , 'descripcion_reto':descripcion_reto, 'nivel': nivel, 'inicio':inicio, 'fin':fin, 'conseguido':'' , 'user':user_id})

        if form.is_valid():
            form.save()

            ejercicio_reto = EjercicioReto.objects.get(descripcion_reto=descripcion_reto).ejercicio
            repeticion = Repeticion.objects.get(ejercicio=ejercicio_reto, user=user_id)
            repeticion.repeticiones = 0
            repeticion.save()

            print("repeticiones reinicializadas")
            return render(request, 'retos.html')    # No se ejecuta porque este formulario se envia con ajax

        else:
            print(form.errors)
            print("Error en el formulario reto")

    return render(request, 'logros.html')


def actualizarRetoLogroConseguido(request): # Eliminamos el reto y actualizamos el nivel del logro y los puntos del usuario [retos.html]
    if request.method == "POST":

        user_id = request.POST['user_id']
        id_descripcion_logro = request.POST['id_descripcion_logro']
        id_reto = request.POST['id_reto']
        ejercicio = request.POST['nombre_ejercicio']

        user = User.objects.get(id=user_id)
        user.points = user.points + 5
        user.save()
        
        reto = Reto.objects.get(id=id_reto, user=user_id)
        reto.delete()

        logro = Logro.objects.get(descripcion_logro=id_descripcion_logro, user=user_id)
        logro.en_curso = 0
        if logro.nivel != 3:        # Queremos que el usuario pueda repetir siempre el útimo nivel
            logro.nivel = logro.nivel + 1
        logro.save()

        repeticion = Repeticion.objects.get(ejercicio=ejercicio, user=user_id)
        repeticion.repeticiones = 0
        repeticion.save()

        print("Logro actualizado y reto borrado")

    return render(request, 'logros.html')


def actualizarRetoLogroCaducado(request):  # Eliminamos el reto y actualizamos logro en_curso=0, sin tocar el nivel ni los puntos [retos.html]
    if request.method == "POST":

        user_id = request.POST['user_id']
        id_descripcion_logro = request.POST['id_descripcion_logro']
        id_reto = request.POST['id_reto']
        ejercicio = request.POST['nombre_ejercicio']
        print("id del reto")
        print(id_reto)
        
        reto = Reto.objects.get(id=id_reto, user=user_id)
        reto.delete()

        logro = Logro.objects.get(descripcion_logro=id_descripcion_logro, user=user_id)
        logro.en_curso = 0
        logro.save()

        repeticion = Repeticion.objects.get(ejercicio=ejercicio, user=user_id)
        repeticion.repeticiones = 0
        repeticion.save()

        print("Logro y reto borrados")

    return render(request, 'retos.html')

    
def actualizarFechaRetoConseguido(request): # Ponemos la fecha de conseguido en el reto [retos.html]
    if request.method == "POST":

        reto_id = request.POST['id_reto']
        user_id = request.POST['user_id']
        reto = Reto.objects.get(id=reto_id, user=user_id)
        reto.conseguido = datetime.today()
        reto.save()

    return render(request, 'retos.html')

  
################################ Directos ################################
@login_required(login_url='login')
def directos_all(request):
    rooms = Room.objects.all()
    if request.method == "POST":
        nombre = request.POST['nombre']
        print ('El nombre de la sala es: ', nombre)
        nombre_display = request.POST['nombre_display']
        descripcion = request.POST['descripcion']

        form = CreateRoom({'nombre':nombre, 'nombre_display':nombre_display, 'descripcion':descripcion})

        if form.is_valid():
            form.save()
            return redirect('directos_room', nombre)
        
        else:
            print("Error, ese nombre ya existe")
            return render (request, 'directos_home.html', {'error': 'Nombre de sala ya existente', 'rooms': rooms})
    else:
        return render(request,'directos_home.html', {'rooms': rooms})
 

@login_required(login_url='login')
def directos_room(request, room):
    return render(request, 'directos_room.html', {'room': room})
      

################################ Calendarios ################################
class CalendarView(LoginRequiredMixin, ListView):
    login_url = '/login/'   
    model = Event
    template_name = 'calendar.html'
    success_url = reverse_lazy("calendar")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month, self.request.user.email)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context

      
def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

  
def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

  
def event(request, event_id=None):
    instance = Event()
    if event_id:
        instance = get_object_or_404(Event, pk=event_id)
    else:
        instance = Event()
    print("USER", request.user.email)
    form = EventForm(request.POST or None, instance=instance, initial={'useremail':request.user.email})
    if request.POST and form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('calendar'))
    return render(request, 'event.html', {'form': form})


from cProfile import label
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import ChoiceField, HiddenInput, ModelForm, DateInput
from django.utils.translation import activate
from django.utils.translation import gettext_lazy as _
from .models import User, Rutina, EjercicioRutina, Logro, Reto, Repeticion, Room, Event


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User 
        fields = ['username', 'email', 'password1', 'password2']

class Rutina_personalizada(forms.ModelForm):
    class Meta:
        model = Rutina 
        fields = ['nombre', 'series', 'user']

class Ejercicio_rutina_personalizada(forms.ModelForm):
    class Meta:
        model = EjercicioRutina 
        fields = ['rutina', 'ejercicio', 'repeticiones'] 

class UserForm(forms.ModelForm):
    class Meta:
        activate('es')
        model = User
        #translate form to spanish
        fields = ['username', 'email', 'avatar']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control-file', 'enctype': 'multipart/form-data'}),
        }

class InicializarLogro(forms.ModelForm):
    class Meta:
        model = Logro 
        fields = ['descripcion_logro', 'nivel', 'user', 'en_curso'] 

class CrearReto(forms.ModelForm):
    class Meta:
        model = Reto 
        fields = ['logro', 'descripcion_reto', 'nivel', 'inicio', 'fin', 'conseguido', 'user'] 

class ActualizarRepeticiones(forms.ModelForm):
    class Meta:
        model = Repeticion 
        fields = ['ejercicio', 'repeticiones', 'user'] 

class EventForm(ModelForm):
  class Meta:
    model = Event
    # datetime-local is a HTML5 input type, format to make date time show on fields
    widgets = {
      'start_time': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
      #'end_time': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
    }
    fields = '__all__'
  def __init__(self, *args, **kwargs):
    #self.user_request = kwargs.pop('user_request')
    super(EventForm, self).__init__(*args, **kwargs)
    # input_formats to parse HTML5 datetime-local input to datetime field

    self.fields['start_time'].input_formats = ('%Y-%m-%dT%H:%M',)
    #self.fields['end_time'].input_formats = ('%Y-%m-%dT%H:%M',)
    self.fields['useremail'].widget = HiddenInput()
    
class CreateRoom(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['nombre', 'nombre_display', 'descripcion']

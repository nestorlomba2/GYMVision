"""PWA URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django import views
from django.contrib import admin
from django.urls import path, include, re_path
from app import views
from django.conf import settings
from django.conf.urls.static import static 
urlpatterns = [

    path('', views.home_page, name='home'),
    path('rutinas/', views.rutinas_all, name='rutinas_home'),
    path('correccion/<str:nombre_rutina>/<str:pk>/', views.correccion, name='correccion'),
    path('correccion_por_defecto/<str:nombre_rutina>/', views.correccion_por_defecto, name='correccion_por_defecto'),
    path('crear_reto/', views.crearReto, name='crearReto'),
    path('actualizar_logro/', views.actualizarLogro, name='actualizarLogro'),
    path('actualizar_reto_y_logro_conseguidos/', views.actualizarRetoLogroConseguido, name='actualizarRetoLogroConseguido'),
    path('actualizar_reto_conseguido/', views.actualizarFechaRetoConseguido, name='actualizarRetoConseguido'),
    path('actualizar_reto_y_logro_caducados/', views.actualizarRetoLogroCaducado, name='actualizarRetoLogroCaducado'),
    path('borrar_rutina/', views.borrarRutina, name='borrarRutina'),


    path('directos/', views.directos_all, name='directos_home'),
    path('directos/<str:room>/',views.directos_room, name='directos_room'),

    
    path('perfil/<str:pk>/rutinas/', views.crearRutinaPersonalizada, name='rutinas'),
    path('perfil/<str:pk>/retos/', views.userProfile_retos, name='retos'),
    path('perfil/<str:pk>/logros/', views.userProfile_logros, name='logros'),
    path('perfil/<str:pk>/misRutinas/', views.userProfile_rutinas, name='mis_rutinas'),
    path('update-user/', views.updateUser, name='update_user'),


    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_user, name='logout'),


    path('admin/', admin.site.urls),
    path("", include('pwa.urls')),
    path(r'offline_layout',views.offline_layout,name='offline_layout'),  
    re_path(r'calendar/$', views.CalendarView.as_view(), name='calendar'),
    path('event/new/', views.event, name='event_new'),
    path('event/edit/?<event_id>/', views.event, name='event_edit'),

]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

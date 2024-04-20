from django.urls import path, re_path
from . import views
from django.contrib.auth import views as auth_views
# from .views import enviar_dinero


urlpatterns = [
    path('', views.index, name='index'),
    path('auth/login', views.inicio_sesion, name='login'),
    path('auth/create', views.registrar, name='registrar'),
    path('auth/recuperar', views.recuperar, name='recuperar'),
    path('auth/logout', views.cerrar_sesion, name='logout'),

    path('transacciones/enviar_dinero', views.enviar_dinero, name='enviar_dinero'),

    # Pagina cliente
    path('home', views.home, name='home'),
    path('home/transferencia', views.transferencia, name='transferencia'),
    path('home/transferencia/<codigo>', views.transferenciaCodigo, name='transferenciaCodigo'),
    path('home/historial', views.historial, name='historial'),



  path('import/cargar', views.cargar, name='cargar'),

   
]
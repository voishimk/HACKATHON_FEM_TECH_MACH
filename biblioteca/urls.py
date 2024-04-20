from django.urls import path
from . import views
# from .views import enviar_dinero


urlpatterns = [
  path('', views.index, name='index'),
  path('auth/login', views.inicio_sesion, name='login'),
  path('auth/create', views.registrar, name='registrar'),
  path('auth/recuperar', views.recuperar, name='recuperar'),
  path('auth/logout', views.cerrar_sesion, name='logout'),

  path('transacciones/enviar_dinero', views.enviar_dinero, name='enviar_dinero'),
  
  # pagina cliente
  path('home', views.home, name='home'),
]

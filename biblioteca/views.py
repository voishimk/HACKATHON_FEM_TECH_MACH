import random
import random
from django.shortcuts import render, get_object_or_404, redirect
from .models import Tarjeta, UserProfile, Transaccion
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail



## REQUESTS
import requests
from django.http import JsonResponse

# inicio de todo
def index(request):
    return render(request, 'index.html')

# AUTH
def inicio_sesion(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        clave = request.POST.get('pass')
        user = authenticate(request, username=usuario, password=clave)
        if user is not None:
            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                # If UserProfile doesn't exist, create one
                profile = UserProfile.objects.create(user=user, role='default')

            request.session['perfil'] = profile.role
            login(request, user)
            return redirect('home')
        else:
            context = {
                'error': 'Error intente nuevamente.'
            }
            return render(request, 'auth/index.html', context)

    return render(request, 'auth/index.html')
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        clave = request.POST.get('pass')
        user = authenticate(request, username=usuario, password=clave)
        if user is not None:
            profile = UserProfile.objects.get(user=user)
            request.session['perfil'] = profile.role

            login(request, user)
            return redirect('home')
        else:
            context = {
                'error' : 'Error intente nuevamente.'
            }
            return render(request, 'auth/index.html', context)

    return render(request, 'auth/index.html')

@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect('index')

def registrar(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('nombre')
        last_name = request.POST.get('apellido')
        email = request.POST.get('correo')
        password = request.POST.get('pass')

        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
        user.save()
        # Genera datos aleatorios para la tarjeta 
        numero_tarjeta =''.join(str(random.randint(0, 9)) for _ in range(16))
        balance = random.randint(0, 100000000)
        
        # Crea la tarjeta asociada al usuario
        Tarjeta.objects.create(cliente=user, numero=numero_tarjeta, balance=balance)
        

        messages.success(request, 'Creado correctamente')

        return redirect('login')

    return render(request, 'auth/create.html')



def cargar(request):
  # crea 10 usuarios con sus tarjetas
  for i in range(10):
      user = User.objects.create_user(username=f'user{i}', first_name=f'valentina {i}', last_name=f'guajardo {i}',email=f'valen{i}@mach.cl', password='123123')
      user.save()

      Tarjeta.objects.create(cliente=user, numero=f'123456789{i}', balance=1000000)

      print(f'Usuario {i} creado')

# SISTEMA
@login_required
def home(request):
    # perfil = request.session.get('perfil')

    context = {
        'perfil' : "perfil",
    }

    return render(request, 'home.html', context)


def transferencia(request):
  tarjetas_usuario = Tarjeta.objects.filter(cliente=request.user)
  primera_tarjeta = tarjetas_usuario.first()

  context = {
      'perfil' : "perfil",
      'tarjeta': primera_tarjeta
  }

  if request.method == 'POST':


      # la constraseña del usuario no se esta verificando

      username_destino = request.POST.get('username')
      monto = request.POST.get('monto')

      if request.user.username == username_destino:
          messages.error(request, 'No puedes transferir dinero a tu propia cuenta.')
          return redirect('transferencia')

      # Obtener el usuario actual y su tarjeta
      # buscar usuario por username
      try:
          receptor = User.objects.get(username=username_destino)
      except User.DoesNotExist:
          messages.error(request, 'El usuario receptor no existe.')
          return redirect('transferencia')
      tarjetas_usuario_receptor = Tarjeta.objects.filter(cliente=receptor)
      tarjeta_receptor = tarjetas_usuario_receptor.first()

      # Verificar si el usuario tiene saldo suficiente
      if primera_tarjeta.balance < int(monto):
          messages.error(request, 'No tienes suficiente saldo para realizar esta transferencia.')
          return redirect('transferencia')

      # Realizar la transferencia
      primera_tarjeta.balance -= int(monto)
      tarjeta_receptor.balance += int(monto)
      primera_tarjeta.save()
      tarjeta_receptor.save()

      Transaccion.objects.create(tarjeta_origen=primera_tarjeta, tarjeta_destino=tarjeta_receptor, monto=monto)

      messages.success(request, f'Se han transferido ${monto} a {receptor.username} correctamente.')
      return redirect('transferencia')

  return render(request, 'transferencia.html', context)



def transferenciaCodigo(request, codigo):
  tarjetas_usuario = Tarjeta.objects.filter(cliente=request.user)
  primera_tarjeta = tarjetas_usuario.first()

  # Obtener las transacciones que tengan el código ingresado
  transaccion = get_object_or_404(Transaccion, id=codigo)

  context = {
      'perfil' : "perfil",
      'tarjeta': primera_tarjeta,
      'transaccion': transaccion
  }

  return render(request, 'transferencia_codigo.html', context)

def historial(request):
  tarjetas_usuario = Tarjeta.objects.filter(cliente=request.user)
  primera_tarjeta = tarjetas_usuario.first()

  # Obtener transacciones donde el usuario está involucrado como origen o destino
  transacciones = Transaccion.objects.filter(tarjeta_origen__in=tarjetas_usuario) | Transaccion.objects.filter(tarjeta_destino__in=tarjetas_usuario)

  transacciones = transacciones.order_by('-fecha')  # Ordenar por fecha, las más recientes primero

  context = {
      'perfil' : "perfil",
      'tarjeta': primera_tarjeta,
      'transacciones': transacciones
  }

  return render(request, 'historial.html', context)

def enviar_dinero(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        receptor_id = request.POST.get('receptor_id')
        monto = int(request.POST.get('monto'))

        # Obtener el usuario actual y su tarjeta
        usuario = request.user
        tarjeta_usuario = Tarjeta.objects.get(cliente=usuario)

        # Verificar si el usuario tiene saldo suficiente
        if tarjeta_usuario.balance < monto:
            messages.error(request, 'No tienes suficiente saldo para realizar esta transferencia.')
            return redirect('enviar_dinero')

        # Verificar si el receptor existe
        try:
            receptor = UserProfile.objects.get(id=receptor_id).user
        except UserProfile.DoesNotExist:
            messages.error(request, 'El receptor no existe.')
            return redirect('enviar_dinero')

        # Realizar la transferencia
        tarjeta_receptor = Tarjeta.objects.get(cliente=receptor)
        tarjeta_usuario.balance -= monto
        tarjeta_receptor.balance += monto
        tarjeta_usuario.save()
        tarjeta_receptor.save()

        messages.success(request, f'Se han transferido ${monto} a {receptor.username} correctamente.')
        return redirect('enviar_dinero')

    return render(request, 'enviar_dinero.html')

def recuperar(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        nueva_contraseña = request.POST.get('nueva_contraseña')

        try:
            usuario = User.objects.get(email=correo)
            # Establecer la nueva contraseña utilizando make_password
            usuario.password = make_password(nueva_contraseña)
            usuario.save()
            messages.success(request, 'Contraseña actualizada correctamente.')
            return redirect('recuperar')
        except User.DoesNotExist:
            messages.error(request, 'No se encontró ningún usuario con ese correo electrónico.')

    return render(request, 'auth/recuperar.html')


# USUARIO

# def enviar_dinero(request):
#     if request.method == 'POST':
#         # Obtener los datos del formulario
#         receptor_id = request.POST.get('receptor_id')
#         monto = int(request.POST.get('monto'))

#         # Obtener el usuario actual y su tarjeta
#         usuario = request.user
#         tarjeta_usuario = Tarjeta.objects.get(cliente=usuario)

#         # Verificar si el usuario tiene saldo suficiente
#         if tarjeta_usuario.balance < monto:
#             messages.error(request, 'No tienes suficiente saldo para realizar esta transferencia.')
#             return redirect('enviar_dinero')

#         # Verificar si el receptor existe
#         try:
#             receptor = UserProfile.objects.get(id=receptor_id).user
#         except UserProfile.DoesNotExist:
#             messages.error(request, 'El receptor no existe.')
#             return redirect('enviar_dinero')

#         # Realizar la transferencia
#         tarjeta_receptor = Tarjeta.objects.get(cliente=receptor)
#         tarjeta_usuario.balance -= monto
#         tarjeta_receptor.balance += monto
#         tarjeta_usuario.save()
#         tarjeta_receptor.save()

#         messages.success(request, f'Se han transferido ${monto} a {receptor.username} correctamente.')
#         return redirect('enviar_dinero')

#     return render(request, 'enviar_dinero.html')


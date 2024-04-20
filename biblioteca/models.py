from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages

class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=settings.ROLES)

    def __str__(self):
        return self.user.username + ' - ' + self.role

class Tarjeta(models.Model):
    numero = models.CharField(max_length=20)
    balance = models.IntegerField()
    cliente = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return f'Tarjeta: {self.numero}'

class Transaccion(models.Model):
    tarjeta_origen = models.ForeignKey(Tarjeta, related_name='transacciones_origen', on_delete=models.CASCADE)
    tarjeta_destino = models.ForeignKey(Tarjeta, related_name='transacciones_destino', on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Transferencia de {self.monto} desde {self.tarjeta_origen} hacia {self.tarjeta_destino}'
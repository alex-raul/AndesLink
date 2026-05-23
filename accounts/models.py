from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        PRODUCTOR = 'PRODUCTOR', 'Productor'
        COMPRADOR = 'COMPRADOR', 'Comprador'
        AGENTE = 'AGENTE_ANDINO', 'Agente Andino'

    class EstadoVerificacion(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        VERIFICADO = 'VERIFICADO', 'Verificado'
        SUSPENDIDO = 'SUSPENDIDO', 'Suspendido'

    dni = models.CharField(max_length=12, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.COMPRADOR
    )
    estado_verificacion = models.CharField(
        max_length=20,
        choices=EstadoVerificacion.choices,
        default=EstadoVerificacion.PENDIENTE
    )
    departamento = models.CharField(max_length=80, blank=True)
    provincia = models.CharField(max_length=80, blank=True)
    foto = models.ImageField(upload_to='usuarios/', blank=True, null=True)

    def es_productor(self):
        return self.rol == self.Rol.PRODUCTOR

    def es_comprador(self):
        return self.rol == self.Rol.COMPRADOR

    def es_agente(self):
        return self.rol == self.Rol.AGENTE

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"
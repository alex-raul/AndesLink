from django.db import models
from django.conf import settings
from marketplace.models import Producto


class SolicitudContacto(models.Model):
    """El comprador envía una solicitud al productor sobre un producto."""

    class Estado(models.TextChoices):
        PENDIENTE  = 'PENDIENTE',  'Pendiente'
        VISTA      = 'VISTA',      'Vista por el productor'
        ACEPTADA   = 'ACEPTADA',   'Aceptada'
        RECHAZADA  = 'RECHAZADA',  'Rechazada'

    comprador   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitudes_enviadas',
        limit_choices_to={'rol': 'COMPRADOR'}
    )
    producto    = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='solicitudes'
    )
    cantidad_requerida = models.DecimalField(max_digits=10, decimal_places=2)
    mensaje     = models.TextField(blank=True)
    estado      = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )
    creado_en   = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        return f"Solicitud de {self.comprador} → {self.producto.nombre}"

    def monto_estimado(self):
        return self.cantidad_requerida * self.producto.precio_unitario
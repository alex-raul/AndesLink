import hashlib
import uuid
from django.db import models
from django.conf import settings
from marketplace.models import Producto


class Orden(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE_PAGO  = 'PENDIENTE_PAGO',  'Pendiente de pago'
        PAGADO          = 'PAGADO',           'Pagado'
        ACEPTADO        = 'ACEPTADO',         'Aceptado'
        RECHAZADO       = 'RECHAZADO',        'Rechazado'
        EN_CAMINO       = 'EN_CAMINO',        'En camino'
        ENTREGADO       = 'ENTREGADO',        'Entregado'
        CONFIRMADO      = 'CONFIRMADO',       'Confirmado por comprador'
        DISPUTADO       = 'DISPUTADO',        'En disputa'
        FINALIZADO      = 'FINALIZADO',       'Finalizado'

    comprador        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ordenes'
    )
    estado           = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE_PAGO
    )
    codigo           = models.CharField(max_length=12, unique=True, editable=False)
    direccion_entrega = models.TextField()
    notas            = models.TextField(blank=True)
    total            = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    creado_en        = models.DateTimeField(auto_now_add=True)
    actualizado_en   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado_en']
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

    def calcular_total(self):
        self.total = sum(
            item.subtotal() for item in self.items.all()
        )
        self.save(update_fields=['total'])

    def __str__(self):
        return f"Orden #{self.codigo} — {self.comprador.get_full_name()}"


class ItemOrden(models.Model):
    orden           = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='items')
    producto        = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='items_orden')
    cantidad        = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # congelado al comprar

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


class PagoSimulado(models.Model):

    class Metodo(models.TextChoices):
        TARJETA      = 'TARJETA',      'Tarjeta de crédito/débito'
        YAPE         = 'YAPE',         'Yape'
        PLIN         = 'PLIN',         'Plin'
        TRANSFERENCIA = 'TRANSFERENCIA', 'Transferencia bancaria'

    class Estado(models.TextChoices):
        RETENIDO  = 'RETENIDO',  'Retenido (escrow)'
        LIBERADO  = 'LIBERADO',  'Liberado al productor'
        DEVUELTO  = 'DEVUELTO',  'Devuelto al comprador'

    orden              = models.OneToOneField(Orden, on_delete=models.CASCADE, related_name='pago')
    monto              = models.DecimalField(max_digits=12, decimal_places=2)
    metodo             = models.CharField(max_length=20, choices=Metodo.choices)
    estado             = models.CharField(max_length=15, choices=Estado.choices, default=Estado.RETENIDO)
    codigo_confirmacion = models.CharField(max_length=64, unique=True, editable=False)
    fecha_pago         = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.codigo_confirmacion:
            raw = f"{self.orden_id}-{uuid.uuid4()}"
            self.codigo_confirmacion = hashlib.sha256(raw.encode()).hexdigest()[:16].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pago {self.codigo_confirmacion} — {self.get_estado_display()}"


class ConfirmacionEntrega(models.Model):
    orden                   = models.OneToOneField(Orden, on_delete=models.CASCADE, related_name='confirmacion')
    confirmado_por_agente   = models.BooleanField(default=False)
    confirmado_por_comprador = models.BooleanField(default=False)
    foto_evidencia          = models.ImageField(upload_to='entregas/', blank=True, null=True)
    notas_entrega           = models.TextField(blank=True)
    fecha_confirmacion      = models.DateTimeField(null=True, blank=True)

    def ambos_confirmaron(self):
        return self.confirmado_por_agente and self.confirmado_por_comprador

    def __str__(self):
        return f"Entrega orden #{self.orden.codigo}"

class Calificacion(models.Model):
    orden        = models.ForeignKey(
        'Orden',
        on_delete=models.CASCADE,
        related_name='calificaciones'
    )
    evaluador    = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='calificaciones_dadas'
    )
    evaluado     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='calificaciones_recibidas'
    )
    estrellas    = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)]
    )
    comentario   = models.TextField(blank=True)
    creado_en    = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Una calificación por evaluador por orden
        unique_together = [('orden', 'evaluador')]
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.evaluador} → {self.evaluado}: {self.estrellas}★ (Orden #{self.orden.codigo})"
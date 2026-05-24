# agente/models.py
import hashlib
import uuid
from django.db import models
from django.conf import settings
from marketplace.models import Producto

'''class ProductorAsignado(models.Model):
    """Relación entre un agente y los productores que gestiona."""
    agente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='productores_asignados',
        limit_choices_to={'rol': 'AGENTE_ANDINO'}
    )
    productor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='agente_responsable',
        limit_choices_to={'rol': 'PRODUCTOR'}
    )
    notas = models.TextField(blank=True)
    asignado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['agente', 'productor']
        verbose_name = 'Productor asignado'
        verbose_name_plural = 'Productores asignados'

    def __str__(self):
        return f"Agente {self.agente.get_full_name()} → {self.productor.get_full_name()}"'''

class SolicitudRelacion(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE  = 'PENDIENTE',  'Pendiente'
        ACEPTADA   = 'ACEPTADA',   'Aceptada'
        RECHAZADA  = 'RECHAZADA',  'Rechazada'

    iniciador  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitudes_enviadas'
    )
    receptor   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitudes_recibidas'
    )
    estado     = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )
    mensaje    = models.TextField(blank=True)
    creado_en  = models.DateTimeField(auto_now_add=True)

    class Meta:
        # No puede haber dos solicitudes activas entre el mismo par
        unique_together = [('iniciador', 'receptor')]
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.iniciador} → {self.receptor} [{self.estado}]"


class ProductorAsignado(models.Model):
    agente     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='productores_asignados'
    )
    productor  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='agentes_asignados'
    )
    solicitud  = models.OneToOneField(
        SolicitudRelacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='relacion_activa'
    )
    asignado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('agente', 'productor')]

    def __str__(self):
        return f"Agente {self.agente} — Productor {self.productor}"
    

class ActaVerificacion(models.Model):
    producto        = models.OneToOneField(
        Producto,
        on_delete=models.CASCADE,
        related_name='acta'
    )
    agente          = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='actas'
    )
    foto_evidencia  = models.ImageField(upload_to='actas/')
    latitud         = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud        = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    notas           = models.TextField(blank=True)
    hash_validacion = models.CharField(max_length=64, unique=True, editable=False)
    creado_en       = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.hash_validacion:
            self.hash_validacion = hashlib.sha256(
                str(uuid.uuid4()).encode()
            ).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Acta {self.hash_validacion[:8]} — {self.producto.nombre}"

    def save(self, *args, **kwargs):
        if not self.hash_validacion:
            import hashlib, uuid
            self.hash_validacion = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
        super().save(*args, **kwargs)


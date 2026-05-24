# agente/models.py

from django.db import models
from django.conf import settings
from marketplace.models import Producto

class ProductorAsignado(models.Model):
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
        return f"Agente {self.agente.get_full_name()} → {self.productor.get_full_name()}"
    
class ActaVerificacion(models.Model):
    """El agente genera un acta cuando verifica un producto en campo."""
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, related_name='acta')
    agente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    foto_evidencia = models.ImageField(upload_to='actas/')
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    notas = models.TextField(blank=True)
    hash_validacion = models.CharField(max_length=64, unique=True)  # SHA256 auto
    creado_en = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.hash_validacion:
            import hashlib, uuid
            self.hash_validacion = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
        super().save(*args, **kwargs)
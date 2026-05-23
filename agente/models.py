from django.db import models
from django.conf import settings


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
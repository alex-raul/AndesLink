from django.db import models
from django.conf import settings


class Notificacion(models.Model):
    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )
    titulo      = models.CharField(max_length=120)
    mensaje     = models.TextField()
    url_accion  = models.CharField(max_length=200, blank=True)
    leida       = models.BooleanField(default=False)
    creado_en   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        return f"[{'✓' if self.leida else '•'}] {self.titulo} → {self.destinatario.username}"
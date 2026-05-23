from django.contrib import admin
from .models import SolicitudContacto


@admin.register(SolicitudContacto)
class SolicitudContactoAdmin(admin.ModelAdmin):
    list_display = ['comprador', 'producto', 'cantidad_requerida', 'estado', 'creado_en']
    list_filter = ['estado']
    list_editable = ['estado']
from django.contrib import admin
from .models import ProductorAsignado


@admin.register(ProductorAsignado)
class ProductorAsignadoAdmin(admin.ModelAdmin):
    list_display = ['agente', 'productor', 'asignado_en']
    list_filter = ['agente']
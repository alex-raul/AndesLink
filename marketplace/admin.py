from django.contrib import admin
from .models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'icono']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'productor', 'categoria', 'precio_unitario', 'cantidad', 'estado']
    list_filter = ['estado', 'categoria', 'departamento']
    search_fields = ['nombre', 'productor__first_name', 'productor__last_name']
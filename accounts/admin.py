# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'rol', 'estado_verificacion', 'departamento']
    list_filter = ['rol', 'estado_verificacion']
    fieldsets = UserAdmin.fieldsets + (
        ('AndesLink', {'fields': ('dni', 'telefono', 'rol', 'estado_verificacion', 'departamento', 'provincia', 'foto')}),
    )
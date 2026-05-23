from django import forms
from .models import SolicitudContacto


class SolicitudContactoForm(forms.ModelForm):
    class Meta:
        model = SolicitudContacto
        fields = ['cantidad_requerida', 'mensaje']
        widgets = {
            'mensaje': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe tu pedido: cantidad, frecuencia, condiciones de entrega...'
            }),
            'cantidad_requerida': forms.NumberInput(attrs={
                'placeholder': 'Ej: 500'
            }),
        }
        labels = {
            'cantidad_requerida': 'Cantidad que necesitas',
            'mensaje': 'Mensaje al productor',
        }
from django import forms
from .models import SolicitudContacto


class SolicitudContactoForm(forms.ModelForm):
    class Meta:
        model  = SolicitudContacto
        fields = ['cantidad_requerida', 'mensaje']
        labels = {
            'cantidad_requerida': 'Cantidad que necesitas',
            'mensaje': 'Mensaje para el productor (opcional)',
        }
        widgets = {
            'mensaje': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Cuéntale al productor tus necesidades, tipo de entrega, etc.'}),
        }
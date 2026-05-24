from django import forms
from marketplace.models import Producto


'''class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre', 'categoria', 'descripcion',
            'cantidad', 'unidad', 'precio_unitario',
            'fecha_cosecha', 'departamento', 'provincia',
            'imagen', 'estado',
        ]
        widgets = {
            'fecha_cosecha': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }'''

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre', 'categoria', 'descripcion',
            'cantidad', 'unidad', 'precio_unitario',
            'fecha_cosecha', 'departamento', 'provincia',
            'imagen', 'estado',
            'latitud', 'longitud',       # coordenadas del mapa
        ]
        widgets = {
            'fecha_cosecha': forms.DateInput(attrs={'type': 'date'}),
            'descripcion':   forms.Textarea(attrs={'rows': 3}),
            'latitud':       forms.HiddenInput(),
            'longitud':      forms.HiddenInput(),
        }
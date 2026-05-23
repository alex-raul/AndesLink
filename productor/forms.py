from django import forms
from marketplace.models import Producto


class ProductoForm(forms.ModelForm):
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
        }
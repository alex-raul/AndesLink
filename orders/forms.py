from django import forms
from .models import PagoSimulado


class CheckoutForm(forms.Form):
    direccion_entrega = forms.CharField(
        label='Dirección de entrega',
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Jr. Los Andes 123, Puno'}),
    )
    notas = forms.CharField(
        label='Notas adicionales',
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Instrucciones especiales para la entrega...'}),
    )
    metodo_pago = forms.ChoiceField(
        label='Método de pago',
        choices=PagoSimulado.Metodo.choices,
    )


class ConfirmarEntregaForm(forms.Form):
    confirmado = forms.BooleanField(
        label='Confirmo que recibí mi pedido correctamente',
        required=True,
    )


class DisputaForm(forms.Form):
    MOTIVOS = [
        ('DIFERENTE', 'El producto recibido es diferente al pedido'),
        ('CANTIDAD',  'La cantidad recibida es incorrecta'),
        ('CALIDAD',   'La calidad no corresponde a lo anunciado'),
        ('NO_LLEGO',  'El pedido no llegó'),
        ('OTRO',      'Otro motivo'),
    ]
    motivo      = forms.ChoiceField(label='Motivo de la disputa', choices=MOTIVOS)
    descripcion = forms.CharField(
        label='Descripción detallada',
        widget=forms.Textarea(attrs={'rows': 4}),
    )

class CalificacionForm(forms.Form):
    estrellas = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        label='Calificación',
        widget=forms.HiddenInput()   # lo manejamos con JS de estrellas
    )
    comentario = forms.CharField(
        label='Comentario (opcional)',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Cuéntanos cómo fue la experiencia...'
        })
    )
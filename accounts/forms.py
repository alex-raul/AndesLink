from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(label='Nombres', max_length=80)
    last_name = forms.CharField(label='Apellidos', max_length=80)
    email = forms.EmailField(label='Correo electrónico')
    dni = forms.CharField(label='DNI', max_length=12)
    telefono = forms.CharField(label='Teléfono', max_length=20)
    departamento = forms.CharField(label='Departamento', max_length=80)
    rol = forms.ChoiceField(
        label='Tipo de cuenta',
        choices=[
            (Usuario.Rol.PRODUCTOR, '🌾 Soy productor / agricultor'),
            (Usuario.Rol.COMPRADOR, '🏢 Soy comprador / empresa'),
            (Usuario.Rol.AGENTE,    '🧭 Soy agente andino'),
        ]
    )

    class Meta:
        model = Usuario
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'dni', 'telefono', 'departamento', 'rol',
            'password1', 'password2',
        ]


class EditarPerfilForm(forms.ModelForm):
    first_name = forms.CharField(label='Nombres', max_length=80)
    last_name  = forms.CharField(label='Apellidos', max_length=80)
    email      = forms.EmailField(label='Correo electrónico')

    class Meta:
        model  = Usuario
        fields = [
            'first_name', 'last_name', 'email',
            'dni', 'telefono', 'departamento', 'provincia', 'foto',
        ]
        labels = {
            'dni':         'DNI',
            'telefono':    'Teléfono',
            'departamento':'Departamento',
            'provincia':   'Provincia',
            'foto':        'Foto de perfil',
        }
        widgets = {
            'foto': forms.FileInput(),
        }
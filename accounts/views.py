from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RegistroForm, EditarPerfilForm
from .models import Usuario


class RegistroView(CreateView):
    model = Usuario
    form_class = RegistroForm
    template_name = 'accounts/registro.html'
    success_url = reverse_lazy('marketplace:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Si se registra como productor, auto-verificar
        if self.object.rol == 'PRODUCTOR':
            self.object.estado_verificacion = 'VERIFICADO'
            self.object.save(update_fields=['estado_verificacion'])
        login(self.request, self.object)
        return response


class LoginAndesView(LoginView):
    template_name = 'accounts/login.html'


def logout_view(request):
    logout(request)
    return redirect('marketplace:home')


@login_required
def perfil(request):
    return render(request, 'accounts/perfil.html', {'usuario': request.user})


@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('accounts:perfil')
    else:
        form = EditarPerfilForm(instance=request.user)
    return render(request, 'accounts/editar_perfil.html', {'form': form})


def perfil_productor_publico(request, pk):
    """Página pública del productor visible para todos."""
    productor = get_object_or_404(Usuario, pk=pk, rol=Usuario.Rol.PRODUCTOR)
    from marketplace.models import Producto
    productos = Producto.objects.filter(
        productor=productor, estado='DISPONIBLE'
    ).select_related('categoria')
    return render(request, 'accounts/perfil_productor.html', {
        'productor': productor,
        'productos': productos,
    })
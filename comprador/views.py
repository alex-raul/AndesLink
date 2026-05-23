from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from marketplace.models import Producto
from .models import SolicitudContacto
from .forms import SolicitudContactoForm


def solo_comprador(view_func):
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.es_comprador():
            messages.error(request, 'Solo los compradores pueden acceder a esta sección.')
            return redirect('marketplace:home')
        return view_func(request, *args, **kwargs)
    return _wrapped


@solo_comprador
def dashboard(request):
    solicitudes = SolicitudContacto.objects.filter(
        comprador=request.user
    ).select_related('producto', 'producto__productor')
    return render(request, 'comprador/dashboard.html', {'solicitudes': solicitudes})


@login_required
def enviar_solicitud(request, pk):
    producto = get_object_or_404(Producto, pk=pk, estado='DISPONIBLE')

    # Solo compradores pueden contactar
    if request.user.es_productor():
        messages.error(request, 'Los productores no pueden enviar solicitudes.')
        return redirect('marketplace:detalle', pk=pk)

    # Evitar duplicados
    ya_enviada = SolicitudContacto.objects.filter(
        comprador=request.user, producto=producto
    ).exists()
    if ya_enviada:
        messages.warning(request, 'Ya enviaste una solicitud para este producto.')
        return redirect('comprador:dashboard')

    if request.method == 'POST':
        form = SolicitudContactoForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.comprador = request.user
            solicitud.producto = producto
            solicitud.save()
            messages.success(request, f'Solicitud enviada al productor de "{producto.nombre}".')
            return redirect('comprador:dashboard')
    else:
        form = SolicitudContactoForm()

    return render(request, 'comprador/enviar_solicitud.html', {
        'form': form,
        'producto': producto,
    })
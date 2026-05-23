from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from marketplace.models import Producto
from comprador.models import SolicitudContacto
from accounts.models import Usuario
from .models import ProductorAsignado


def solo_agente(view_func):
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.es_agente():
            messages.error(request, 'Solo los agentes andinos pueden acceder a esta sección.')
            return redirect('marketplace:home')
        return view_func(request, *args, **kwargs)
    return _wrapped


@solo_agente
def dashboard(request):
    # Productores que gestiona este agente
    asignaciones = ProductorAsignado.objects.filter(
        agente=request.user
    ).select_related('productor')

    productores_ids = asignaciones.values_list('productor_id', flat=True)

    # Productos de esos productores
    productos = Producto.objects.filter(
        productor_id__in=productores_ids
    ).select_related('productor', 'categoria')

    # Solicitudes pendientes sobre esos productos
    solicitudes_pendientes = SolicitudContacto.objects.filter(
        producto__in=productos,
        estado='PENDIENTE'
    ).select_related('comprador', 'producto')

    stats = {
        'productores': asignaciones.count(),
        'productos_activos': productos.filter(estado='DISPONIBLE').count(),
        'solicitudes_pendientes': solicitudes_pendientes.count(),
    }

    return render(request, 'agente/dashboard.html', {
        'asignaciones': asignaciones,
        'productos': productos[:10],
        'solicitudes_pendientes': solicitudes_pendientes,
        'stats': stats,
    })


@solo_agente
def lista_productores(request):
    """Todos los productores del sistema (para el agente pueda asignarlos)."""
    productores = Usuario.objects.filter(rol='PRODUCTOR').order_by('first_name')
    mis_ids = ProductorAsignado.objects.filter(
        agente=request.user
    ).values_list('productor_id', flat=True)

    return render(request, 'agente/lista_productores.html', {
        'productores': productores,
        'mis_ids': list(mis_ids),
    })


@solo_agente
def asignar_productor(request, productor_id):
    productor = get_object_or_404(Usuario, pk=productor_id, rol='PRODUCTOR')
    _, creado = ProductorAsignado.objects.get_or_create(
        agente=request.user,
        productor=productor
    )
    if creado:
        messages.success(request, f'{productor.get_full_name()} añadido a tu cartera.')
    else:
        messages.info(request, 'Ya tienes asignado a este productor.')
    return redirect('agente:lista_productores')


@solo_agente
def solicitudes_zona(request):
    """Solicitudes de todos los productos de productores del agente."""
    productores_ids = ProductorAsignado.objects.filter(
        agente=request.user
    ).values_list('productor_id', flat=True)

    solicitudes = SolicitudContacto.objects.filter(
        producto__productor_id__in=productores_ids
    ).select_related('comprador', 'producto', 'producto__productor').order_by('-creado_en')

    return render(request, 'agente/solicitudes.html', {'solicitudes': solicitudes})
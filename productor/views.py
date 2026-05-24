from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from agente.models import SolicitudRelacion, ProductorAsignado
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from marketplace.models import Producto
from .forms import ProductoForm
from accounts.models import Usuario

def solo_productor(view_func):
    """Decorador: solo usuarios con rol PRODUCTOR pueden acceder."""
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.es_productor():
            messages.error(request, 'Solo los productores pueden acceder a esta sección.')
            return redirect('marketplace:home')
        return view_func(request, *args, **kwargs)
    return _wrapped


@solo_productor
def dashboard(request):
    productos = Producto.objects.filter(productor=request.user)
    stats = {
        'total': productos.count(),
        'disponibles': productos.filter(estado='DISPONIBLE').count(),
        'vendidos': productos.filter(estado='VENDIDO').count(),
    }
    return render(request, 'productor/dashboard.html', {
        'productos': productos,
        'stats': stats,
    })


@solo_productor
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.productor = request.user
            producto.save()
            messages.success(request, f'Producto "{producto.nombre}" publicado exitosamente.')
            return redirect('productor:dashboard')
    else:
        form = ProductoForm()
    return render(request, 'productor/form_producto.html', {'form': form, 'accion': 'Agregar'})


@solo_productor
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk, productor=request.user)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado.')
            return redirect('productor:dashboard')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productor/form_producto.html', {'form': form, 'accion': 'Editar', 'producto': producto})


@solo_productor
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk, productor=request.user)
    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'"{nombre}" eliminado.')
        return redirect('productor:dashboard')
    return render(request, 'productor/confirmar_eliminar.html', {'producto': producto})

@solo_productor
def mis_solicitudes(request):
    """El productor ve las solicitudes que recibió y su agente actual."""
    solicitudes_recibidas = SolicitudRelacion.objects.filter(
        receptor=request.user,
        estado=SolicitudRelacion.Estado.PENDIENTE
    ).select_related('iniciador')

    solicitudes_enviadas = SolicitudRelacion.objects.filter(
        iniciador=request.user,
        estado=SolicitudRelacion.Estado.PENDIENTE
    ).select_related('receptor')

    mi_agente = ProductorAsignado.objects.filter(
        productor=request.user
    ).select_related('agente').first()

    return render(request, 'productor/mis_solicitudes.html', {
        'solicitudes_recibidas': solicitudes_recibidas,
        'solicitudes_enviadas':  solicitudes_enviadas,
        'mi_agente':             mi_agente,
    })
@solo_productor
def buscar_agentes(request):
    q = request.GET.get('q', '').strip()
    agentes = []

    ya_asignado = ProductorAsignado.objects.filter(
        productor=request.user
    ).values_list('agente_id', flat=True)

    solicitudes_activas = SolicitudRelacion.objects.filter(
        Q(iniciador=request.user) | Q(receptor=request.user),
        estado=SolicitudRelacion.Estado.PENDIENTE
    ).values_list('iniciador_id', 'receptor_id')

    ids_con_relacion = set(ya_asignado)
    for ini, rec in solicitudes_activas:
        ids_con_relacion.add(ini)
        ids_con_relacion.add(rec)
    ids_con_relacion.discard(request.user.pk)

    if q:
        agentes = Usuario.objects.filter(
            rol=Usuario.Rol.AGENTE
        ).filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(departamento__icontains=q)
        ).exclude(pk__in=ids_con_relacion)

    return render(request, 'productor/buscar_agentes.html', {
        'agentes': agentes,
        'q': q,
    })


@solo_productor
def enviar_solicitud_a_agente(request, agente_id):
    agente = get_object_or_404(Usuario, pk=agente_id, rol=Usuario.Rol.AGENTE)

    existe = SolicitudRelacion.objects.filter(
        Q(iniciador=request.user, receptor=agente) |
        Q(iniciador=agente, receptor=request.user)
    ).exists()
    ya_asignado = ProductorAsignado.objects.filter(
        agente=agente, productor=request.user
    ).exists()

    if existe or ya_asignado:
        messages.warning(request, 'Ya existe una solicitud o relación con este agente.')
        return redirect('productor:buscar_agentes')

    if request.method == 'POST':
        mensaje = request.POST.get('mensaje', '')
        SolicitudRelacion.objects.create(
            iniciador=request.user,
            receptor=agente,
            mensaje=mensaje,
        )
        from notificaciones.utils import notificar
        notificar(
            agente,
            'Nueva solicitud de productor',
            f'{request.user.get_full_name()} quiere que seas su agente andino.',
            '/agente/'
        )
        messages.success(request, f'Solicitud enviada a {agente.get_full_name()}.')
        return redirect('productor:solicitudes')

    return render(request, 'productor/enviar_solicitud_agente.html', {'agente': agente})
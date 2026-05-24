from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from marketplace.models import Producto
from comprador.models import SolicitudContacto
from accounts.models import Usuario
from .models import ProductorAsignado
from orders.models import Orden
from .models import SolicitudRelacion, ProductorAsignado, ActaVerificacion

def solo_agente(view_func):
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.es_agente():
            messages.error(request, 'Solo los agentes pueden acceder a esta sección.')
            return redirect('marketplace:home')
        return view_func(request, *args, **kwargs)
    return _wrapped


@solo_agente
def dashboard(request):
    productores_asignados = ProductorAsignado.objects.filter(
        agente=request.user
    ).select_related('productor')

    solicitudes_recibidas = SolicitudRelacion.objects.filter(
        receptor=request.user,
        estado=SolicitudRelacion.Estado.PENDIENTE
    ).select_related('iniciador')

    solicitudes_enviadas = SolicitudRelacion.objects.filter(
        iniciador=request.user,
        estado=SolicitudRelacion.Estado.PENDIENTE
    ).select_related('receptor')

    # Pedidos de todos los productores asignados
    productores_ids = productores_asignados.values_list('productor_id', flat=True)
    pedidos = Orden.objects.filter(
        items__producto__productor_id__in=productores_ids
    ).distinct().order_by('-creado_en')[:20]

    return render(request, 'agente/dashboard.html', {
        'productores_asignados':  productores_asignados,
        'solicitudes_recibidas':  solicitudes_recibidas,
        'solicitudes_enviadas':   solicitudes_enviadas,
        'pedidos':                pedidos,
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

# ── BUSCAR PRODUCTORES ────────────────────────────────────────────────────────

@solo_agente
def buscar_productores(request):
    q = request.GET.get('q', '').strip()
    productores = []

    # IDs con los que ya tiene relación activa o solicitud pendiente
    ya_asignados = ProductorAsignado.objects.filter(
        agente=request.user
    ).values_list('productor_id', flat=True)

    solicitudes_activas = SolicitudRelacion.objects.filter(
        Q(iniciador=request.user) | Q(receptor=request.user),
        estado=SolicitudRelacion.Estado.PENDIENTE
    ).values_list('iniciador_id', 'receptor_id')

    ids_con_relacion = set(ya_asignados)
    for ini, rec in solicitudes_activas:
        ids_con_relacion.add(ini)
        ids_con_relacion.add(rec)
    ids_con_relacion.discard(request.user.pk)

    if q:
        productores = Usuario.objects.filter(
            rol=Usuario.Rol.PRODUCTOR      
        ).filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(departamento__icontains=q)
        ).exclude(pk__in=ids_con_relacion)

    return render(request, 'agente/buscar_productores.html', {
        'productores': productores,
        'q': q,
    })


# ── SOLICITUDES ───────────────────────────────────────────────────────────────

@solo_agente
def enviar_solicitud(request, productor_id):
    productor = get_object_or_404(Usuario, pk=productor_id, rol=Usuario.Rol.PRODUCTOR)

    # Verificar que no exista ya una relación o solicitud
    existe = SolicitudRelacion.objects.filter(
        Q(iniciador=request.user, receptor=productor) |
        Q(iniciador=productor, receptor=request.user)
    ).exists()
    ya_asignado = ProductorAsignado.objects.filter(
        agente=request.user, productor=productor
    ).exists()

    if existe or ya_asignado:
        messages.warning(request, 'Ya existe una solicitud o relación con este productor.')
        return redirect('agente:buscar')

    if request.method == 'POST':
        mensaje = request.POST.get('mensaje', '')
        SolicitudRelacion.objects.create(
            iniciador=request.user,
            receptor=productor,
            mensaje=mensaje,
        )
        from notificaciones.utils import notificar
        notificar(
            productor,
            f'Nueva solicitud de agente',
            f'{request.user.get_full_name()} quiere ser tu agente andino.',
            f'/agente/solicitudes/'
        )
        messages.success(request, f'Solicitud enviada a {productor.get_full_name()}.')
        return redirect('agente:dashboard')

    return render(request, 'agente/enviar_solicitud.html', {'productor': productor})


@login_required
def aceptar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(
        SolicitudRelacion,
        pk=solicitud_id,
        receptor=request.user,
        estado=SolicitudRelacion.Estado.PENDIENTE
    )
    if request.method == 'POST':
        solicitud.estado = SolicitudRelacion.Estado.ACEPTADA
        solicitud.save()

        # Determinar quién es agente y quién es productor
        if solicitud.iniciador.es_agente():
            agente    = solicitud.iniciador
            productor = solicitud.receptor
        else:
            agente    = solicitud.receptor
            productor = solicitud.iniciador

        ProductorAsignado.objects.get_or_create(
            agente=agente,
            productor=productor,
            defaults={'solicitud': solicitud}
        )
        from notificaciones.utils import notificar
        notificar(
            solicitud.iniciador,
            'Solicitud aceptada',
            f'{request.user.get_full_name()} aceptó tu solicitud de relación.',
        )
        messages.success(request, 'Relación establecida correctamente.')
    return redirect('agente:dashboard') if request.user.es_agente() else redirect('productor:dashboard')


@login_required
def rechazar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(
        SolicitudRelacion,
        pk=solicitud_id,
        receptor=request.user,
        estado=SolicitudRelacion.Estado.PENDIENTE
    )
    if request.method == 'POST':
        solicitud.estado = SolicitudRelacion.Estado.RECHAZADA
        solicitud.save()
        messages.info(request, 'Solicitud rechazada.')
    return redirect('agente:dashboard') if request.user.es_agente() else redirect('productor:dashboard')


@login_required
def eliminar_relacion(request, relacion_id):
    relacion = get_object_or_404(
        ProductorAsignado,
        pk=relacion_id
    )
    # Solo el agente o el productor de esa relación pueden eliminarla
    if request.user not in (relacion.agente, relacion.productor):
        messages.error(request, 'Sin permiso.')
        return redirect('marketplace:home')

    if request.method == 'POST':
        otro = relacion.productor if request.user == relacion.agente else relacion.agente
        relacion.delete()
        from notificaciones.utils import notificar
        notificar(
            otro,
            'Relación eliminada',
            f'{request.user.get_full_name()} eliminó la relación de trabajo.',
        )
        messages.info(request, 'Relación eliminada.')

    if request.user.es_agente():
        return redirect('agente:dashboard')
    return redirect('productor:dashboard')
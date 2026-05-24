from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from marketplace.models import Producto
from .carrito import Carrito
from .forms import CheckoutForm, ConfirmarEntregaForm, DisputaForm
from .models import Orden, ItemOrden, PagoSimulado, ConfirmacionEntrega
from notificaciones.utils import notificar_nuevo_pedido, notificar_cambio_estado, notificar


# ── CARRITO ───────────────────────────────────────────────────────────────────

def ver_carrito(request):
    carrito = Carrito(request)
    return render(request, 'orders/carrito.html', {'carrito': carrito})


@require_POST
def agregar_al_carrito(request, pk):
    producto = get_object_or_404(Producto, pk=pk, estado='DISPONIBLE')
    carrito  = Carrito(request)
    cantidad = Decimal(request.POST.get('cantidad', '1'))
    carrito.agregar(producto, cantidad)
    messages.success(request, f'"{producto.nombre}" añadido al carrito.')
    return redirect('orders:carrito')


@require_POST
def actualizar_carrito(request, producto_id):
    carrito  = Carrito(request)
    cantidad = Decimal(request.POST.get('cantidad', '1'))
    carrito.actualizar(producto_id, cantidad)
    return redirect('orders:carrito')


@require_POST
def eliminar_del_carrito(request, producto_id):
    Carrito(request).eliminar(producto_id)
    return redirect('orders:carrito')


# ── CHECKOUT Y PAGO ───────────────────────────────────────────────────────────

@login_required
def checkout(request):
    carrito = Carrito(request)
    if not len(carrito):
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('orders:carrito')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # 1. Crear orden
            orden = Orden.objects.create(
                comprador=request.user,
                direccion_entrega=form.cleaned_data['direccion_entrega'],
                notas=form.cleaned_data['notas'],
                estado=Orden.Estado.PENDIENTE_PAGO,
            )
            # 2. Crear items (congelando precio)
            for item in carrito:
                producto = get_object_or_404(Producto, pk=item['producto_id'])
                ItemOrden.objects.create(
                    orden=orden,
                    producto=producto,
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio_unitario'],
                )
            orden.calcular_total()

            # 3. Simular pago — siempre aprobado en MVP
            PagoSimulado.objects.create(
                orden=orden,
                monto=orden.total,
                metodo=form.cleaned_data['metodo_pago'],
                estado=PagoSimulado.Estado.RETENIDO,
            )
            orden.estado = Orden.Estado.PAGADO
            orden.save()

            # 4. Crear registro de confirmación de entrega
            ConfirmacionEntrega.objects.create(orden=orden)

            # 5. Limpiar carrito y notificar
            carrito.limpiar()
            notificar_nuevo_pedido(orden)

            return redirect('orders:pago_exitoso', pk=orden.pk)
    else:
        form = CheckoutForm()

    return render(request, 'orders/checkout.html', {'form': form, 'carrito': carrito})


def pago_exitoso(request, pk):
    orden = get_object_or_404(Orden, pk=pk)
    return render(request, 'orders/pago_exitoso.html', {'orden': orden})


# ── MIS ÓRDENES (COMPRADOR) ───────────────────────────────────────────────────

@login_required
def mis_ordenes(request):
    ordenes = Orden.objects.filter(comprador=request.user).prefetch_related('items__producto')
    return render(request, 'orders/mis_ordenes.html', {'ordenes': ordenes})


@login_required
def detalle_orden(request, pk):
    orden = get_object_or_404(Orden, pk=pk)
    # Solo el comprador, el productor de algún item o un agente pueden ver
    es_comprador  = orden.comprador == request.user
    es_productor  = request.user.es_productor() and orden.items.filter(producto__productor=request.user).exists()
    es_agente     = request.user.es_agente()
    if not (es_comprador or es_productor or es_agente or request.user.is_staff):
        messages.error(request, 'No tienes acceso a esta orden.')
        return redirect('marketplace:home')

    confirmar_form = ConfirmarEntregaForm() if es_comprador and orden.estado == Orden.Estado.ENTREGADO else None
    disputa_form   = DisputaForm() if es_comprador and orden.estado == Orden.Estado.ENTREGADO else None

    return render(request, 'orders/detalle_orden.html', {
        'orden':          orden,
        'confirmar_form': confirmar_form,
        'disputa_form':   disputa_form,
        'es_comprador':   es_comprador,
        'es_productor':   es_productor,
        'es_agente':      es_agente,
    })


# ── ACCIONES DEL PRODUCTOR / AGENTE ──────────────────────────────────────────

def _puede_gestionar(user, orden):
    """True si el usuario puede aceptar/rechazar/despachar esta orden."""
    if user.es_productor():
        return orden.items.filter(producto__productor=user).exists()
    if user.es_agente():
        from agente.models import ProductorAsignado
        productores_ids = ProductorAsignado.objects.filter(agente=user).values_list('productor_id', flat=True)
        return orden.items.filter(producto__productor_id__in=productores_ids).exists()
    return user.is_staff


@login_required
@require_POST
def aceptar_orden(request, pk):
    orden = get_object_or_404(Orden, pk=pk, estado=Orden.Estado.PAGADO)
    if not _puede_gestionar(request.user, orden):
        messages.error(request, 'Sin permiso.')
        return redirect('orders:detalle', pk=pk)
    orden.estado = Orden.Estado.ACEPTADO
    orden.save()
    notificar_cambio_estado(orden)
    messages.success(request, f'Orden #{orden.codigo} aceptada.')
    return redirect('orders:detalle', pk=pk)


@login_required
@require_POST
def rechazar_orden(request, pk):
    orden = get_object_or_404(Orden, pk=pk, estado=Orden.Estado.PAGADO)
    if not _puede_gestionar(request.user, orden):
        messages.error(request, 'Sin permiso.')
        return redirect('orders:detalle', pk=pk)
    orden.estado = Orden.Estado.RECHAZADO
    orden.save()
    # Devolver pago
    if hasattr(orden, 'pago'):
        orden.pago.estado = PagoSimulado.Estado.DEVUELTO
        orden.pago.save()
    notificar_cambio_estado(orden)
    messages.warning(request, f'Orden #{orden.codigo} rechazada. El pago será devuelto.')
    return redirect('orders:detalle', pk=pk)


@login_required
@require_POST
def marcar_en_camino(request, pk):
    orden = get_object_or_404(Orden, pk=pk, estado=Orden.Estado.ACEPTADO)
    if not _puede_gestionar(request.user, orden):
        messages.error(request, 'Sin permiso.')
        return redirect('orders:detalle', pk=pk)
    orden.estado = Orden.Estado.EN_CAMINO
    orden.save()
    notificar_cambio_estado(orden)
    messages.success(request, f'Orden #{orden.codigo} marcada como en camino.')
    return redirect('orders:detalle', pk=pk)


@login_required
@require_POST
def confirmar_entrega_agente(request, pk):
    """El agente sube foto y marca entregado."""
    orden = get_object_or_404(Orden, pk=pk, estado=Orden.Estado.EN_CAMINO)
    if not _puede_gestionar(request.user, orden):
        messages.error(request, 'Sin permiso.')
        return redirect('orders:detalle', pk=pk)

    confirmacion = orden.confirmacion
    foto = request.FILES.get('foto_evidencia')
    if foto:
        confirmacion.foto_evidencia = foto
    confirmacion.confirmado_por_agente = True
    confirmacion.notas_entrega = request.POST.get('notas_entrega', '')
    confirmacion.save()

    orden.estado = Orden.Estado.ENTREGADO
    orden.save()
    notificar_cambio_estado(orden)
    messages.success(request, 'Entrega registrada. Esperando confirmación del comprador.')
    return redirect('orders:detalle', pk=pk)


@login_required
@require_POST
def confirmar_recepcion_comprador(request, pk):
    orden = get_object_or_404(Orden, pk=pk, estado=Orden.Estado.ENTREGADO)
    if orden.comprador != request.user:
        messages.error(request, 'Sin permiso.')
        return redirect('orders:detalle', pk=pk)

    form = ConfirmarEntregaForm(request.POST)
    if form.is_valid():
        confirmacion = orden.confirmacion
        confirmacion.confirmado_por_comprador = True
        confirmacion.fecha_confirmacion = timezone.now()
        confirmacion.save()

        orden.estado = Orden.Estado.CONFIRMADO
        orden.save()

        # Liberar pago
        if hasattr(orden, 'pago'):
            orden.pago.estado = PagoSimulado.Estado.LIBERADO
            orden.pago.save()

        orden.estado = Orden.Estado.FINALIZADO
        orden.save()

        notificar_cambio_estado(orden)

        # Notificar al productor que recibió su pago
        productores = set(i.producto.productor for i in orden.items.select_related('producto__productor'))
        for p in productores:
            notificar(p, f'Pago liberado — Orden #{orden.codigo}',
                      f'El comprador confirmó la entrega. Tu pago de S/ {orden.pago.monto} fue liberado.',
                      f'/orders/detalle/{orden.pk}/')

        messages.success(request, 'Recepción confirmada. ¡Gracias por tu compra!')
    return redirect('orders:detalle', pk=pk)


@login_required
@require_POST
def abrir_disputa(request, pk):
    orden = get_object_or_404(Orden, pk=pk, estado=Orden.Estado.ENTREGADO)
    if orden.comprador != request.user:
        messages.error(request, 'Sin permiso.')
        return redirect('orders:detalle', pk=pk)

    form = DisputaForm(request.POST)
    if form.is_valid():
        orden.estado = Orden.Estado.DISPUTADO
        orden.save()
        # Notificar a admin, productor y agente
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admins = list(User.objects.filter(is_staff=True))
        productores = list(set(i.producto.productor for i in orden.items.select_related('producto__productor')))
        notificar(
            admins + productores,
            f'Disputa abierta — Orden #{orden.codigo}',
            f'Motivo: {form.cleaned_data["motivo"]}. {form.cleaned_data["descripcion"]}',
            f'/orders/detalle/{orden.pk}/'
        )
        messages.warning(request, 'Disputa registrada. El equipo revisará tu caso.')
    return redirect('orders:detalle', pk=pk)
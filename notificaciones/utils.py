from .models import Notificacion


def notificar(destinatarios, titulo, mensaje, url=''):
    """
    destinatarios puede ser un usuario o una lista de usuarios.
    """
    if not isinstance(destinatarios, (list, tuple)):
        destinatarios = [destinatarios]
    notifs = [
        Notificacion(
            destinatario=u,
            titulo=titulo,
            mensaje=mensaje,
            url_accion=url,
        )
        for u in destinatarios if u is not None
    ]
    Notificacion.objects.bulk_create(notifs)


def notificar_nuevo_pedido(orden):
    from agente.models import ProductorAsignado
    # Notificar a cada productor involucrado
    productores = set()
    agentes = set()
    for item in orden.items.select_related('producto__productor'):
        prod = item.producto.productor
        productores.add(prod)
        # Buscar agente asignado a ese productor
        asign = ProductorAsignado.objects.filter(productor=prod).select_related('agente').first()
        if asign:
            agentes.add(asign.agente)

    url = f'/orders/detalle/{orden.pk}/'
    for p in productores:
        notificar(p, f'Nuevo pedido #{orden.codigo}',
                  f'{orden.comprador.get_full_name()} solicitó productos por S/ {orden.total}', url)
    for a in agentes:
        notificar(a, f'Pedido #{orden.codigo} en tu zona',
                  f'Hay un pedido nuevo que involucra a tus productores.', url)


def notificar_cambio_estado(orden):
    url = f'/orders/detalle/{orden.pk}/'
    estado = orden.get_estado_display()
    msgs = {
        'ACEPTADO':   ('Tu pedido fue aceptado', f'El productor aceptó tu pedido #{orden.codigo}.'),
        'RECHAZADO':  ('Tu pedido fue rechazado', f'El pedido #{orden.codigo} fue rechazado. El pago será devuelto.'),
        'EN_CAMINO':  ('Tu pedido está en camino', f'El pedido #{orden.codigo} ya fue despachado.'),
        'ENTREGADO':  ('Confirma tu entrega', f'El pedido #{orden.codigo} fue marcado como entregado. Por favor confírmalo.'),
        'FINALIZADO': ('Pedido finalizado', f'El pago de tu pedido #{orden.codigo} ha sido liberado. ¡Gracias!'),
    }
    titulo, mensaje = msgs.get(orden.estado, (f'Estado actualizado: {estado}', f'Tu pedido #{orden.codigo} cambió a {estado}.'))
    notificar(orden.comprador, titulo, mensaje, url)
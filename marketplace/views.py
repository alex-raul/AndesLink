from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Producto, Categoria
from django.db.models import Avg
from orders.models import Calificacion
from django.db import models

def home(request):
    categorias = Categoria.objects.all()
    productos  = Producto.objects.filter(estado='DISPONIBLE').select_related('productor', 'categoria')

    q = request.GET.get('q', '').strip()
    if q:
        productos = productos.filter(
            Q(nombre__icontains=q) |
            Q(descripcion__icontains=q) |
            Q(departamento__icontains=q)
        )

    cat_id = request.GET.get('categoria')
    categoria_activa = None
    if cat_id:
        categoria_activa = get_object_or_404(Categoria, pk=cat_id)
        productos = productos.filter(categoria=categoria_activa)

    depto = request.GET.get('departamento', '').strip()
    if depto:
        productos = productos.filter(departamento__icontains=depto)

    departamentos = (
        Producto.objects
        .filter(estado='DISPONIBLE')
        .values_list('departamento', flat=True)
        .distinct()
        .order_by('departamento')
    )

    return render(request, 'marketplace/home.html', {
        'productos':        productos,
        'categorias':       categorias,
        'categoria_activa': categoria_activa,
        'q':                q,
        'departamentos':    departamentos,
        'depto_activo':     depto,
    })


def detalle_producto(request, pk):
    producto = get_object_or_404(
        Producto.objects.select_related('productor', 'categoria'),
        pk=pk
    )
    otros = Producto.objects.filter(
        productor=producto.productor,
        estado='DISPONIBLE'
    ).exclude(pk=pk)[:4]

    # Promedio de estrellas del productor
    stats_productor = Calificacion.objects.filter(
        evaluado=producto.productor
    ).aggregate(
        promedio=Avg('estrellas'),
        total=models.Count('id')
    )

    return render(request, 'marketplace/detalle.html', {
        'producto':         producto,
        'otros':            otros,
        'promedio':         stats_productor['promedio'],
        'total_resenas':    stats_productor['total'],
    })

from django.http import JsonResponse

def productos_geojson(request):
    """Devuelve todos los productos con coordenadas en formato JSON para Leaflet."""
    productos = Producto.objects.filter(
        estado='DISPONIBLE',
        latitud__isnull=False,
        longitud__isnull=False,
    ).select_related('productor', 'categoria')

    # Filtro por categoría (opcional, desde el mapa)
    cat_id = request.GET.get('categoria')
    if cat_id:
        productos = productos.filter(categoria_id=cat_id)

    data = []
    for p in productos:
        data.append({
            'id':         p.pk,
            'nombre':     p.nombre,
            'precio':     str(p.precio_unitario),
            'unidad':     p.get_unidad_display(),
            'cantidad':   str(p.cantidad),
            'categoria':  p.categoria.nombre if p.categoria else 'Sin categoría',
            'categoria_id': p.categoria_id,
            'icono':      p.categoria.icono if p.categoria else '🌿',
            'departamento': p.departamento,
            'provincia':  p.provincia,
            'productor':  p.productor.get_full_name(),
            'productor_id': p.productor_id,
            'imagen':     p.imagen.url if p.imagen else None,
            'lat':        float(p.latitud),
            'lng':        float(p.longitud),
            'url':        f'/producto/{p.pk}/',
        })

    return JsonResponse({'productos': data})
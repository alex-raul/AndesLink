from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Producto, Categoria


def home(request):
    categorias = Categoria.objects.all()
    productos = Producto.objects.filter(estado='DISPONIBLE').select_related('productor', 'categoria')

    # Búsqueda
    q = request.GET.get('q', '').strip()
    if q:
        productos = productos.filter(
            Q(nombre__icontains=q) |
            Q(descripcion__icontains=q) |
            Q(departamento__icontains=q)
        )

    # Filtro por categoría
    cat_id = request.GET.get('categoria')
    categoria_activa = None
    if cat_id:
        categoria_activa = get_object_or_404(Categoria, pk=cat_id)
        productos = productos.filter(categoria=categoria_activa)

    # Filtro por departamento
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
        'productos': productos,
        'categorias': categorias,
        'categoria_activa': categoria_activa,
        'q': q,
        'departamentos': departamentos,
        'depto_activo': depto,
    })


def detalle_producto(request, pk):
    producto = get_object_or_404(
        Producto.objects.select_related('productor', 'categoria'),
        pk=pk,
        estado='DISPONIBLE'
    )
    return render(request, 'marketplace/detalle.html', {'producto': producto})
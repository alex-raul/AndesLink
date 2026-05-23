from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from marketplace.models import Producto
from .forms import ProductoForm


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
from django.urls import path
from . import views

app_name = 'productor'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('agregar/', views.agregar_producto, name='agregar'),
    path('editar/<int:pk>/', views.editar_producto, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_producto, name='eliminar'),
]
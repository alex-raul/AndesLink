from django.urls import path
from . import views

app_name = 'agente'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('productores/', views.lista_productores, name='lista_productores'),
    path('productores/asignar/<int:productor_id>/', views.asignar_productor, name='asignar'),
    path('solicitudes/', views.solicitudes_zona, name='solicitudes'),
]
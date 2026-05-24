from django.urls import path
from . import views

app_name = 'agente'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('buscar/',                             views.buscar_productores,  name='buscar'),
    path('productores/', views.lista_productores, name='lista_productores'),
    path('productores/asignar/<int:productor_id>/', views.asignar_productor, name='asignar'),
    path('solicitudes/', views.solicitudes_zona, name='solicitudes'),
    path('solicitud/enviar/<int:productor_id>/',views.enviar_solicitud,    name='enviar_solicitud'),
    path('solicitud/aceptar/<int:solicitud_id>/',views.aceptar_solicitud, name='aceptar_solicitud'),
    path('solicitud/rechazar/<int:solicitud_id>/',views.rechazar_solicitud,name='rechazar_solicitud'),
    path('relacion/eliminar/<int:relacion_id>/', views.eliminar_relacion,  name='eliminar_relacion'),
]
from django.urls import path
from . import views
from agente import views as agente_views
app_name = 'productor'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('agregar/', views.agregar_producto, name='agregar'),
    path('editar/<int:pk>/', views.editar_producto, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_producto, name='eliminar'),
    path('solicitudes/',                                  views.mis_solicitudes,               name='solicitudes'),
    path('buscar-agentes/',                           views.buscar_agentes,               name='buscar_agentes'),
    path('solicitud/enviar/<int:agente_id>/',         views.enviar_solicitud_a_agente,    name='enviar_solicitud_agente'),
    path('solicitud/aceptar/<int:solicitud_id>/',     agente_views.aceptar_solicitud,     name='aceptar_solicitud'),
    path('solicitud/rechazar/<int:solicitud_id>/',    agente_views.rechazar_solicitud,    name='rechazar_solicitud'),
    path('relacion/eliminar/<int:relacion_id>/',      agente_views.eliminar_relacion,     name='eliminar_relacion'),
]
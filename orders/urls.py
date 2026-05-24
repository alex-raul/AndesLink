from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('carrito/',                              views.ver_carrito,                  name='carrito'),
    path('carrito/agregar/<int:pk>/',             views.agregar_al_carrito,           name='agregar'),
    path('carrito/actualizar/<int:producto_id>/', views.actualizar_carrito,           name='actualizar'),
    path('carrito/eliminar/<int:producto_id>/',   views.eliminar_del_carrito,         name='eliminar'),
    path('checkout/',                             views.checkout,                     name='checkout'),
    path('pago-exitoso/<int:pk>/',                views.pago_exitoso,                 name='pago_exitoso'),
    path('mis-ordenes/',                          views.mis_ordenes,                  name='mis_ordenes'),
    path('detalle/<int:pk>/',                     views.detalle_orden,                name='detalle'),
    path('detalle/<int:pk>/aceptar/',             views.aceptar_orden,                name='aceptar'),
    path('detalle/<int:pk>/rechazar/',            views.rechazar_orden,               name='rechazar'),
    path('detalle/<int:pk>/en-camino/',           views.marcar_en_camino,             name='en_camino'),
    path('detalle/<int:pk>/entregar/',            views.confirmar_entrega_agente,     name='entregar'),
    path('detalle/<int:pk>/confirmar/',           views.confirmar_recepcion_comprador,name='confirmar'),
    path('detalle/<int:pk>/disputa/',             views.abrir_disputa,                name='disputa'),
    path('detalle/<int:pk>/calificar/', views.calificar_orden, name='calificar'),
]
from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.home, name='home'),
    path('producto/<int:pk>/', views.detalle_producto, name='detalle'),
    path('api/productos-mapa/', views.productos_geojson, name='productos_mapa_json'),
]
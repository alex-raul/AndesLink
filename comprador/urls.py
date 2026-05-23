from django.urls import path
from . import views

app_name = 'comprador'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('contactar/<int:pk>/', views.enviar_solicitud, name='contactar'),
]
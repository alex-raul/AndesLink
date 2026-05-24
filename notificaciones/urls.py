# notificaciones/urls.py
from django.urls import path
from . import views

app_name = 'notificaciones'

urlpatterns = [
    path('',        views.mis_notificaciones, name='lista'),
    path('count/',  views.conteo_no_leidas,   name='count'),
]
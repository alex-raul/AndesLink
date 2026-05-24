from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('registro/',                   views.RegistroView.as_view(),        name='registro'),
    path('login/',                      views.LoginAndesView.as_view(),       name='login'),
    path('logout/',                     views.logout_view,                    name='logout'),
    path('perfil/',                     views.perfil,                         name='perfil'),
    path('perfil/editar/',              views.editar_perfil,                  name='editar_perfil'),
    path('productor/<int:pk>/',         views.perfil_productor_publico,       name='perfil_productor'),
]
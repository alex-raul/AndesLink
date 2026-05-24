# notificaciones/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from .models import Notificacion


@login_required
def mis_notificaciones(request):
    notifs = Notificacion.objects.filter(destinatario=request.user)
    notifs.filter(leida=False).update(leida=True)
    return render(request, 'notificaciones/lista.html', {'notificaciones': notifs})


@login_required
def conteo_no_leidas(request):
    n = Notificacion.objects.filter(destinatario=request.user, leida=False).count()
    return JsonResponse({'count': n})
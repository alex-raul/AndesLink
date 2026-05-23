from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RegistroForm
from .models import Usuario


class RegistroView(CreateView):
    model = Usuario
    form_class = RegistroForm
    template_name = 'accounts/registro.html'
    success_url = reverse_lazy('marketplace:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class LoginAndesView(LoginView):
    template_name = 'accounts/login.html'


def logout_view(request):
    logout(request)
    return redirect('marketplace:home')
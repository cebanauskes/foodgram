from django.shortcuts import render
from django.views.generic import CreateView

from .forms import CreationForm

class SignUp(CreateView):
    form_class = CreationForm
    success_url = '/auth/login'
    template_name = 'reg.html'
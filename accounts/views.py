from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from .forms import UserCreationForm


class UserCreateView(generic.CreateView):
    model = settings.AUTH_USER_MODEL
    form_class = UserCreationForm
    template_name = 'accounts/user_create_form.html'

    def get_success_url(self):
        return reverse('accounts:login')

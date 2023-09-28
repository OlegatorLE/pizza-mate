from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from pizza.forms import CustomUserCreationForm
from pizza.models import Pizza, CustomUser


class PizzaListView(generic.ListView):
    model = Pizza
    template_name = "pizza/index.html"


class CustomUserCreateView(generic.CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")

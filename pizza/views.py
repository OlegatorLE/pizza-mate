from django.shortcuts import render
from django.views import generic

from pizza.models import Pizza


class PizzaListView(generic.ListView):
    model = Pizza
    template_name = "pizza/index.html"



from django.urls import path

from pizza.views import PizzaListView

urlpatterns = [
    path("", PizzaListView.as_view(), name="home-page"),
]

app_name = "pizza"

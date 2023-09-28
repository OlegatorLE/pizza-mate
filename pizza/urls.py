from django.urls import path

from pizza.views import PizzaListView, CustomUserCreateView

urlpatterns = [
    path("", PizzaListView.as_view(), name="home-page"),
    path("users/create/", CustomUserCreateView.as_view(), name="customuser-create"),
]

app_name = "pizza"

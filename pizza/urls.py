from django.urls import path

from pizza.views import (
    PizzaListView,
    CustomUserCreateView,
    PizzaDetailView,
    show_updated_pizza,
)

urlpatterns = [
    path("", PizzaListView.as_view(), name="home-page"),
    path("users/create/", CustomUserCreateView.as_view(), name="customuser-create"),
    path("detail/<int:pk>/", PizzaDetailView.as_view(), name="pizza-detail"),
    path('pizza/<int:pk>/update_ingredients/',
         show_updated_pizza, name='update-pizza-ingredients'),
]

app_name = "pizza"

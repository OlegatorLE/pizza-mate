from django.urls import path

from pizza.views import HomePageView

urlpatterns = [
    path("", HomePageView.as_view(), name="home-page"),
]

app_name = "pizza"

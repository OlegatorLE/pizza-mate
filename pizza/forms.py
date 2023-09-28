from django import forms
from django.contrib.auth.forms import UserCreationForm

from pizza.models import Ingredient, Pizza, CustomUser


class PizzaForm(forms.ModelForm):
    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-columns'})
    )

    class Meta:
        model = Pizza
        fields = "__all__"


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "address",
            "phone",
        )

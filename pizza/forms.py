from django import forms
from django.contrib.auth.forms import UserCreationForm

from pizza.models import Ingredient, Pizza, CustomUser, IngredientType


class PizzaForm(forms.ModelForm):
    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "checkbox-columns"}
        ),
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


class ProfileCustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "address", "phone"]


class CustomPizzaCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        super(CustomPizzaCreateForm, self).__init__(*args, **kwargs)
        for ingredient_type in IngredientType.objects.all():
            self.fields[
                "ingredient_type.name"
            ] = forms.ModelMultipleChoiceField(
                queryset=Ingredient.objects.filter(
                    ingredient_type=ingredient_type
                ),
                widget=forms.CheckboxSelectMultiple(
                    attrs={"class": "checkbox-columns"}
                ),
                label=ingredient_type.name,
                required=False,
            )

    class Meta:
        model = Pizza
        fields = ["name", "description"]

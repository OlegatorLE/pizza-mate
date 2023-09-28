from django import forms

from pizza.models import Ingredient, Pizza


class PizzaForm(forms.ModelForm):
    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-columns'})
    )

    class Meta:
        model = Pizza
        fields = "__all__"

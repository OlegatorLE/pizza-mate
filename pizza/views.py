from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from pizza.forms import CustomUserCreationForm
from pizza.models import Pizza, CustomUser, Ingredient


class PizzaListView(generic.ListView):
    model = Pizza
    template_name = "pizza/index.html"


class CustomUserCreateView(generic.CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")


class PizzaDetailView(generic.DetailView):
    model = Pizza

    def post(self, request, *args, **kwargs):
        size = request.POST.get('size', 'small')
        self.object = self.get_object()
        context = self.get_context_data(object=self.object, size=size)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['size'] = kwargs.get('size', 'small')
        all_ingredients = Ingredient.objects.all()
        half_length = len(all_ingredients) // 2
        context['left_ingredients'] = all_ingredients[:half_length]
        context['right_ingredients'] = all_ingredients[half_length:]
        return context


def show_updated_pizza(request, *args, **kwargs):
    pizza = get_object_or_404(Pizza, id=kwargs["pk"])

    selected_ingredients = request.POST.getlist("ingredients")
    ingredient_quantities = {}
    for ingredient_id in selected_ingredients:
        qty_key = f"ingredient_qty_{ingredient_id}"
        ingredient_quantities[ingredient_id] = request.POST.get(qty_key, 1)

    updated_ingredients = []
    for ingredient_id, quantity in ingredient_quantities.items():
        ingredient = get_object_or_404(Ingredient, id=ingredient_id)
        updated_ingredients.append({
            "ingredient": ingredient,
            "quantity": quantity,
        })

    pizza_size = request.POST.get("size")

    context = {
        "pizza": pizza,
        "updated_ingredients": updated_ingredients,
        "pizza_size": pizza_size,
    }

    return render(request, 'pizza/update_pizza_detail.html', context)
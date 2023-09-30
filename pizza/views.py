from copy import copy

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from pizza.forms import CustomUserCreationForm
from pizza.models import Pizza, CustomUser, Ingredient, IngredientType, Order, \
    OrderPizza


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
        pizza = get_object_or_404(Pizza, id=kwargs["pk"])
        pizza_prices = pizza.get_prices()
        print(pizza_prices)
        context = self.get_context_data(object=self.object, size=size, pizza_prices=pizza_prices)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['size'] = kwargs.get('size', 'small')
        context["pizza_price"] = kwargs.get("pizza_prices")
        ingredient_types = IngredientType.objects.all().prefetch_related(
            'ingredients'
        )

        for ingredient_type in ingredient_types:
            context_key = ingredient_type.name.lower().replace(" ", "_")
            context[context_key] = ingredient_type.ingredients.all()

        return context


def show_updated_pizza(request, *args, **kwargs):
    pizza = get_object_or_404(Pizza, id=kwargs["pk"])
    pizza_prices = pizza.get_prices()

    base_ingredients_quantity = len([ing.name for ing in pizza.ingredients.all()])

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

    updated_ingredients_quantity = sum(
        int(ingredient["quantity"]) for ingredient in updated_ingredients
    )

    copy_pizza_prices = copy(pizza_prices)
    price_difference = updated_ingredients_quantity - base_ingredients_quantity
    if price_difference != 0:
        for key, pizza_price in copy_pizza_prices.items():
            pizza_price += price_difference * 10
            pizza_prices[key] = pizza_price

    context = {
        "pizza": pizza,
        "updated_ingredients": updated_ingredients,
        "pizza_size": pizza_size,
        "pizza_prices": pizza_prices,
    }

    return render(request, 'pizza/update_pizza_detail.html', context)


class OrderPizzaView(LoginRequiredMixin, generic.DetailView):
    model = Pizza
    template_name = "pizza/order_pizza.html"

    def post(self, request, *args, **kwargs):
        pizza = self.get_object()
        pizza_price = self.request.POST.get("pizza_price")
        request.session["pizza_price"] = pizza_price
        return redirect("pizza:order-pizza", pk=pizza.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pizza_price"] = self.request.session.get("pizza_price")
        return context


class OrderConfirmationView(LoginRequiredMixin, generic.View):
    model = Order
    template_name = "pizza/order_confirmation.html"

    def post(self, request, *args, **kwargs):
        pizza_id = request.POST.get("pizza")
        pizza = get_object_or_404(Pizza, id=pizza_id)

        quantity = int(request.POST.get("quantity"))
        pizza_price = float(request.POST.get("pizza_price"))

        print(pizza, quantity, pizza_price)
        order = Order.objects.create(
            customer=request.user,
            total_price=pizza_price * quantity
        )
        OrderPizza.objects.create(
            order=order,
            pizza=pizza,
            quantity=quantity
        )

        return redirect("pizza:home-page")


class UserOrdersView(LoginRequiredMixin, generic.ListView):
    model = Order
    template_name = 'pizza/user_orders.html'

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)
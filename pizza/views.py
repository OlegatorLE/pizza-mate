from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractUser
from django.db import transaction
from django.db.models import Q, QuerySet
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from pizza.forms import (
    CustomUserCreationForm,
    ProfileCustomUserForm,
    CustomPizzaCreateForm,
)
from pizza.models import (
    Pizza,
    CustomUser,
    Ingredient,
    IngredientType,
    Order,
    OrderPizza,
)


class PizzaListView(generic.ListView):
    model = Pizza
    template_name = "pizza/index.html"

    def get_queryset(self) -> QuerySet["Pizza"]:
        user = self.request.user
        if user.is_authenticated:
            queryset = Pizza.objects.filter(
                Q(user=user) | Q(user__isnull=True)
            ).select_related("user")
        else:
            queryset = Pizza.objects.filter(user__isnull=True)
        return queryset


class CustomUserCreateView(generic.CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")


class PizzaDetailView(generic.DetailView):
    model = Pizza

    def post(self, request, *args, **kwargs) -> HttpResponse:
        size = request.POST.get("size", "small")
        self.object = self.get_object()
        pizza = get_object_or_404(Pizza, id=kwargs["pk"])
        pizza_prices = pizza.get_prices()
        context = self.get_context_data(
            object=self.object, size=size, pizza_prices=pizza_prices
        )
        return self.render_to_response(context)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["size"] = kwargs.get("size", "small")
        context["pizza_price"] = kwargs.get("pizza_prices")
        ingredient_types = IngredientType.objects.all().prefetch_related(
            "ingredients"
        )

        context.update(
            {
                ingredient_type.name.lower().replace(
                    " ", "_"
                ): ingredient_type.ingredients.all()
                for ingredient_type in ingredient_types
            }
        )

        return context


def show_updated_pizza(request, *args, **kwargs) -> HttpResponse:
    pizza = get_object_or_404(
        Pizza.objects.prefetch_related("ingredients"), id=kwargs["pk"]
    )
    pizza_prices = pizza.get_prices()

    base_ingredients_quantity = pizza.ingredients.values_list(
        "name", flat=True
    ).count()

    selected_ingredients = request.POST.getlist("ingredients")
    ingredient_quantities = {}
    for ingredient_id in selected_ingredients:
        qty_key = f"ingredient_qty_{ingredient_id}"
        ingredient_quantities[ingredient_id] = request.POST.get(qty_key, 1)

    ingredients = Ingredient.objects.filter(
        id__in=ingredient_quantities.keys()
    )
    ingredient_quantity_dict = {
        str(ing.id): ingredient_quantities[str(ing.id)] for ing in ingredients
    }
    updated_ingredients = [
        {
            "ingredient": ingredient,
            "quantity": ingredient_quantity_dict[str(ingredient.id)],
        }
        for ingredient in ingredients
    ]

    pizza_size = request.POST.get("size")

    updated_ingredients_quantity = sum(
        int(ingredient["quantity"]) for ingredient in updated_ingredients
    )

    price_difference = updated_ingredients_quantity - base_ingredients_quantity
    if price_difference != 0:
        for key in pizza_prices:
            pizza_prices[key] += price_difference * 10

    context = {
        "pizza": pizza,
        "updated_ingredients": updated_ingredients,
        "pizza_size": pizza_size,
        "pizza_prices": pizza_prices,
    }

    return render(request, "pizza/update_pizza_detail.html", context)


class OrderPizzaView(LoginRequiredMixin, generic.DetailView):
    model = Pizza
    template_name = "pizza/order_pizza.html"

    def post(self, request, *args, **kwargs) -> HttpResponse:
        pizza = self.get_object()
        pizza_price = self.request.POST.get("pizza_price")
        request.session["pizza_price"] = pizza_price
        return redirect("pizza:order-pizza", pk=pizza.id)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["pizza_price"] = self.request.session.get("pizza_price")
        return context


class OrderConfirmationView(LoginRequiredMixin, generic.View):
    model = Order

    def post(self, request, *args, **kwargs) -> HttpResponse:
        pizza_id = request.POST.get("pizza")
        pizza = get_object_or_404(Pizza, id=pizza_id)

        quantity = int(request.POST.get("quantity"))
        pizza_price = float(request.POST.get("pizza_price"))

        with transaction.atomic():
            order = Order.objects.create(
                customer=request.user, total_price=pizza_price * quantity
            )
            OrderPizza.objects.create(
                order=order, pizza=pizza, quantity=quantity
            )

        return redirect("pizza:user-orders")


class CustomUserOrdersView(LoginRequiredMixin, generic.ListView):
    model = Order
    template_name = "pizza/user_orders.html"

    def get_queryset(self) -> QuerySet["Order"]:
        return Order.objects.filter(customer=self.request.user)


class ProfileCustomUserView(LoginRequiredMixin, generic.UpdateView):
    model = CustomUser
    form_class = ProfileCustomUserForm
    template_name = "pizza/profile.html"
    success_url = reverse_lazy("pizza:profile")

    def get_object(self, queryset=None) -> AbstractUser:
        return self.request.user


class CustomPizzaCreateView(LoginRequiredMixin, generic.CreateView):
    model = Pizza
    template_name = "pizza/custom_pizza.html"
    form_class = CustomPizzaCreateForm

    def form_valid(self, form) -> HttpResponse:
        ingredient_ids = self.request.POST.getlist("ingredients")
        pizza = form.save(commit=False)
        pizza.user = self.request.user
        pizza.base_price = 158 + (len(ingredient_ids) * 10)
        pizza.save()
        pizza.ingredients.set(ingredient_ids)

        return redirect("pizza:home-page")

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["ingredient_types"] = IngredientType.objects.all()
        return context

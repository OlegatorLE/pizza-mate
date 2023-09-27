from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.username


class Pizza(models.Model):
    name = models.CharField(max_length=63)
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(upload_to='pizzas/')
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=63)
    description = models.TextField()

    def __str__(self) -> str:
        return self.name


class PizzaIngredient(models.Model):
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        unique_together = ('pizza', 'ingredient')

    def __str__(self) -> str:
        return f"{self.ingredient.name} in {self.pizza.name}"


class Order(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=7, decimal_places=2)
    pizzas = models.ManyToManyField(Pizza, through='OrderPizza')

    def __str__(self) -> str:
        return f"Order {self.id} by {self.customer.username}"


class OrderPizza(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.quantity} of {self.pizza.name} in order {self.order.id}"

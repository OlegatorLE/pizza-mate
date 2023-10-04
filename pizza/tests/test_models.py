from django.test import TestCase, override_settings
from pizza.models import CustomUser, PizzaSize, IngredientType, Ingredient, \
    Pizza, Order, OrderPizza


class ModelsTest(TestCase):
    def setUp(self) -> None:
        self.user = CustomUser.objects.create_user(
            username="test_user",
            password="password12345",
            phone="0123456789",
            address="Test Address",
        )

        self.small_size = PizzaSize.objects.create(
            name="Small", weight=300, multiplier=1.0
        )
        self.medium_size = PizzaSize.objects.create(
            name="Medium", weight=500, multiplier=1.5
        )
        self.big_size = PizzaSize.objects.create(
            name="Big", weight=700, multiplier=2.0
        )

        self.pizza_name = "Test_Pizza"

        self.pizza = Pizza.objects.create(
            name=self.pizza_name,
            description='Test description',
            base_price=100,
            size=self.small_size,
            image="pizzas/default_pizza.jpg"
        )

        self.order = Order.objects.create(
            customer=self.user,
            total_price=100,
        )

        self.order_pizza = OrderPizza.objects.create(
            order=self.order,
            pizza=self.pizza,
            quantity=2
        )

    def test_username_str(self) -> None:
        self.assertEqual(str(self.user), "test_user")

    def test_pizza_name_str(self) -> None:
        self.assertEqual(str(self.pizza), self.pizza_name)

    def test_get_prices(self) -> None:
        expected_prices = {"Small": 100, "Medium": 150, "Big": 200}
        self.assertEqual(self.pizza.get_prices(), expected_prices)

    def test_order_str(self) -> None:
        expected_str = f"Order {self.order.id} by {self.user.username}"
        self.assertEqual(str(self.order), expected_str)

    def test_order_pizza_str(self) -> None:
        expected_str = (
            f"{self.order_pizza.quantity} of {self.pizza.name}"
            f" in order {self.order.id}"
        )
        self.assertEqual(str(self.order_pizza), expected_str)

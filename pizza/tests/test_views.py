from django.test import TestCase
from django.urls import reverse
from pizza.models import Pizza, CustomUser, PizzaSize
from django.db.models import Q

HOME_PAGE_URL = reverse("pizza:home-page")


class PizzaListViewTests(TestCase):
    def setUp(self) -> None:
        self.user = CustomUser.objects.create_user(
            username="test_user",
            password="password12345",
        )

        PizzaSize.objects.create(name="Small", weight=300, multiplier=1.0)
        PizzaSize.objects.create(name="Medium", weight=500, multiplier=1.5)
        PizzaSize.objects.create(name="Big", weight=700, multiplier=2.0)

        Pizza.objects.create(name="Margarita", base_price=100, user=self.user)
        Pizza.objects.create(name="Pepperoni", base_price=100)
        Pizza.objects.create(name="Veggie", base_price=100, user=self.user)

        self.response = self.client.get(HOME_PAGE_URL)

    def test_view_url_exists_at_desired_location(self) -> None:

        self.assertEqual(self.response.status_code, 200)

    def test_view_uses_correct_template(self) -> None:
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "pizza/index.html")

    def test_queryset_for_authenticated_user(self) -> None:
        self.client.login(username="test_user", password="password12345")
        response = self.client.get(HOME_PAGE_URL)
        self.assertQuerysetEqual(
            response.context["object_list"],
            [pizza for pizza in
             Pizza.objects.filter(Q(user=self.user) | Q(user__isnull=True))]
        )

    def test_queryset_for_unauthenticated_user(self) -> None:
        self.assertQuerysetEqual(
            self.response.context["object_list"],
            [pizza for pizza in Pizza.objects.filter(user__isnull=True)]
        )

    def test_queryset_with_search_query(self) -> None:
        response = self.client.get(HOME_PAGE_URL, {"search": "Veggie"})
        self.assertQuerysetEqual(
            response.context["object_list"],
            [Pizza.objects.get(name="Veggie")]
        )


class OrderPizzaViewTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = CustomUser.objects.create_user(
            username="test_user",
            password="test_pass"
        )
        cls.pizza = Pizza.objects.create(name="Margarita", base_price=100)
        PizzaSize.objects.create(name="Small", weight=300, multiplier=1.0)
        PizzaSize.objects.create(name="Medium", weight=500, multiplier=1.5)
        PizzaSize.objects.create(name="Big", weight=700, multiplier=2.0)

    def test_view_requires_login(self) -> None:
        response = self.client.get(
            reverse('pizza:order-pizza', kwargs={'pk': self.pizza.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_post_adds_price_to_session_and_redirects(self) -> None:
        self.client.login(username='test_user', password='test_pass')
        response = self.client.post(
            reverse(
                'pizza:order-pizza',
                kwargs={'pk': self.pizza.pk}),
            data={'pizza_price': '10.50'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse(
            'pizza:order-pizza', kwargs={'pk': self.pizza.pk})
                         )
        self.assertEqual(self.client.session['pizza_price'], '10.50')

    def test_pizza_price_added_to_context_data(self) -> None:
        self.client.login(username='test_user', password='test_pass')
        session = self.client.session
        session['pizza_price'] = '10.50'
        session.save()

        response = self.client.get(
            reverse('pizza:order-pizza', kwargs={'pk': self.pizza.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['pizza_price'], '10.50')

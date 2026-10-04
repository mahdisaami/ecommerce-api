from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from carts.models import Cart, CartItem
from orders.models import Order
from products.models import Product

User = get_user_model()

class CheckoutTests(APITestCase):

    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="testuser@example.com"
        )

        self.product = Product.objects.create(
            name="Test_Product",
            seller=self.user,
            description="A product for testing.",
            price=1000,
            stock=100
        )

        self.cart = Cart.objects.create(user=self.user)


        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )

        self.client.force_authenticate(user=self.user)

    def test_checkout_creates_order(self):
        response = self.client.post('/api/orders/checkout/')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        order = Order.objects.get(
            user=self.user
        )

        item = order.items.first()

        self.assertEqual(
            item.product,
            self.product
        )

        self.assertEqual(
            item.price,
            self.product.price
        )

        self.assertEqual(
            self.cart.items.count(),
            0
        )

    def test_order_keeps_product_price_at_checkout(self):
        # Change the product price after adding to cart

        self.client.post('/api/orders/checkout/')

        order = Order.objects.get(
            user=self.user
        )

        item = order.items.first()

        self.product.price = 1500
        self.product.save()

        self.assertEqual(
            item.price,
            1000
        )

    def test_checkout_with_empty_cart(self):
        # Clear the cart
        self.cart.items.all().delete()

        response = self.client.post('/api/orders/checkout/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            Order.objects.count(),
            0
        )

    def test_checkout_decreases_product_stock(self):
        response = self.client.post(
            "/api/orders/checkout/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            98,
        )

    def test_checkout_fails_when_stock_is_insufficient(self):
        self.product.stock = 1
        self.product.save()

        response = self.client.post(
            "/api/orders/checkout/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            1,
        )

        self.assertEqual(
            Order.objects.count(),
            0,
        )

        self.assertEqual(
            self.cart.items.count(),
            1,
        )

    def test_cancel_order_restores_product_stock(self):

        # First, checkout to create an order
        response = self.client.post('/api/orders/checkout/')

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        order = Order.objects.get(user=self.user)

        self.product.refresh_from_db()
        self.assertEqual(
            self.product.stock,
            98
        )

        # Now, cancel the order
        response = self.client.post(f'/api/orders/{order.id}/cancel/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        order.refresh_from_db()
        self.assertEqual(order.status, "CANCELED")

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 100)  # Stock should be restored

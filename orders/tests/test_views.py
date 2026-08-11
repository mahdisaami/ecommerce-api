from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from orders.models import Order

User = get_user_model()

class OrderDetailPermissionTests(APITestCase):

    def setUp(self):
        # Create two users and an order for user1
        self.user1 = User.objects.create_user(
            username="user1",
            password="testpass123",
            email='user1@gmail.com'
        )

        self.user2 = User.objects.create_user(
            username="user2",
            password="testpass123",
            email='user2@gmail.com'
        )

        self.order = Order.objects.create(
            user=self.user1,
            status="PENDING",
        )

    def test_user_cannot_access_another_users_order(self):
        self.client.force_authenticate(
            user=self.user2
        )

        response = self.client.get(
            f"/api/orders/{self.order.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_user_can_access_own_order(self):
        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.get(
            f"/api/orders/{self.order.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from orders.models import Order


User = get_user_model()


class OrderCancelTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="cancel_user",
            password="testpass123",
            email='teat@gmail.com'
        )

        self.order = Order.objects.create(
            user=self.user,
            status="PENDING",
        )

        self.client.force_authenticate(
            user=self.user
        )

    def test_pending_order_can_be_canceled(self):
        response = self.client.post(
            f"/api/orders/{self.order.id}/cancel/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            "CANCELED",
        )

    def test_completed_order_cannot_be_canceled(self):
        self.order.status = "COMPLETED"
        self.order.save()

        response = self.client.post(
            f"/api/orders/{self.order.id}/cancel/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            "COMPLETED",
        )

    def test_user_cannot_cancel_another_users_order(self):
        another_user = User.objects.create_user(
            username="another_user",
            password="testpass123",
        )

        self.client.force_authenticate(
            user=another_user
        )

        response = self.client.post(
            f"/api/orders/{self.order.id}/cancel/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_unauthenticated_user_cannot_cancel_order(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            f"/api/orders/{self.order.id}/cancel/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
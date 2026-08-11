from django.db import transaction
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from carts.models import Cart
from orders.models import Order, OrderItem
from orders.serializers import OrderSerializer


class CheckoutAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user).first()

        if not cart or not cart.items.exists():
            return Response(
                {"detail": "Your cart is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = Order.objects.create(
            user = request.user,
            status = 'PENDING'
        )

        for cart_item in cart.items.select_related('product'):
            # Create order items based on cart items
            OrderItem.objects.create(
                order = order,
                quantity = cart_item.quantity,
                product = cart_item.product,
                price = cart_item.product.price
            )

        cart.items.all().delete()

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )
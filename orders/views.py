from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.models import Cart
from orders.models import Order, OrderItem
from orders.serializers import OrderSerializer, OrderStatusSerializer


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


class MyOrdersAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product').order_by('-created_at')

class OrderDetailAPIView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')

class OrderStatusUpdateAPIView(UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderStatusSerializer
    permission_classes = (IsAdminUser,)


class OrderPaymentAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk, *args, **kwargs):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {'detail': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if order.status != "PENDING":
            raise ValidationError(
                "Only pending orders can be paid.",
            )

        order.status = 'COMPLETED'
        order.save(update_fields=['status', 'updated_at'])

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_200_OK
        )
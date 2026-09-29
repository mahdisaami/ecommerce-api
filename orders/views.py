from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.models import Cart
from orders.models import Order, OrderItem
from orders.serializers import OrderSerializer, OrderStatusSerializer
from products.models import Product


class CheckoutAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        cart = (
            Cart.objects.select_for_update()
            .filter(user=request.user)
            .first()
        )

        if not cart or not cart.items.exists():
            return Response(
                {"detail": "Your cart is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_items = list(
            cart.items.select_related('product')
        )

        product_ids = [item.product.id for item in cart_items]

        products = (
            Product.objects
            .select_for_update()
            .filter(id__in=product_ids)
        )

        products_by_id = {
            product.id: product
            for product in products
        }

        for cart_item in cart_items:
            product = products_by_id[cart_item.product.id]
            if cart_item.quantity > product.stock:
                raise ValidationError(
                    f"Not enough stock for {product.name}"
                )

        order = Order.objects.create(
            user = request.user,
            status = 'PENDING'
        )

        for cart_item in cart_items:
            product = products_by_id[cart_item.product.id]
            OrderItem.objects.create(
                order = order,
                quantity = cart_item.quantity,
                product = product,
                price = product.price
            )
            product.stock -= cart_item.quantity
            product.save(update_fields=['stock'])

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

class OrderPaymentCancelAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk, *args, **kwargs):
        order = get_object_or_404(
            Order,
            pk=pk,
            user=request.user,
        )

        if order.status != "PENDING":
            raise ValidationError(
                "Only pending orders can be canceled.",
            )

        order.status = 'CANCELED'
        order.save(update_fields=['status', 'updated_at'])

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_200_OK
        )

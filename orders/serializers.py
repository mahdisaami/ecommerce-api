from rest_framework import serializers

from orders.models import OrderItem, Order


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField(read_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'price',
            'quantity',
            'subtotal',
        ]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'status',
            'items',
            'total_price',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ('created_at', 'updated_at', 'status', 'user')

    def get_total_price(self, obj):
        return sum(item.subtotal for item in obj.items.all())

class OrderStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ("status",)
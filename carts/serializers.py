from rest_framework import serializers
from carts.models import CartItem, Cart
from products.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField(read_only=True)
    price = serializers.DecimalField(
        source='product.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields =  [
            'id',
            'product',
            'price',
            'quantity',
            'subtotal'
        ]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()


    class Meta:
        model = Cart
        fields = [
            'id',
            'items',
            'total_price',
            'created_at',
        ]


class AddToCartSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1, default=1)


    def save(self, **kwargs):
        user = self.context['request'].user
        cart, _ = Cart.objects.get_or_create(user=user)
        product = self.validated_data['product']
        quantity = self.validated_data['quantity']

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item


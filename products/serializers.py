from rest_framework import serializers

from products.models import Product, Category


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
            "stock",
            "category",
            "category_id",
        )
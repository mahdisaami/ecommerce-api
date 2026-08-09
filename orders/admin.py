from django.contrib import admin

from orders.models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status','display_items', 'created_at', 'updated_at')

    def display_items(self, obj):
        return ", ".join(
            item.product.name
            for item in obj.items.all()
        )

    display_items.short_description = "Items"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price', 'subtotal')
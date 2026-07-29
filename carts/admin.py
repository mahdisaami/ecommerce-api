from django.contrib import admin

from carts.models import Cart, CartItem

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'cart__user')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'user_groups',
        'created_at',
    )

    def user_groups(self, obj):
        return ", ".join(
            obj.user.groups.values_list(
                "name",
                flat=True
            )
        )

    user_groups.short_description = "Groups"
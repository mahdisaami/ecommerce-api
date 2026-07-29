from django.contrib import admin

from products.models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'slug')

admin.site.register(Product)
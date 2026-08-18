from django.urls import path

from orders.views import OrderPaymentAPIView
from .views import MyCartView, AddToCartView, UpdateCartAPIView, DeleteCartAPIView

urlpatterns = [
    path('me/', MyCartView.as_view(), name='my-cart'),
    path('add-item/', AddToCartView.as_view(), name='add-to-cart'),
    path('items/<int:pk>/', UpdateCartAPIView.as_view(), name='update-cart-item'),
    path('items/<int:pk>/delete/', DeleteCartAPIView.as_view(), name='delete-cart-item'),
]
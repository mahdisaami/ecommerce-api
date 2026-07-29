from django.urls import path
from .views import MyCartView, AddToCartView

urlpatterns = [
    path('me/', MyCartView.as_view(), name='my-cart'),
    path('add-item/', AddToCartView.as_view(), name='add-to-cart'),
]
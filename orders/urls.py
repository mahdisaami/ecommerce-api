from django.urls import path

from orders.views import CheckoutAPIView, MyOrdersAPIView, OrderDetailAPIView, OrderStatusUpdateAPIView, \
    OrderPaymentAPIView

urlpatterns = [
    path('checkout/', CheckoutAPIView.as_view(), name='checkout'),
    path('my-orders/', MyOrdersAPIView.as_view(), name='my-orders'),
    path('<int:pk>/', OrderDetailAPIView.as_view(), name='order-detail'),
    path('<int:pk>/status/', OrderStatusUpdateAPIView.as_view(), name='order-status-update'),
    path('<int:pk>/pay/', OrderPaymentAPIView.as_view(), name='order-payment')

]
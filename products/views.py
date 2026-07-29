from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from products.models import Product
from products.permissions import IsSellerOrReadOnly
from products.serializers import ProductSerializer


class ProductListCreateView(generics.ListCreateAPIView):

    serializer_class = ProductSerializer
    permission_classes = (IsSellerOrReadOnly,)
    queryset = Product.objects.all()

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    filterset_fields = [
        'category',
    ]

    search_fields = [
        'name',
        'description',
    ]

    ordering_fields = [
        'price',
        'created_at',
    ]

    ordering = ('-created_at',)



    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

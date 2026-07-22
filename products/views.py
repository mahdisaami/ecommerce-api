from django.views import generic

from products.models import Product
from products.permissions import IsSellerOrReadOnly
from products.serializers import ProductSerializer


class ProductCreateView(generic.ListCreateView):

    serializer_class = ProductSerializer
    permission_classes = (IsSellerOrReadOnly,)
    queryset = Product.objects.all()



    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

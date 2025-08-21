from rest_framework import serializers
from product.models import Product
from product.serializer import ProductDetailSerializer, ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items']

    def get_total_price(self, obj):
        return sum(items.total_price for item in obj.items.all())
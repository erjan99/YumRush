from rest_framework import serializers
from product.models import Product
from product.serializers import ProductDetailSerializer, ProductListSerializer
from .models import *


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items']

    def get_total_price(self, obj):
        return sum(item.total_price for item in obj.items.all())

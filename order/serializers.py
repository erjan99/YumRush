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
        fields = ['id', 'items', 'total_price']

    def get_total_price(self, obj):
        return sum(item.total_price for item in obj.items.all())


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'created_at', 'status', 'total_price']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'total_price']


class OrderRatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['id', 'rating']

    def validate(self, data):
        if self.intance.status != "delivered":
            raise serializers.ValidationError("Нельзя ставить рейтинг до завершения заказа.")
        return data
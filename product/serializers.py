from rest_framework import serializers
from .models import *


class CategoryListSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'parent']


class ProductListSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    category = CategoryListSerializer()

    class Meta:
        model = Product
        fields = ['name', 'image', 'original_price', 'discounted_price', 'category', 'rating', 'company']


class ProductDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'name', 'original_price', 'discounted_price', 'category', 'rating', 'company', 'description', 'image', 'ingredients']

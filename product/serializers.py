from rest_framework import serializers
from .models import *


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']


class ProductListSerializer(serializers.ModelSerializer):
    category = CategoryListSerializer()

    class Meta:
        model = Product
        fields = ['name', 'image', 'original_price', 'discounted_price', 'category', 'rating', 'company']


class ProductDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'name', 'original_price', 'discounted_price', 'category', 'rating', 'company', 'description', 'image', 'ingredients']
